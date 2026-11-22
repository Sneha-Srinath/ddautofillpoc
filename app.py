"""DD Autofill - Streamlit entry point. Run:  streamlit run app.py"""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ui import theme  # noqa: E402

st.set_page_config(page_title=theme.APP_NAME, page_icon=":material/verified_user:", layout="wide")
theme.apply()


@st.cache_resource(show_spinner=False)
def _warm_up() -> bool:
    """Load parsers and the PDF engine once per server so the first Fill stays under 3 s."""
    from core import convert, registry
    from core.catalog import build_catalog
    convert.to_date("March 3, 2024"); convert.to_date("2024")
    for t in registry.list_templates()[:1]:
        build_catalog(t.client_id)
    return True


_warm_up()

nav = st.navigation([
    st.Page("views/fill.py", title="Fill template", icon=":material/edit_document:", default=True),
    st.Page("views/setup.py", title="Template setup", icon=":material/tune:"),
    st.Page("views/data.py", title="Data", icon=":material/database:"),
    st.Page("views/audit.py", title="Audit", icon=":material/history:"),
])

theme.app_header()
nav.run()          # pages return early instead of calling st.stop(), so the footer always renders
theme.app_footer()
