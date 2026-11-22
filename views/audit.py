"""Audit page (FR-27)."""
from __future__ import annotations

import streamlit as st

from core import audit
from ui import theme


def main() -> None:
    theme.header("Audit log", "Every fill, edit and download, newest first, with the template and mapping "
                              "version used and a fingerprint of the input data.")

    df = audit.entries()
    if df.empty:
        st.info("Nothing has been filled yet. Fill a form and it will be recorded here.")
        return

    theme.kpi_row([("Fills recorded", str(len(df))), ("Clients", str(df["client_id"].nunique())),
                   ("Fills with user edits", str((df["edited_fields"].fillna("") != "").sum())),
                   ("Median fill time", f"{int(df['elapsed_ms'].median())} ms")])
    st.dataframe(
        df.rename(columns={"ts": "Time", "user": "User", "action": "Action", "template_id": "Template",
                           "template_version": "Template v", "mapping_version": "Mapping v", "client_id": "Client",
                           "filled": "Filled", "review": "Review", "missing": "Missing", "unmapped": "Unmapped",
                           "manual": "Manual", "edited_fields": "Edited fields", "output_file": "Output file",
                           "input_hash": "Input hash", "elapsed_ms": "ms"}).drop(columns=["id"]),
        hide_index=True, use_container_width=True, height=min(560, 38 + 35 * len(df)))


main()
