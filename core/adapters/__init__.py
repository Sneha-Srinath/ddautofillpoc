"""One interface for every template format: discover fields, fill, read back.

    adapter = adapters.get("docx")
    fields  = adapter.discover(path)
    out     = adapter.fill(path, resolved_fields, out_path, flatten=False)
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from core import discovery, filler
from core.adapters import docx_adapter, html_adapter

FORMATS = {
    ".pdf": "pdf",
    ".docx": "docx",
    ".html": "html",
    ".htm": "html",
}
LABELS = {"pdf": "PDF", "docx": "Word", "html": "Web form"}
EXTENSIONS = {"pdf": ".pdf", "docx": ".docx", "html": ".html"}
MIME = {"pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "html": "text/html"}


@dataclass(frozen=True)
class Adapter:
    format: str
    discover: Callable
    fill: Callable
    read_back: Callable


_ADAPTERS = {
    "pdf": Adapter("pdf", discovery.discover, filler.fill_pdf, filler.read_back),
    "docx": Adapter("docx", docx_adapter.discover, docx_adapter.fill, docx_adapter.text_of),
    "html": Adapter("html", html_adapter.discover, html_adapter.fill, html_adapter.read_back),
}


def get(fmt: str) -> Adapter:
    return _ADAPTERS[fmt]


def format_of(file_name: str) -> str | None:
    return FORMATS.get(Path(file_name).suffix.lower())
