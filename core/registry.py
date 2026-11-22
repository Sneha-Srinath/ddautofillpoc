"""Template registry: one YAML record per uploaded template in config/templates/.

The unique identifier (stored as client_id) is alphanumeric, upper-cased and unique. It is the key
into the company's extracted JSON (data/extracted/<ID>.json) and its database rows (client_id).
"""
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

import pymupdf
import yaml

from core import config
from core import adapters
from core.discovery import TemplateError
from core.models import TemplateConfig

ID_RULE = re.compile(r"^[A-Za-z0-9]{2,20}$")
ID_HELP = "2 to 20 letters and numbers, no spaces or symbols"

# Overridable in tests
CFG_DIR: Path = config.TEMPLATE_CFG_DIR
PDF_DIR: Path = config.ROOT / "templates"
ROOT: Path = config.ROOT


class RegistryError(Exception):
    """A template could not be registered or found; the message is shown to the user."""


def normalize_id(identifier: str) -> str:
    return (identifier or "").strip().upper()


def validate_id(identifier: str, company_name: str = "", fmt: str | None = None) -> str:
    """Identifier rules. An identifier belongs to one company; each company may have one template per
    format (PDF, Word, web form)."""
    ident = normalize_id(identifier)
    if not ident:
        raise RegistryError("Enter a unique identifier.")
    if not ID_RULE.fullmatch(ident):
        raise RegistryError(f"Identifier '{identifier.strip()}' is not valid: use {ID_HELP}.")
    same = [t for t in list_templates() if t.client_id == ident]
    if same:
        owner = same[0].company_name or same[0].name
        if company_name and owner.strip().casefold() != company_name.strip().casefold():
            raise RegistryError(f"Identifier {ident} is already used by {owner}. Each company needs its own "
                                "identifier; choose that company to add another template type.")
        if fmt and any(t.format == fmt for t in same):
            raise RegistryError(f"{owner} ({ident}) already has a {adapters.LABELS[fmt]} template. "
                                "Delete it first to replace it.")
    return ident


def _path(template_id: str) -> Path:
    return CFG_DIR / f"{template_id}.yaml"


def list_templates() -> list[TemplateConfig]:
    if not CFG_DIR.exists():
        return []
    out = [TemplateConfig.model_validate(yaml.safe_load(p.read_text(encoding="utf-8")))
           for p in sorted(CFG_DIR.glob("*.yaml"))]
    order = {"pdf": 0, "docx": 1, "html": 2}
    return sorted(out, key=lambda t: (t.client_id, order.get(t.format, 9)))


def get(template_id: str) -> TemplateConfig:
    p = _path(template_id)
    if not p.exists():
        raise RegistryError(f"Template {template_id} is not registered.")
    return TemplateConfig.model_validate(yaml.safe_load(p.read_text(encoding="utf-8")))


def for_client(client_id: str, fmt: str = "pdf") -> TemplateConfig | None:
    ident = normalize_id(client_id)
    return next((t for t in list_templates() if t.client_id == ident and t.format == fmt), None)


def formats_for(client_id: str) -> list[str]:
    ident = normalize_id(client_id)
    return [t.format for t in list_templates() if t.client_id == ident]


def companies() -> dict[str, str]:
    """identifier -> company name, for every company with at least one template."""
    out: dict[str, str] = {}
    for t in list_templates():
        out.setdefault(t.client_id, t.company_name or t.name)
    return out


def template_file(cfg: TemplateConfig) -> Path:
    return ROOT / cfg.file


def _write(cfg: TemplateConfig) -> None:
    CFG_DIR.mkdir(parents=True, exist_ok=True)
    data = cfg.model_dump(mode="json", exclude_none=True, exclude={"fields"})
    _path(cfg.template_id).write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=120),
                                      encoding="utf-8")


def _slug(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_")[:60] or "template"


def _pdf_title(pdf: bytes) -> str:
    try:
        with pymupdf.open(stream=pdf, filetype="pdf") as doc:
            title = (doc.metadata or {}).get("title") or ""
            return title.split(" - ")[0].strip()
    except Exception:
        return ""


def _title(data: bytes, fmt: str) -> str:
    if fmt == "pdf":
        return _pdf_title(data)
    if fmt == "html":
        m = re.search(rb"<title>(.*?)</title>", data, re.I | re.S)
        return m.group(1).decode("utf-8", "replace").strip() if m else ""
    try:
        import io
        import docx
        return (docx.Document(io.BytesIO(data)).core_properties.title or "").strip()
    except Exception:
        return ""


def register(company_name: str, identifier: str, data: bytes, template_name: str | None = None,
             file_name: str = "template.pdf", issuer: str = "", user: str | None = None) -> TemplateConfig:
    """Validate and store an empty template (PDF, Word or web form) for one company.
    Nothing is written on failure."""
    company = (company_name or "").strip()
    if not company:
        raise RegistryError("Enter the company name.")
    fmt = adapters.format_of(file_name)
    if fmt is None:
        raise RegistryError("Upload a PDF, Word (.docx) or web form (.html) file.")
    ident = validate_id(identifier, company, fmt)
    if not data:
        raise RegistryError("Choose a file to upload.")

    PDF_DIR.mkdir(parents=True, exist_ok=True)
    name = (template_name or "").strip() or _title(data, fmt) or Path(file_name).stem.replace("_", " ")
    ext = adapters.EXTENSIONS[fmt]
    target = PDF_DIR / f"{ident}_{_slug(name)}{ext}"
    tmp = target.with_name(target.stem + ".upload" + ext)
    tmp.write_bytes(data)
    try:
        fields = adapters.get(fmt).discover(tmp)
    except TemplateError as exc:
        tmp.unlink(missing_ok=True)
        raise RegistryError(str(exc)) from exc
    except Exception as exc:
        tmp.unlink(missing_ok=True)
        raise RegistryError(f"This file could not be read as a {adapters.LABELS[fmt]} template.") from exc
    tmp.replace(target)

    try:
        rel = target.relative_to(ROOT).as_posix()
    except ValueError:
        rel = str(target)
    tid = f"tpl-{ident.lower()}" if fmt == "pdf" else f"tpl-{ident.lower()}-{fmt}"
    cfg = TemplateConfig(
        template_id=tid, client_id=ident, company_name=company, name=name, issuer=issuer, format=fmt,
        file=rel, field_count=len(fields), uploaded_on=datetime.now().isoformat(timespec="minutes"),
        uploaded_by=user or config.current_user())
    _write(cfg)
    return cfg


def delete(template_id: str) -> TemplateConfig:
    """Remove one template file and its registry record. Company data and audit history are untouched."""
    cfg = get(template_id)
    template_file(cfg).unlink(missing_ok=True)
    _path(template_id).unlink(missing_ok=True)
    return cfg


def has_data(client_id: str) -> dict[str, bool]:
    """Which sources hold data for this identifier."""
    from core import db
    ident = normalize_id(client_id)
    json_ok = (config.JSON_DIR / f"{ident}.json").exists()
    try:
        db_ok = db.client_record(ident) is not None
    except Exception:
        db_ok = False
    return {"json": json_ok, "db": db_ok}


def data_label(client_id: str) -> str:
    d = has_data(client_id)
    if d["json"] and d["db"]:
        return "JSON + DB"
    if d["json"]:
        return "JSON only"
    if d["db"]:
        return "DB only"
    return "No data found"
