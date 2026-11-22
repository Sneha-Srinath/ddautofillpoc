"""Word (.docx) templates with {{placeholders}}.

  {{Applicant Legal Name}}                         text
  {{Uses a Third Party Administrator?}}            yes/no      -> "☒ Yes   ☐ No"
  {{Binding Authority: Full | Limited | Referral Only}}  choice -> "☒ Full   ☐ Limited   ☐ Referral Only"

Placeholders are found in body paragraphs, tables (including nested), headers and footers.
A placeholder whose text Word split across several runs is still found and replaced.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Iterator

import docx
from docx.document import Document as _Doc
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

from core.discovery import TemplateError
from core.models import DiscoveredField, ResolvedField

PLACEHOLDER = re.compile(r"\{\{\s*([^{}]+?)\s*\}\}")
BLANK = "__________"


def parse(inner: str) -> DiscoveredField:
    inner = inner.strip()
    if ":" in inner and "|" in inner.split(":", 1)[1]:
        label, opts = inner.split(":", 1)
        options = [o.strip() for o in opts.split("|") if o.strip()]
        return DiscoveredField(name=inner, label=label.strip(), type="radio", options=options)
    if inner.endswith("?"):
        return DiscoveredField(name=inner, label=inner[:-1].strip(), type="checkbox")
    return DiscoveredField(name=inner, label=inner, type="text")


def _tables(tables) -> Iterator[Paragraph]:
    for t in tables:
        for row in t.rows:
            for cell in row.cells:
                yield from cell.paragraphs
                yield from _tables(cell.tables)


def paragraphs(doc: _Doc) -> Iterator[Paragraph]:
    """Every paragraph in reading order: body paragraphs and tables as they appear, then headers/footers."""
    for child in doc.element.body.iterchildren():
        if child.tag == qn("w:p"):
            yield Paragraph(child, doc)
        elif child.tag == qn("w:tbl"):
            yield from _tables([Table(child, doc)])
    for section in doc.sections:
        for part in (section.header, section.footer, section.first_page_header, section.first_page_footer):
            if part is None or part.is_linked_to_previous:
                continue
            yield from part.paragraphs
            yield from _tables(part.tables)


def discover(path: str | Path) -> list[DiscoveredField]:
    try:
        doc = docx.Document(str(path))
    except Exception as exc:
        raise TemplateError("This file could not be read as a Word (.docx) document.") from exc
    found: dict[str, DiscoveredField] = {}
    for p in paragraphs(doc):
        for m in PLACEHOLDER.finditer(p.text):
            f = parse(m.group(1))
            found.setdefault(f.name, f)
    if not found:
        raise TemplateError("No fillable fields found in this Word document. Mark each field with a "
                            "placeholder such as {{Applicant Legal Name}}.")
    return list(found.values())


def render(field: DiscoveredField, rf: ResolvedField | None) -> str:
    value = None if rf is None else rf.value
    if field.type == "checkbox":
        if value is True:
            return "☒ Yes   ☐ No"
        if value is False:
            return "☐ Yes   ☒ No"
        return "☐ Yes   ☐ No"
    if field.type == "radio":
        return "   ".join(("☒ " if value == o else "☐ ") + o for o in field.options)
    return BLANK if value is None or str(value) == "" else str(value)


def _replace_in_paragraph(p: Paragraph, values: dict[str, str]) -> None:
    def sub(m: re.Match) -> str:
        return values.get(m.group(1).strip(), m.group(0))
    # 1) placeholders that sit inside a single run keep that run's formatting
    for run in p.runs:
        if "{{" in run.text and PLACEHOLDER.search(run.text):
            run.text = PLACEHOLDER.sub(sub, run.text)
    # 2) placeholders split across runs: rebuild the paragraph text in the first run that holds "{{"
    if PLACEHOLDER.search(p.text):
        runs = p.runs
        start = next(i for i, r in enumerate(runs) if "{" in r.text)
        merged = "".join(r.text for r in runs[start:])
        runs[start].text = PLACEHOLDER.sub(sub, merged)
        for r in runs[start + 1:]:
            r.text = ""


def fill(path: str | Path, fields: list[ResolvedField], out_path: str | Path, flatten: bool = False) -> Path:
    doc = docx.Document(str(path))
    by_name = {f.name: f for f in fields}
    defs = {f.name: f for f in discover(path)}
    values = {name: render(d, by_name.get(name)) for name, d in defs.items()}
    for p in paragraphs(doc):
        if "{{" in p.text:
            _replace_in_paragraph(p, values)
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out))
    return out


def text_of(path: str | Path) -> str:
    """All visible text (used by tests and checks)."""
    doc = docx.Document(str(path))
    return "\n".join(p.text for p in paragraphs(doc))
