"""Template setup: upload each company's empty fillable PDF, list them, preview and delete."""
from __future__ import annotations

import html

import streamlit as st

from core import registry
from core.models import TemplateConfig
from ui import theme
from core import adapters, db
from ui.docview import template_view

DATA_BADGE = {
    "JSON + DB": ("#1F6B45", "#E3F1E9"),
    "JSON only": ("#1F5F8B", "#E2EEF7"),
    "DB only": ("#1F5F8B", "#E2EEF7"),
    "No data found": ("#9C2F2F", "#F8E2E2"),
}
COLS = [2.3, 0.9, 2.7, 0.9, 0.55, 1.1, 1.2, 1.5]


@st.dialog("Template preview", width="medium")
def preview_template(cfg: TemplateConfig) -> None:
    st.markdown(f'<div class="dd-meta"><b style="color:{theme.INK}">{html.escape(cfg.name)}</b>. '
                f'{html.escape(cfg.company_name)} ({cfg.client_id}). {cfg.field_count} fillable fields. '
                'Blank template as uploaded.</div>', unsafe_allow_html=True)
    template_view(cfg.format, registry.template_file(cfg), key=f"tplprev_{cfg.template_id}", height=640)


@st.dialog("Delete template")
def confirm_delete(cfg: TemplateConfig) -> None:
    st.markdown(f"Delete the {adapters.LABELS[cfg.format]} template for **{cfg.company_name}** ({cfg.client_id})?")
    st.markdown('<div class="dd-meta">This file and its registry entry are removed; the company&#39;s other template '
                'types stay. The company\'s JSON, database '
                'rows and past audit entries are kept.</div>', unsafe_allow_html=True)
    st.write("")
    a, b = st.columns(2)
    with a:
        if st.button("Delete template", type="primary", use_container_width=True, icon=":material/delete:"):
            registry.delete(cfg.template_id)
            st.session_state["setup_notice"] = (f"Deleted the {adapters.LABELS[cfg.format]} template for "
                                                f"{cfg.company_name} ({cfg.client_id}).")
            if st.session_state.get("fill_template") == cfg.template_id:
                st.session_state.pop("fill_template", None)
            st.rerun()
    with b:
        if st.button("Cancel", use_container_width=True):
            st.rerun()


NEW_COMPANY = "__new__"


def _company_options() -> dict[str, str]:
    """identifier -> company name: companies with templates, then companies that only have data."""
    out = dict(registry.companies())
    for cid, name in db.client_names().items():
        out.setdefault(cid, name)
    return dict(sorted(out.items()))


def upload_card() -> None:
    with st.container(key="uploadcard"):
        theme.section("Upload a template")
        options = _company_options()
        sel, _ = st.columns([1.6, 2.6])
        with sel:
            choice = st.selectbox(
                "Select company", [NEW_COMPANY] + list(options), key="upload_company",
                format_func=lambda c: "New company" if c == NEW_COMPANY else f"{options[c]} ({c})")
        has = [adapters.LABELS[f] for f in registry.formats_for(choice)] if choice != NEW_COMPANY else []
        with st.form("upload", clear_on_submit=True, border=False):
            c1, c2, c3 = st.columns([1.6, 1, 1.6])
            if choice == NEW_COMPANY:
                with c1:
                    company = st.text_input("Company name", placeholder="e.g. Harbor Point Insurance Group, LLC")
                with c2:
                    ident = st.text_input("Unique identifier", placeholder="e.g. C015", max_chars=20,
                                          help=f"{registry.ID_HELP}. Must match the client_id in the company's "
                                               "extracted JSON and database rows.")
            else:
                company, ident = options[choice], choice
                with c1:
                    st.text_input("Company name", value=company, disabled=True)
                with c2:
                    st.text_input("Unique identifier", value=ident, disabled=True)
            with c3:
                name = st.text_input("Template name (optional)", placeholder="Taken from the file if left blank")
            f1, f2, f3 = st.columns([2.2, 0.95, 2.6], vertical_alignment="bottom")
            with f1:
                upload = st.file_uploader("Template file (PDF, Word or web form)",
                                          type=["pdf", "docx", "html", "htm"])
            with f2:
                submitted = st.form_submit_button("Add template", type="primary", use_container_width=True,
                                                  icon=":material/upload_file:")
            with f3:
                hint = (f"{options[choice]} already has: {', '.join(has)}. One of each type is allowed."
                        if has else "One PDF, one Word document and one web form per company.")
                st.markdown(f'<div class="dd-meta" style="margin-bottom:14px">{html.escape(hint)}</div>',
                            unsafe_allow_html=True)
        if submitted:
            try:
                cfg = registry.register(company, ident, upload.getvalue() if upload else b"", template_name=name,
                                        file_name=upload.name if upload else "template.pdf")
            except registry.RegistryError as exc:
                st.error(str(exc), icon=":material/error:")
            else:
                label = registry.data_label(cfg.client_id)
                note = "" if label != "No data found" else " No JSON or database rows exist for it yet."
                st.session_state["setup_notice"] = (
                    f"Uploaded {adapters.LABELS[cfg.format]} template {cfg.name} for {cfg.company_name} "
                    f"({cfg.client_id}), {cfg.field_count} fields.{note}")
                st.rerun()


def badge(label: str) -> str:
    fg, bg = DATA_BADGE[label]
    return (f'<span style="background:{bg};color:{fg};padding:.15rem .5rem;border-radius:999px;'
            f'font-size:.78rem;font-weight:500;white-space:nowrap">{label}</span>')


PAGE_KEY, SIZE_KEY = "tpl_page", "tpl_page_size"
HEADERS = ["Company name", "Identifier", "Template", "Type", "Fields", "Data", "Uploaded", "Actions"]


def _set_page(page: int) -> None:
    st.session_state[PAGE_KEY] = page


def template_grid(templates: list[TemplateConfig]) -> None:
    theme.section(f"Uploaded templates ({len(templates)})")
    if not templates:
        st.markdown('<div class="dd-panel">No templates yet. Upload a company&#39;s empty PDF, Word document or web form above.</div>',
                    unsafe_allow_html=True)
        return

    st.session_state.setdefault(SIZE_KEY, 10)
    size = st.session_state[SIZE_KEY]
    pages = max(1, -(-len(templates) // size))
    page = min(max(st.session_state.get(PAGE_KEY, 1), 1), pages)
    shown = templates[(page - 1) * size: page * size]

    with st.container(key="tplgrid"):
        with st.container(key="tplhead"):
            for col, label in zip(st.columns(COLS, vertical_alignment="center"), HEADERS):
                align = " center" if label in ("Actions", "Fields") else ""
                col.markdown(f'<div class="dd-grid-head{align}">{label}</div>', unsafe_allow_html=True)
        for t in shown:
            with st.container(key=f"tplrow_{t.template_id}"):
                c = st.columns(COLS, vertical_alignment="center")
                c[0].markdown(f'<div class="dd-cell"><b>{html.escape(t.company_name or "-")}</b></div>',
                              unsafe_allow_html=True)
                c[1].markdown(f'<div class="dd-cell"><code>{t.client_id}</code></div>', unsafe_allow_html=True)
                c[2].markdown(f'<div class="dd-cell">{html.escape(t.name)}</div>', unsafe_allow_html=True)
                c[3].markdown(f'<span class="dd-fmt fmt-{t.format}">{adapters.LABELS[t.format]}</span>',
                              unsafe_allow_html=True)
                c[4].markdown(f'<div class="dd-cell center">{t.field_count}</div>', unsafe_allow_html=True)
                c[5].markdown(badge(registry.data_label(t.client_id)), unsafe_allow_html=True)
                c[6].markdown(f'<div class="dd-cell dd-meta">{t.uploaded_on.replace("T", " ")}</div>',
                              unsafe_allow_html=True)
                with c[7].container(key=f"actions_{t.template_id}", horizontal=True,
                                    horizontal_alignment="center", gap="small"):
                    if st.button("", key=f"prev_{t.template_id}", icon=":material/visibility:",
                                 help=f"Preview {t.name}"):
                        preview_template(t)
                    path = registry.template_file(t)
                    st.download_button("", path.read_bytes() if path.exists() else b"", file_name=path.name,
                                       mime=adapters.MIME[t.format], key=f"dl_{t.template_id}",
                                       icon=":material/download:", help=f"Download the empty {t.name}",
                                       disabled=not path.exists())
                    if st.button("", key=f"del_{t.template_id}", icon=":material/delete:",
                                 help=f"Delete the template for {t.company_name}"):
                        confirm_delete(t)

    first, last = (page - 1) * size + 1, min(page * size, len(templates))
    p1, p2, p3, p4, p5 = st.columns([3.2, 1.1, 0.45, 0.9, 0.45], vertical_alignment="center")
    with p1:
        st.markdown(f'<div class="dd-meta">Showing {first} to {last} of {len(templates)} templates</div>',
                    unsafe_allow_html=True)
    with p2:
        st.selectbox("Rows per page", [5, 10, 20], key=SIZE_KEY, label_visibility="collapsed",
                     format_func=lambda n: f"{n} per page", on_change=_set_page, args=(1,))
    with p3:
        st.button("", icon=":material/chevron_left:", key="tpl_prev", disabled=page <= 1, help="Previous page",
                  on_click=_set_page, args=(page - 1,), use_container_width=True)
    with p4:
        st.markdown(f'<div class="dd-meta" style="text-align:center">Page {page} of {pages}</div>',
                    unsafe_allow_html=True)
    with p5:
        st.button("", icon=":material/chevron_right:", key="tpl_next", disabled=page >= pages, help="Next page",
                  on_click=_set_page, args=(page + 1,), use_container_width=True)


def main() -> None:
    theme.header("Template setup")
    if st.session_state.get("setup_notice"):
        st.success(st.session_state.pop("setup_notice"), icon=":material/task_alt:")
    upload_card()
    st.write("")
    template_grid(registry.list_templates())


main()
