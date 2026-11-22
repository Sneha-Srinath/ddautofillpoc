"""Resolve each mapped field: precedence, conversion, conflicts, status (FR-19, 5.5)."""
from __future__ import annotations

from typing import Any

from core import convert
from core.catalog import Catalog
from core.config import settings
from core.models import FieldMapping, ResolvedField, TemplateConfig


def _kind(path: str) -> str:
    return "JSON" if path.startswith("json.") else "DB"


def resolve_field(name: str, m: FieldMapping, cat: Catalog,
                  override: Any = None, has_override: bool = False) -> ResolvedField:
    base = dict(name=name, label=m.label or name, type=m.type, options=m.options)
    threshold = settings()["confidence_threshold"]

    if has_override:
        if convert.is_blank(override):
            return ResolvedField(**base, status="Review" if not m.manual else "Manual",
                                 source="User", note="Cleared by user")
        c = convert.convert(override, m.type, m.format, m.options, m.max_length)
        if not c.ok:
            return ResolvedField(**base, status="Review", source="User",
                                 note="User value not usable: " + "; ".join(c.flags))
        return ResolvedField(**base, value=c.value, display=c.display, source="User",
                             source_path="edited in review", status="Review" if c.flags else "Filled",
                             note="; ".join(["Edited by user"] + c.flags))

    if m.manual:
        return ResolvedField(**base, status="Manual", note="Completed by a person (never auto-filled)")
    if not m.sources:
        return ResolvedField(**base, status="Unmapped", note="No field in this company's JSON or database rows matches this form field")

    # Evaluate every source in precedence order
    evaluated = []
    for path in m.sources:
        e = cat.get(path)
        raw = None if e is None else e.value
        conv = convert.convert(raw, m.type, m.format, m.options, m.max_length)
        evaluated.append((path, e, raw, conv))

    usable = [x for x in evaluated if x[3].ok]
    if not usable:
        tried = [x for x in evaluated if not convert.is_blank(x[2])]
        if tried:
            path, e, raw, conv = tried[0]
            return ResolvedField(**base, source=_kind(path), source_path=path,
                                 confidence=e.confidence if e else None, status="Review",
                                 note="; ".join(conv.flags) or f'Value "{raw}" could not be used')
        return ResolvedField(**base, status="Missing",
                             note="No value for this client in: " + ", ".join(m.sources))

    path, e, raw, conv = usable[0]
    notes: list[str] = list(conv.flags)
    # A higher-precedence source had a value we could not interpret -> fell back
    for p2, e2, raw2, conv2 in evaluated:
        if p2 == path:
            break
        if not convert.is_blank(raw2) and not conv2.ok:
            notes.append(f'{_kind(p2)} value "{raw2}" not usable ({"; ".join(conv2.flags)}); '
                         f"used {_kind(path)}")
    # Conflict with a lower-precedence usable source
    for p2, e2, raw2, conv2 in usable[1:]:
        if str(conv2.value) != str(conv.value):
            notes.append(f"Conflict: {_kind(path)} {conv.display!s} vs {_kind(p2)} {conv2.display!s}; "
                         f"{_kind(path)} used by precedence")
    conf = e.confidence if e else None
    if conf is not None and conf < threshold:
        notes.append(f"Low extraction confidence {conf:.2f} (< {threshold:.2f})")
    match = m.match.get("json" if path.startswith("json.") else "db")
    if match and match.method in ("fuzzy", "semantic") and not m.reviewed_by:
        notes.append(f"{match.method} match not yet reviewed by an admin")
    return ResolvedField(**base, value=conv.value, display=conv.display, source=_kind(path),
                         source_path=path + (f"  [{e.source_ref}]" if e and e.source_ref else ""),
                         confidence=conf, status="Review" if notes else "Filled", note="; ".join(notes))


def resolve(cfg: TemplateConfig, cat: Catalog, overrides: dict[str, Any] | None = None) -> list[ResolvedField]:
    overrides = overrides or {}
    return [resolve_field(name, m, cat, overrides.get(name), name in overrides)
            for name, m in cfg.fields.items()]
