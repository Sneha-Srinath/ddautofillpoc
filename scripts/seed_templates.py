"""Register the five demo templates exactly as an admin would through the upload screen."""
from __future__ import annotations

from pathlib import Path

from core import registry
from scripts import mock_data as M
from scripts.build_docx_templates import DOCX_TEMPLATES
from scripts.build_html_templates import HTML_TEMPLATES
from scripts.template_specs import ALL_TEMPLATES

EVERY_TEMPLATE = ALL_TEMPLATES + DOCX_TEMPLATES + HTML_TEMPLATES


def run(specs: list[dict] | None = None, reset: bool = True) -> list:
    registry.CFG_DIR.mkdir(parents=True, exist_ok=True)
    if reset:
        for old in registry.CFG_DIR.glob("*.yaml"):
            old.unlink()
    names = {c["client_id"]: c["legal_name"] for c in M.CLIENTS}
    out = []
    for spec in (EVERY_TEMPLATE if specs is None else specs):
        src = registry.ROOT / spec["file"]
        cfg = registry.register(spec.get("company_name") or names[spec["client_id"]], spec["client_id"], src.read_bytes(),
                                template_name=spec["name"], file_name=Path(spec["file"]).name,
                                issuer=spec.get("issuer", ""), user="admin.demo")
        if registry.template_file(cfg) != src:
            src.unlink(missing_ok=True)
        print(f"{cfg.client_id}  {cfg.company_name:40} {cfg.name}  ({cfg.field_count} fields, "
              f"data: {registry.data_label(cfg.client_id)})")
        out.append(cfg)
    return out


if __name__ == "__main__":
    run()
