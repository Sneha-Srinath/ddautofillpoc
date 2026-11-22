"""Preview any template or filled document: PDF, Word (rendered by Word as PDF) or web form."""
from __future__ import annotations

from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from core.adapters import html_adapter, word_render
from ui.pdfview import pdf_scroll, pdf_viewer


def word_pdf(path: str | Path) -> Path | None:
    """Exact PDF of a Word file, or None when Word is unavailable."""
    try:
        with st.spinner("Preparing Word preview…"):
            return word_render.to_pdf(path)
    except word_render.RenderError:
        return None


def _web_form(path: str | Path, height: int, highlights: dict[str, str] | None = None) -> None:
    with st.container(key="webform_frame"):
        components.html(html_adapter.preview_html(path, highlights), height=height, scrolling=True)


def _word_fallback(path: str | Path, height: int) -> None:
    st.markdown('<div class="dd-meta">Approximate preview: Microsoft Word is not available to render this '
                'document exactly.</div>', unsafe_allow_html=True)
    with st.container(key="webform_frame"):
        components.html(word_render.to_html(path), height=height, scrolling=True)


def template_view(fmt: str, path: str | Path, key: str, height: int = 760) -> None:
    """Empty template on the Fill page and in the preview dialog: scroll view."""
    if fmt == "html":
        _web_form(path, height)
    elif fmt == "docx":
        pdf = word_pdf(path)
        if pdf:
            pdf_scroll(pdf, key=key, dpi=120)
        else:
            _word_fallback(path, height)
    else:
        pdf_scroll(path, key=key, dpi=120)


def filled_view(fmt: str, path: str | Path, key: str, height: int,
                highlights: dict[str, str] | None = None) -> None:
    """Filled document beside the validation grid."""
    if fmt == "html":
        _web_form(path, height, highlights)
    elif fmt == "docx":
        pdf = word_pdf(path)
        if pdf:
            pdf_viewer(pdf, key=key, height=height)
        else:
            _word_fallback(path, height)
    else:
        pdf_viewer(path, key=key, height=height, highlights=highlights)
