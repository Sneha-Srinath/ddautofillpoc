"""One-click fill orchestration. Pure Python - reusable from Streamlit, FastAPI or batch jobs.

Fields are matched to the company's data at fill time: discover the PDF's form fields, auto-match
each one against the company's JSON paths and database columns (exact, glossary synonym, fuzzy),
then resolve, convert and write the values.
"""
from __future__ import annotations

import time
from functools import lru_cache
from pathlib import Path
from typing import Any

from core import adapters, audit, registry
from core.catalog import build_catalog
from core.config import OUTPUT_DIR, current_user
from core.filler import output_name
from core.matcher import auto_match
from core.models import DiscoveredField, FieldMapping, FillResult, TemplateConfig
from core.resolver import resolve


@lru_cache(maxsize=64)
def _discover_cached(path: str, mtime: float, fmt: str) -> tuple[DiscoveredField, ...]:
    return tuple(adapters.get(fmt).discover(path))


def template_fields(cfg: TemplateConfig) -> list[DiscoveredField]:
    p = registry.template_file(cfg)
    return [f.model_copy(deep=True) for f in _discover_cached(str(p), p.stat().st_mtime, cfg.format)]


def match_fields(cfg: TemplateConfig, catalog) -> dict[str, FieldMapping]:
    """Match every PDF field to this company's data; nothing is saved."""
    return {p.field.name: p.to_mapping() for p in auto_match(template_fields(cfg), catalog, use_llm=False)}


def fill(template_id: str, overrides: dict[str, Any] | None = None, flatten: bool = False,
         user: str | None = None, log: bool = True) -> FillResult:
    t0 = time.perf_counter()
    cfg = registry.get(template_id)
    cat = build_catalog(cfg.client_id)          # refuses wrong client_id; DataError when no data at all
    cfg = cfg.model_copy(update={"fields": match_fields(cfg, cat)})
    fields = resolve(cfg, cat, overrides)
    ext = adapters.EXTENSIONS[cfg.format]
    name = output_name(cfg.company_name or cat.client_name, cfg.name).replace(".pdf", ext)
    suffix = "_final" if flatten and cfg.format == "pdf" else ""
    out = adapters.get(cfg.format).fill(registry.template_file(cfg), fields,
                                        OUTPUT_DIR / cfg.client_id / name.replace(ext, f"{suffix}{ext}"),
                                        flatten=flatten and cfg.format == "pdf")
    ms = int((time.perf_counter() - t0) * 1000)
    res = FillResult(template_id=cfg.template_id, client_id=cfg.client_id,
                     client_name=cfg.company_name or cat.client_name, fields=fields, output_path=str(out),
                     output_name=name, elapsed_ms=ms, input_hash=cat.input_hash())
    if log:
        audit.log_fill(user=user or current_user(),
                       action="Download (flattened)" if flatten else ("Apply edits" if overrides else "Fill"),
                       template_id=cfg.template_id, template_version=cfg.version,
                       mapping_version=cfg.mapping_version, client_id=cfg.client_id, counts=res.counts(),
                       edited=overrides or {}, output_file=Path(out).name, input_hash=res.input_hash,
                       elapsed_ms=ms)
    return res
