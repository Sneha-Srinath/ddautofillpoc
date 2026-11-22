"""Auto-match template fields to JSON paths and DB columns (FR-9 .. FR-14).

Tiers, stopping at the first confident match, run separately for JSON and DB sources:
  1 exact    normalized field name/label == normalized path phrase
  2 synonym  both sides resolve to the same glossary concept
  3 fuzzy    rapidfuzz token-sort similarity >= threshold
  4 semantic Claude, choosing only from real paths (optional, setup only)
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from functools import lru_cache

from rapidfuzz import fuzz

from core import convert
from core.catalog import Catalog
from core.config import glossary, settings
from core.llm import semantic_match
from core.models import DiscoveredField, FieldMapping, SourceEntry, SourceMatch
from core.textnorm import normalize

TYPE_FORMAT = {"checkbox": "yesno", "radio": "text", "dropdown": "text"}


@lru_cache
def alias_index() -> dict[str, str]:
    idx: dict[str, str] = {}
    for concept, spec in (glossary().get("concepts") or {}).items():
        for a in spec.get("aliases", []):
            idx.setdefault(normalize(a), concept)
    return idx


def concept_spec(concept: str | None) -> dict:
    return (glossary().get("concepts") or {}).get(concept or "", {})


def field_phrases(f: DiscoveredField) -> list[str]:
    return list(dict.fromkeys(p for p in (normalize(f.name), normalize(f.label)) if p))


def concept_of_field(f: DiscoveredField) -> str | None:
    idx = alias_index()
    for p in field_phrases(f):
        if p in idx:
            return idx[p]
    return None


def concept_of_entry(e: SourceEntry) -> str | None:
    idx = alias_index()
    for v in sorted(e.variants, key=len, reverse=True):
        if v in idx:
            return idx[v]
    return None


def infer_format(f: DiscoveredField, concept: str | None) -> str:
    if f.type in TYPE_FORMAT:
        return TYPE_FORMAT[f.type]
    spec = concept_spec(concept)
    if spec.get("format"):
        return spec["format"]
    n = normalize(f.name + " " + f.label)
    for pat, fmt in [(r"\bdate\b", "date"), (r"\b(phone|telephone)\b", "phone"),
                     (r"\be ?mail\b", "email"), (r"\bzip\b", "zip"), (r"\bpct\b|\bratio\b", "percent"),
                     (r"\b(premium|revenue|limit|income|surplus|amount)\b", "currency")]:
        if re.search(pat, n):
            return fmt
    return "text"


def compatible(f: DiscoveredField, fmt: str, e: SourceEntry) -> bool:
    """Type compatibility (FR-11). Blank values stay compatible (they become Missing)."""
    v = e.value
    if convert.is_blank(v):
        return True
    is_num = isinstance(v, (int, float)) and not isinstance(v, bool)
    if f.type == "checkbox":
        if convert.to_yesno(v).ok:
            return True
        return not is_num and len(str(v)) <= 80 and not convert.to_date(v).ok
    if f.type in ("radio", "dropdown"):
        return not is_num or bool(convert.to_option(v, f.options).ok)
    if fmt == "date":
        return convert.to_date(v).ok
    if fmt in ("currency", "number", "percent"):
        return convert.parse_amount(str(v).replace("%", "") if not is_num else v)[0] is not None
    if fmt in ("phone", "zip"):
        return len(re.sub(r"\D", "", str(v))) >= 5
    if fmt == "email":
        return "@" in str(v)
    return True


@dataclass
class Proposal:
    field: DiscoveredField
    concept: str | None
    fmt: str
    manual: bool = False
    json: SourceMatch | None = None
    db: SourceMatch | None = None
    sources: list[str] = field(default_factory=list)
    sample: str = ""

    def to_mapping(self) -> FieldMapping:
        return FieldMapping(
            type=self.field.type, label=self.field.label, format=self.fmt, options=self.field.options,
            max_length=self.field.max_length, manual=self.manual, sources=self.sources,
            match={k: m for k, m in (("json", self.json), ("db", self.db)) if m},
            concept=self.concept)

    @property
    def method(self) -> str:
        if self.manual:
            return "rule"
        ms = [m for m in (self.json, self.db) if m]
        if not ms:
            return "-"
        order = ["exact", "synonym", "fuzzy", "semantic", "admin"]
        return min(ms, key=lambda m: order.index(m.method) if m.method in order else 9).method

    @property
    def score(self) -> float:
        ms = [m.score for m in (self.json, self.db) if m]
        return max(ms) if ms else 0.0


def _best(cands: list[tuple[SourceEntry, float]]) -> tuple[SourceEntry, float] | None:
    if not cands:
        return None
    return sorted(cands, key=lambda c: (-c[1], -(c[0].confidence or 1.0), len(c[0].path)))[0]


def match_kind(f: DiscoveredField, fconcept: str | None, fmt: str,
               entries: list[SourceEntry]) -> SourceMatch | None:
    phrases = field_phrases(f)
    entries = [e for e in entries if compatible(f, fmt, e)]
    # Tier 1 - exact
    exact = []
    for e in entries:
        hit = [v for v in e.variants if v in phrases]
        if hit:
            same = 1 if fconcept and concept_of_entry(e) == fconcept else 0
            exact.append((e, same * 100 + max(len(h) for h in hit)))
    if (b := _best(exact)):
        return SourceMatch(path=b[0].path, method="exact", score=1.0)
    # Tier 2 - synonym
    if fconcept:
        syn = [(e, len(max(e.variants, key=len))) for e in entries if concept_of_entry(e) == fconcept]
        if (b := _best(syn)):
            return SourceMatch(path=b[0].path, method="synonym", score=0.95)
    # Tier 3 - fuzzy (skip candidates that clearly mean a different concept)
    threshold = settings()["fuzzy_threshold"]
    fuzzy = []
    for e in entries:
        ec = concept_of_entry(e)
        if fconcept and ec and ec != fconcept:
            continue
        sc = max((fuzz.token_sort_ratio(p, v) for p in phrases for v in e.variants), default=0)
        if sc >= threshold:
            fuzzy.append((e, sc))
    if (b := _best(fuzzy)):
        return SourceMatch(path=b[0].path, method="fuzzy", score=round(b[1] / 100, 2))
    return None


def order_sources(js: SourceMatch | None, dbm: SourceMatch | None) -> list[str]:
    master = set(settings()["master_tables"])
    out = []
    if dbm and dbm.path.split(".")[1].split("[")[0] in master:
        out = [dbm.path] + ([js.path] if js else [])
    else:
        out = ([js.path] if js else []) + ([dbm.path] if dbm else [])
    return out


def auto_match(fields: list[DiscoveredField], catalog: Catalog, use_llm: bool = False) -> list[Proposal]:
    props: list[Proposal] = []
    jentries, dentries = catalog.of_kind("json"), catalog.of_kind("db")
    for f in fields:
        concept = concept_of_field(f)
        fmt = infer_format(f, concept)
        p = Proposal(field=f, concept=concept, fmt=fmt)
        if concept_spec(concept).get("manual"):
            p.manual = True
            props.append(p)
            continue
        p.json = match_kind(f, concept, fmt, jentries)
        p.db = match_kind(f, concept, fmt, dentries)
        p.sources = order_sources(p.json, p.db)
        props.append(p)

    if use_llm:
        todo = [p for p in props if not p.manual and not p.sources]
        if todo:
            res = semantic_match([{"name": p.field.name, "label": p.field.label, "type": p.field.type}
                                  for p in todo], sorted(catalog.entries))
            for p in todo:
                if p.field.name in res:
                    path, conf = res[p.field.name]
                    m = SourceMatch(path=path, method="semantic", score=round(conf, 2))
                    if path.startswith("json."):
                        p.json = m
                    else:
                        p.db = m
                    p.sources = order_sources(p.json, p.db)

    for p in props:
        if p.sources:
            e = catalog.get(p.sources[0])
            p.sample = "" if e is None or e.value is None else str(e.value)
    return props


def mappable_coverage(props: list[Proposal]) -> tuple[int, int]:
    mappable = [p for p in props if not p.manual]
    return sum(1 for p in mappable if p.sources), len(mappable)


def today_str() -> str:
    return date.today().isoformat()
