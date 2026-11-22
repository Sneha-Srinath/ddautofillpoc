"""PDF viewer used on the Fill page and in the template preview.

Two views: page by page (one page fitted to the screen height, with a pager) or a scroll
window with every page. Images are rendered once per file version and cached.
"""
from __future__ import annotations

from pathlib import Path

import streamlit as st

from core.filler import render_pages

MODES = ["Page by page", "Scroll"]


@st.cache_data(show_spinner=False, max_entries=64)
def _pages(path: str, mtime: float, dpi: int, highlights: tuple = ()) -> list[bytes]:
    return render_pages(path, dpi=dpi, highlights=dict(highlights) or None)


def pdf_viewer(path: str | Path, key: str, scroll_height: int = 760, dpi: int = 120,
               height: int | None = None, highlights: dict[str, str] | None = None) -> None:
    """height: fixed panel height in px for both views (lines the viewer up with a grid beside it).
    highlights: field name -> colour outlines drawn on the on-screen pages only."""
    p = Path(path)
    pages = _pages(str(p), p.stat().st_mtime, dpi, tuple(sorted((highlights or {}).items())))
    n = len(pages)
    page_key = f"{key}_page"
    if st.session_state.get(f"{key}_file") != str(p):        # new file -> back to page 1
        st.session_state[f"{key}_file"] = str(p)
        st.session_state[page_key] = 1
    page = min(max(st.session_state.get(page_key, 1), 1), n)

    bar = st.container(key=f"panelbar_{key}").columns([1.6, 0.45, 1, 0.45], vertical_alignment="center")
    with bar[0]:
        mode = st.segmented_control("View", MODES, default=MODES[0], key=f"{key}_mode",
                                    label_visibility="collapsed") or MODES[0]
    if mode == MODES[0] and n > 1:
        with bar[1]:
            st.button("", icon=":material/chevron_left:", key=f"{key}_prev", disabled=page <= 1,
                      help="Previous page", use_container_width=True,
                      on_click=_go, args=(page_key, page - 1))
        with bar[2]:
            st.markdown(f'<div class="dd-meta" style="text-align:center">Page {page} of {n}</div>',
                        unsafe_allow_html=True)
        with bar[3]:
            st.button("", icon=":material/chevron_right:", key=f"{key}_next", disabled=page >= n,
                      help="Next page", use_container_width=True,
                      on_click=_go, args=(page_key, page + 1))
    elif mode == MODES[1]:
        with bar[2]:
            st.markdown(f'<div class="dd-meta" style="text-align:center">{n} page{"s" if n != 1 else ""}</div>',
                        unsafe_allow_html=True)

    if mode == MODES[0]:
        box = {"height": height} if height else {}
        with st.container(key=f"pdffit_{key}", border=False, **box):
            if height:   # inside the panel, so the panel itself starts level with the grid beside it
                st.markdown(f"<style>.st-key-pdffit_{key} img {{ max-height: {height - 50}px !important; }}</style>",
                            unsafe_allow_html=True)
            st.image(pages[page - 1], use_container_width=True)
    else:
        with st.container(height=height or scroll_height, key=f"pdfscroll_{key}"):
            for i, png in enumerate(pages, start=1):
                st.image(png, caption=f"Page {i} of {n}", use_container_width=True)


def _go(page_key: str, page: int) -> None:
    st.session_state[page_key] = page


def pdf_scroll(path: str | Path, key: str, height: int = 600, dpi: int = 110) -> None:
    """Scroll-only view: every page stacked at full container width (used by the template preview)."""
    p = Path(path)
    pages = _pages(str(p), p.stat().st_mtime, dpi)
    with st.container(height=height, key=f"pdfonly_{key}"):
        for i, png in enumerate(pages, start=1):
            st.image(png, caption=f"Page {i} of {len(pages)}", use_container_width=True)
