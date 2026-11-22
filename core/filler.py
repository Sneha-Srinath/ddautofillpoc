"""Write resolved values into the PDF form, render previews, optionally flatten (FR-20, FR-23)."""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path

import pymupdf

from core.models import ResolvedField


def _pdfname(opt: str) -> str:
    return opt.replace(" ", "#20")


def fill_pdf(template_path: str | Path, fields: list[ResolvedField], out_path: str | Path,
             flatten: bool = False) -> Path:
    values = {f.name: f for f in fields}
    doc = pymupdf.open(str(template_path))
    radio_done: set[str] = set()
    for page in doc:
        for w in page.widgets():
            rf = values.get(w.field_name)
            if rf is None:
                continue
            t = w.field_type
            if t == pymupdf.PDF_WIDGET_TYPE_TEXT:
                w.field_value = "" if rf.value is None else str(rf.value)
                w.update()
            elif t == pymupdf.PDF_WIDGET_TYPE_CHECKBOX:
                w.field_value = w.on_state() if rf.value is True else "Off"
                w.update()
            elif t in (pymupdf.PDF_WIDGET_TYPE_COMBOBOX, pymupdf.PDF_WIDGET_TYPE_LISTBOX):
                w.field_value = rf.value if rf.value else " "
                w.update()
            elif t == pymupdf.PDF_WIDGET_TYPE_RADIOBUTTON:
                _set_radio(doc, w, rf.value)
                radio_done.add(w.field_name)
    if flatten:
        doc.bake()
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out), garbage=3, deflate=True)
    doc.close()
    return out


def _set_radio(doc: pymupdf.Document, w, value: str | None) -> None:
    """Set a radio kid's /AS directly and the parent's /V - deterministic across viewers."""
    on = w.on_state()
    selected = value is not None and on.replace("#20", " ") == value
    doc.xref_set_key(w.xref, "AS", f"/{_pdfname(on)}" if selected else "/Off")
    parent = doc.xref_get_key(w.xref, "Parent")
    if parent[0] == "xref":
        pxref = int(parent[1].split()[0])
        if selected:
            doc.xref_set_key(pxref, "V", f"/{_pdfname(on)}")
        elif value is None:
            doc.xref_set_key(pxref, "V", "/Off")


def read_back(pdf_path: str | Path) -> dict[str, object]:
    """Read field values from a filled PDF (used by tests and the download check)."""
    doc = pymupdf.open(str(pdf_path))
    out: dict[str, object] = {}
    for page in doc:
        for w in page.widgets():
            t = w.field_type
            if t == pymupdf.PDF_WIDGET_TYPE_RADIOBUTTON:
                state = doc.xref_get_key(w.xref, "AS")[1].lstrip("/")
                if state != "Off":
                    out[w.field_name] = state.replace("#20", " ")
                else:
                    out.setdefault(w.field_name, None)
            elif t == pymupdf.PDF_WIDGET_TYPE_CHECKBOX:
                out[w.field_name] = w.field_value not in (False, "Off", "", None)
            else:
                v = w.field_value
                out[w.field_name] = v.strip() if isinstance(v, str) and v.strip() else None
    doc.close()
    return out


def render_pages(pdf_path: str | Path, dpi: int = 110,
                 highlights: dict[str, str] | None = None) -> list[bytes]:
    """PNG per page. highlights maps field name -> hex colour; an outline is drawn around those
    fields in the rendered images only (the PDF file itself is never modified)."""
    doc = pymupdf.open(str(pdf_path))
    if highlights:
        for page in doc:
            for w in page.widgets():
                colour = highlights.get(w.field_name)
                if not colour:
                    continue
                rgb = tuple(int(colour.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4))
                r = pymupdf.Rect(w.rect) + (-1.6, -1.6, 1.6, 1.6)
                page.draw_rect(r, color=rgb, width=1.6, overlay=True)
    imgs = [page.get_pixmap(dpi=dpi).tobytes("png") for page in doc]
    doc.close()        # not saved
    return imgs


def output_name(client_name: str, template_name: str, on: date | None = None) -> str:
    def slug(s: str) -> str:
        return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")
    return f"{slug(client_name)}_{slug(template_name)}_{(on or date.today()).isoformat()}.pdf"
