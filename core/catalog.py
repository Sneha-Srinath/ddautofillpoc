"""Flatten one client's extracted JSON and SQL rows into a searchable list of sources.

JSON paths look like  json.entity.legal_name
DB paths look like    db.client.legal_name
                      db.client_contact[role=Primary].phone
                      db.client_financials[latest].gross_written_premium
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from core import db
from core.config import JSON_DIR, settings
from core.models import ExtractedJson, SourceEntry
from core.textnorm import normalize

META_KEYS = {"client_id", "client_name", "extracted_at", "source_documents"}


class DataError(Exception):
    """Raised when a client's data is missing or belongs to another client."""


@dataclass
class Catalog:
    client_id: str
    client_name: str
    entries: dict[str, SourceEntry] = field(default_factory=dict)
    raw_json: dict = field(default_factory=dict)
    db_rows: dict[str, list[dict]] = field(default_factory=dict)

    def get(self, path: str) -> SourceEntry | None:
        return self.entries.get(path)

    def of_kind(self, kind: str) -> list[SourceEntry]:
        return [e for e in self.entries.values() if e.kind == kind]

    def input_hash(self) -> str:
        blob = json.dumps({"json": self.raw_json, "db": self.db_rows}, sort_keys=True, default=str)
        return hashlib.sha256(blob.encode()).hexdigest()[:16]


# ------------------------------------------------------------------ JSON
def load_json(client_id: str, path=None) -> dict:
    p = path or JSON_DIR / f"{client_id}.json"
    if not p.exists():
        raise DataError(f"No extracted JSON found for client {client_id}.")
    doc = json.loads(p.read_text(encoding="utf-8"))
    validate_json(doc, client_id)
    return doc


def validate_json(doc: dict, expected_client_id: str) -> ExtractedJson:
    try:
        model = ExtractedJson.model_validate(doc)
    except Exception as exc:  # pydantic ValidationError -> clear message
        raise DataError(f"Extracted JSON does not meet the contract: {exc}") from exc
    if model.client_id != expected_client_id:
        raise DataError(
            f"Refused: the extracted JSON belongs to client '{model.client_id}', but this template "
            f"is registered to client '{expected_client_id}'. No data was read.")
    return model


def _is_leaf(node: Any) -> bool:
    return isinstance(node, dict) and "value" in node and set(node) <= {"value", "confidence", "source_ref"}


def _json_variants(parts: list[str]) -> list[str]:
    words = [normalize(p) for p in parts if not p.startswith("[")]
    out = []
    if words:
        out.append(words[-1])
    if len(words) >= 2:
        out.append(f"{words[-2]} {words[-1]}")
    if len(words) >= 3:
        out.append(" ".join(words[-3:]))
    return list(dict.fromkeys(out))


def flatten_json(doc: dict) -> list[SourceEntry]:
    out: list[SourceEntry] = []

    def walk(node, parts):
        if _is_leaf(node):
            out.append(SourceEntry(path="json." + ".".join(parts).replace(".[", "["), kind="json",
                                   value=node.get("value"), confidence=node.get("confidence"),
                                   source_ref=node.get("source_ref"), variants=_json_variants(parts)))
        elif isinstance(node, dict):
            for k, child in node.items():
                if not parts and k in META_KEYS:
                    continue
                walk(child, parts + [k])
        elif isinstance(node, list):
            for i, child in enumerate(node):
                walk(child, parts + [f"[{i}]"])
        else:
            out.append(SourceEntry(path="json." + ".".join(parts).replace(".[", "["), kind="json",
                                   value=node, variants=_json_variants(parts)))

    walk(doc, [])
    return out


# ------------------------------------------------------------------ DB
def _db_variants(table: str, col: str, qual: str | None, is_default: bool) -> list[str]:
    t = normalize(table.removeprefix("client_")) if table != "client" else "client"
    c = normalize(col)
    out = []
    if qual:
        q = normalize(qual)
        out += [f"{q} {c}", f"{t} {q} {c}", f"{q} {t} {c}"]
    if is_default or not qual:
        out += [c, f"{t} {c}"]
    return list(dict.fromkeys(out))


def flatten_db(client_id: str) -> tuple[list[SourceEntry], dict[str, list[dict]]]:
    entries: list[SourceEntry] = []
    all_rows: dict[str, list[dict]] = {}
    cfg = settings()["db_tables"]
    for table in db.DD_TABLES:
        rows = db.client_rows(client_id, table)
        all_rows[table] = rows
        if table not in cfg or not rows:
            continue
        tc = cfg[table] or {}
        if "latest" in tc:
            rows = [max(rows, key=lambda r: r[tc["latest"]])]
            quals = [("latest", None)]
        elif "key" in tc:
            quals = [(f"{tc['key']}={r[tc['key']]}", r[tc["key"]]) for r in rows]
        else:
            rows, quals = rows[:1], [(None, None)]
        for row, (sel, qual) in zip(rows, quals):
            is_default = qual is not None and qual == tc.get("default")
            for col, val in row.items():
                if col == "client_id" or col == tc.get("key") or col == tc.get("latest"):
                    continue
                path = f"db.{table}" + (f"[{sel}]" if sel else "") + f".{col}"
                entries.append(SourceEntry(path=path, kind="db", value=val,
                                           variants=_db_variants(table, col, qual, is_default)))
    return entries, all_rows


# ------------------------------------------------------------------ build
def build_catalog(client_id: str) -> Catalog:
    """Everything known about one company. Either source alone is enough; neither is an error."""
    has_json = (JSON_DIR / f"{client_id}.json").exists()
    doc = load_json(client_id) if has_json else {}
    db_entries, rows = flatten_db(client_id)
    has_db = any(rows.values())
    if not has_json and not has_db:
        raise DataError(f"No data found for identifier {client_id}. Add its extracted JSON "
                        f"(data/extracted/{client_id}.json) or database rows with client_id = '{client_id}', "
                        "then fill again.")
    name = doc.get("client_name") or (rows["client"][0]["legal_name"] if rows.get("client") else client_id)
    cat = Catalog(client_id=client_id, client_name=name, raw_json=doc, db_rows=rows)
    for e in (flatten_json(doc) if doc else []) + db_entries:
        cat.entries[e.path] = e
    return cat
