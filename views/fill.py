"""Fill Template page (FR-16 .. FR-24)."""
from __future__ import annotations

import html
from pathlib import Path

import pandas as pd
import streamlit as st

from core import adapters, engine, registry
from core.catalog import DataError
from ui import theme
from ui.docview import filled_view, template_view

PANEL_HEIGHT = 620          # grid and document panel share this height so they line up
FILTER_KEY = "fill_filter"


def _clear_result() -> None:
    for k in ("fill", FILTER_KEY):
        st.session_state.pop(k, None)


def picker(by_id: dict) -> str:
    with st.container(key="fillbar"):
        c1, c2, c3, _ = st.columns([2.9, 3.1, 1.05, 1.2], vertical_alignment="bottom", gap="medium")
        with c1:
            tid = st.selectbox("Form", list(by_id), key="fill_template", on_change=_clear_result,
                               format_func=lambda i: f"{by_id[i].name} ({by_id[i].client_id}, "
                                                     f"{adapters.LABELS[by_id[i].format]})")
        cfg = by_id[tid]
        with c2:
            st.markdown(
                f'<div class="dd-company"><span class="lbl">Company</span>'
                f'<span class="val"><b>{html.escape(cfg.company_name or "-")}</b>'
                f'<span class="dd-id">ID {html.escape(cfg.client_id)}</span>'
                f'<span class="dd-fmt fmt-{cfg.format}">{adapters.LABELS[cfg.format]}</span></span></div>',
                unsafe_allow_html=True)
        with c3:
            clicked = st.button("Fill form", type="primary", use_container_width=True, icon=":material/bolt:")
    if clicked:
        try:
            with st.spinner("Filling…"):
                res = engine.fill(tid)
            st.session_state["fill"] = res.model_dump()
            st.session_state.pop("fill_error", None)
            st.session_state.pop(FILTER_KEY, None)
        except DataError:
            st.session_state.pop("fill", None)
            no_data_popup(cfg)
    return tid


@st.dialog("Data is not available")
def no_data_popup(cfg) -> None:
    st.markdown(f"We don't have any data for **{html.escape(cfg.company_name or cfg.client_id)}** "
                f"(identifier **{html.escape(cfg.client_id)}**) yet, so this form can't be filled.")
    st.markdown(f'<div class="dd-meta">Add the company&#39;s extracted JSON or its database rows under '
                f'identifier {html.escape(cfg.client_id)}, then choose Fill form again. The template itself is '
                'saved and ready.</div>', unsafe_allow_html=True)
    st.write("")
    if st.button("OK", type="primary", use_container_width=True):
        st.rerun()


# ------------------------------------------------------------------ status chips (filters)
def _toggle_filter(status: str) -> None:
    cur = st.session_state.get(FILTER_KEY)
    st.session_state[FILTER_KEY] = None if cur == status else status


def status_filters(counts: dict) -> None:
    active = st.session_state.get(FILTER_KEY)
    cols = st.columns(len(counts), gap="small")
    for col, (status, n) in zip(cols, counts.items()):
        with col:
            st.button(f"{n}  {status}", key=f"chip_{status}_{'on' if active == status else 'off'}",
                      on_click=_toggle_filter, args=(status,), use_container_width=True,
                      help=f"Show only {status.lower()} fields" if active != status else "Show all fields")


# ------------------------------------------------------------------ validation grid
def _rows(res: dict, status: str | None) -> pd.DataFrame:
    rows = []
    for f in res["fields"]:
        if status and f["status"] != status:
            continue
        opts = f" (options: {', '.join(f['options'])})" if f["options"] else ""
        rows.append({
            "Field": f["label"] or f["name"], "_name": f["name"], "Status": f["status"],
            "Value": f["display"] or "", "Source": f["source"],
            "Confidence": f["confidence"], "Source path": f["source_path"],
            "Note": (f["note"] or "") + (opts if f["status"] != "Filled" else ""),
        })
    return pd.DataFrame(rows)


def review(tid: str, res: dict) -> None:
    status = st.session_state.get(FILTER_KEY)
    df = _rows(res, status)
    editor_key = f"editor_{tid}_{status or 'all'}"

    # Pending edits are read from the editor's state, so Apply edits can sit above the grid
    pending = (st.session_state.get(editor_key) or {}).get("edited_rows", {})
    changes = {df.iloc[int(i)]["_name"]: v["Value"] for i, v in pending.items()
               if "Value" in v and str(v["Value"]) != str(df.iloc[int(i)]["Value"])}
    prior = dict(st.session_state.get("overrides", {}).get(tid, {}))

    with st.container(key="panelbar_grid"):
        b1, b2 = st.columns([1, 2.4], vertical_alignment="center")
        with b1:
            if st.button("Apply edits", disabled=not changes, icon=":material/refresh:", use_container_width=True,
                         help="Regenerates the document with your edits and records them in the audit log"):
                prior.update(changes)
                st.session_state.setdefault("overrides", {})[tid] = prior
                st.session_state["fill"] = engine.fill(tid, overrides=prior).model_dump()
                st.session_state.pop(editor_key, None)
                st.toast(f"Applied {len(changes)} edit(s). The document was regenerated and the edit logged.")
                st.rerun()
        with b2:
            shown = f"{len(df)} {status.lower()} field{'s' if len(df) != 1 else ''}" if status \
                else f"All {len(df)} fields"
            extra = f" {len(changes)} unsaved edit{'s' if len(changes) != 1 else ''}." if changes else ""
            st.markdown(f'<div class="dd-meta">{shown}.{extra} Edit a value, then choose Apply edits.</div>',
                        unsafe_allow_html=True)

    if df.empty:
        with st.container(height=PANEL_HEIGHT, border=True):
            st.markdown(f'<div class="dd-meta">No {status.lower() if status else ""} fields.</div>',
                        unsafe_allow_html=True)
        return
    st.data_editor(
        df, hide_index=True, use_container_width=True, height=PANEL_HEIGHT, key=editor_key,
        column_order=["Field", "Status", "Value", "Source", "Confidence", "Note", "Source path"],
        disabled=["Field", "Status", "Source", "Confidence", "Source path", "Note"],
        column_config={
            "Field": st.column_config.TextColumn(width="medium"),
            "Status": st.column_config.TextColumn(width="small"),
            "Value": st.column_config.TextColumn(width="medium", help="Edit, then choose Apply edits"),
            "Source": st.column_config.TextColumn(width="small"),
            "Confidence": st.column_config.ProgressColumn(min_value=0, max_value=1, format="%.2f", width="small"),
            "Source path": st.column_config.TextColumn(width="medium"),
            "Note": st.column_config.TextColumn(width="medium"),
        })
    if prior:
        st.caption(f"User edits in this session: {', '.join(prior)}")


# ------------------------------------------------------------------ results area
def result(tid: str) -> None:
    res = st.session_state.get("fill")
    if not res or res["template_id"] != tid:
        template_preview(registry.get(tid))
        return
    counts = {s: 0 for s in theme.STATUS}
    for f in res["fields"]:
        counts[f["status"]] += 1
    cfg = registry.get(tid)
    fmt = cfg.format
    label = {"pdf": "PDF", "docx": "Word document", "html": "web form"}[fmt]
    theme.section(res["client_name"])

    chips, actions = st.columns([5.0, 4.5], vertical_alignment="center", gap="small")
    with chips:
        status_filters(counts)
    with actions:
        a1, a2, a3, a4 = st.columns([1.05, 1.3, 1.0, 1.6], vertical_alignment="center", gap="small")
        with a1:
            layout = st.segmented_control(
                "Layout", ["Side by side", "Tabs"], default="Side by side", key="fill_layout",
                label_visibility="collapsed", help="Side by side or tabs",
                format_func=lambda o: ":material/view_column_2:" if o == "Side by side" else ":material/tab:",
            ) or "Side by side"
        with a2:
            mark = st.toggle("Highlight", value=True, key="fill_highlight", disabled=fmt == "docx",
                             help="Outline each field in the preview by status (PDF and web form). "
                                  "The downloaded file is not marked.")
        with a3:
            flatten = st.checkbox("Flatten", key="fill_flatten", disabled=fmt != "pdf",
                                  help="Makes the downloaded PDF non-editable (PDF templates only)")
        with a4:
            download_button(tid, res, flatten and fmt == "pdf", fmt)
    theme.status_bar(counts)
    marks = ({f["name"]: theme.STATUS[f["status"]]["fg"] for f in res["fields"]}
             if mark and fmt != "docx" else None)

    if layout == "Tabs":
        t1, t2 = st.tabs(["Validation results", f"Filled {label}"])
        with t1:
            review(tid, res)
        with t2:
            filled_view(fmt, res["output_path"], key="fillpdf", height=PANEL_HEIGHT, highlights=marks)
        return
    left, right = st.columns(2, gap="large")
    with left:
        theme.section("Validation results")
        review(tid, res)
    with right:
        theme.section(f"Filled {label}")
        filled_view(fmt, res["output_path"], key="fillpdf", height=PANEL_HEIGHT, highlights=marks)


def template_preview(cfg) -> None:
    label = registry.data_label(cfg.client_id)
    theme.section(f"{cfg.name}")
    note = (f"Empty template for {cfg.company_name} ({cfg.client_id}), {cfg.field_count} fillable fields. "
            "Choose Fill form to fill it from this company's data.")
    if label == "No data found":
        note = (f"No JSON or database rows exist yet for identifier {cfg.client_id}, so this template "
                "cannot be filled until that data is added.")
    st.markdown(f'<div class="dd-meta" style="margin-bottom:.6rem">{note}</div>', unsafe_allow_html=True)
    template_view(cfg.format, registry.template_file(cfg), key="filltpl")


def download_button(tid: str, res: dict, flatten: bool, fmt: str = "pdf") -> None:
    if flatten:
        prior = st.session_state.get("overrides", {}).get(tid) or None
        final = engine.fill(tid, overrides=prior, flatten=True, log=False)
        data, name = Path(final.output_path).read_bytes(), final.output_name
    else:
        data, name = Path(res["output_path"]).read_bytes(), res["output_name"]
    word = {"pdf": "PDF", "docx": "Word", "html": "form"}[fmt]
    st.download_button(f"Download {word}", data, file_name=name, mime=adapters.MIME[fmt],
                       type="primary", use_container_width=True, icon=":material/download:")


def main() -> None:
    theme.header("Fill a due diligence form")
    templates = registry.list_templates()
    if not templates:
        st.info("No templates are registered yet. Run `python -m scripts.build_all` or add one on Template setup.")
        return
    by_id = {t.template_id: t for t in templates}
    if st.session_state.get("fill_template") not in by_id:
        st.session_state.pop("fill_template", None)
    tid = picker(by_id)
    result(tid)


main()
