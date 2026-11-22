"""Data page (FR-25): the extracted JSON and database rows a fill reads, per company identifier."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from core import db, registry
from core.catalog import flatten_json, load_json
from core.config import JSON_DIR, REPORTS_DIR
from ui import theme


def companies() -> dict[str, str]:
    """identifier -> company name, from registered templates plus every client in the database."""
    out = {t.client_id: t.company_name or t.name for t in registry.list_templates()}
    for cid, name in db.client_names().items():
        out.setdefault(cid, name)
    for p in JSON_DIR.glob("*.json"):
        out.setdefault(p.stem.upper(), p.stem.upper())
    return dict(sorted(out.items()))


def json_tab(cid: str) -> None:
    if not (JSON_DIR / f"{cid}.json").exists():
        st.info(f"No extracted JSON for identifier {cid}. Expected file: data/extracted/{cid}.json",
                icon=":material/info:")
        return
    try:
        doc = load_json(cid)
    except Exception as exc:
        st.error(str(exc), icon=":material/error:")
        return
    st.markdown(f'<div class="dd-meta">Extracted {doc.get("extracted_at", "")} from: '
                f'{", ".join(doc.get("source_documents", []))}</div>', unsafe_allow_html=True)
    rows = [{"Path": e.path, "Value": "" if e.value is None else str(e.value), "Confidence": e.confidence,
             "Source document": e.source_ref or ""} for e in flatten_json(doc)]
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True, height=460, column_config={
        "Confidence": st.column_config.ProgressColumn(min_value=0, max_value=1, format="%.2f")})
    with st.expander("Raw JSON"):
        st.json(doc, expanded=1)


def db_tab(cid: str) -> None:
    any_rows = False
    for table in db.DD_TABLES:
        frame = db.client_frame(cid, table)
        any_rows = any_rows or not frame.empty
        with st.expander(f"{table}  ({len(frame)} row{'s' if len(frame) != 1 else ''})",
                         expanded=table == "client" and not frame.empty):
            if frame.empty:
                st.caption("No rows for this identifier.")
            else:
                st.dataframe(frame, hide_index=True, use_container_width=True)
    if not any_rows:
        st.info(f"No database rows with client_id = '{cid}'.", icon=":material/info:")


def main() -> None:
    theme.header("Client data")
    names = companies()
    c1, c2 = st.columns([2, 1], vertical_alignment="bottom")
    with c1:
        cid = st.selectbox("Company", list(names), format_func=lambda c: f"{names[c]} ({c})", key="data_client")
    with c2:
        rep = REPORTS_DIR / "Mock_Data_Report.pdf"
        if rep.exists():
            st.download_button("Download mock data report (PDF)", rep.read_bytes(), file_name=rep.name,
                               mime="application/pdf", use_container_width=True, icon=":material/description:")
    st.write("")
    tab_json, tab_sql = st.tabs(["Extracted JSON", "Database rows"])
    with tab_json:
        json_tab(cid)
    with tab_sql:
        db_tab(cid)


main()
