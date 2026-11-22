"""Discover AcroForm fields in a fillable PDF (FR-2, FR-3)."""
from __future__ import annotations

from pathlib import Path

import pymupdf

from core.models import DiscoveredField

_TYPES = {
    pymupdf.PDF_WIDGET_TYPE_TEXT: "text",
    pymupdf.PDF_WIDGET_TYPE_CHECKBOX: "checkbox",
    pymupdf.PDF_WIDGET_TYPE_RADIOBUTTON: "radio",
    pymupdf.PDF_WIDGET_TYPE_COMBOBOX: "dropdown",
    pymupdf.PDF_WIDGET_TYPE_LISTBOX: "dropdown",
}


class TemplateError(Exception):
    pass


def _clean(state: str) -> str:
    return state.replace("#20", " ")


def discover(pdf_path: str | Path) -> list[DiscoveredField]:
    doc = pymupdf.open(str(pdf_path))
    try:
        if not doc.is_form_pdf:
            raise TemplateError("This PDF has no fillable form fields. Only fillable (AcroForm) "
                                "PDFs are supported; flat or scanned PDFs are out of scope.")
        fields: dict[str, DiscoveredField] = {}
        for page in doc:
            for w in page.widgets():
                ftype = _TYPES.get(w.field_type)
                if not ftype:
                    continue
                name = w.field_name
                if name in fields:
                    if ftype == "radio":
                        opt = _clean(w.on_state())
                        if opt not in fields[name].options:
                            fields[name].options.append(opt)
                    continue
                opts: list[str] = []
                if ftype == "radio":
                    opts = [_clean(w.on_state())]
                elif ftype == "dropdown":
                    opts = [o if isinstance(o, str) else o[0] for o in (w.choice_values or [])]
                    opts = [o for o in opts if o.strip()]
                r = w.rect
                fields[name] = DiscoveredField(
                    name=name, label=(w.field_label or "").strip(), type=ftype, options=opts,
                    page=page.number + 1, rect=(r.x0, r.y0, r.x1, r.y1),
                    max_length=(w.text_maxlen or None) if ftype == "text" else None)
        if not fields:
            raise TemplateError("No supported form fields were found in this PDF.")
        return list(fields.values())
    finally:
        doc.close()
