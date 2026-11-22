"""Design tokens + CSS for the Streamlit UI. Shared with the PDF report (same hex values).

Direction: an underwriting desk, not a SaaS dashboard. Cool paper background, deep ink navy,
one brass rule as the signature, and status colours that read like reviewer stamps.

Type scale (used on every page, nothing else sets sizes):
  page title 1.85rem serif | section 1.12rem serif | body .95rem | meta .84rem | KPI value 1.45rem serif
"""
from __future__ import annotations

import html

import streamlit as st

from core.config import llm_available

APP_NAME = "DD Autofill"
APP_TAGLINE = "Due diligence forms for US commercial insurance"
APP_VERSION = "POC v0.1, November 2026"

INK = "#14233C"
PAPER = "#F3F5F8"
SURFACE = "#FFFFFF"
RULE = "#D5DBE3"
MUTED = "#5B6676"
BRASS = "#A07C2C"
SIDEBAR_TEXT = "#DCE3EC"

STATUS = {
    "Filled":   {"fg": "#1F6B45", "bg": "#E3F1E9"},
    "Review":   {"fg": "#8A5A0B", "bg": "#FBF0D9"},
    "Missing":  {"fg": "#9C2F2F", "bg": "#F8E2E2"},
    "Unmapped": {"fg": "#4E5968", "bg": "#E6E9EE"},
    "Manual":   {"fg": "#4B3F7A", "bg": "#ECE8F6"},
}
SOURCE = {"JSON": "#1F5F8B", "DB": "#2F6B4F", "User": "#8A5A0B", "-": "#7A8494"}

# Shield with a check: the app mark, drawn inline so it needs no asset
MARK_SVG = (
    '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">'
    f'<path d="M12 2.5 4.5 5.4v6.1c0 4.6 3.1 8.6 7.5 10 4.4-1.4 7.5-5.4 7.5-10V5.4L12 2.5Z" fill="{INK}"/>'
    f'<path d="m8.4 12.2 2.5 2.5 4.9-5.2" fill="none" stroke="{BRASS}" stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round"/></svg>'
)

RAIL = 64          # collapsed sidebar width (px)
MENU = 210         # expanded sidebar width (px)

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=Source+Serif+4:opsz,wght@8..60,600;8..60,700&display=swap');

/* ---------- base type ---------- */
html, body, .stApp, [data-testid="stMarkdownContainer"], button, input, textarea, select {{
  font-family: 'IBM Plex Sans', 'Segoe UI', system-ui, sans-serif;
}}
.stApp {{ background: {PAPER}; }}
[data-testid="stMain"] [data-testid="stMarkdownContainer"] p,
[data-testid="stMain"] [data-testid="stMarkdownContainer"] li {{ font-size: .95rem; }}
[data-testid="stMain"] label p, [data-testid="stWidgetLabel"] p {{ font-size: .9rem !important; }}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {{ font-size: .84rem !important; color: {MUTED}; }}
[data-testid="stTab"] p {{ font-size: .92rem !important; font-weight: 500; }}
h1, h2, h3, h4, h5 {{ font-family: 'Source Serif 4', Georgia, serif !important; color: {INK}; letter-spacing: -0.01em; }}

/* ---------- layout ---------- */
[data-testid="stHeader"] {{ background: transparent; height: 0 !important; z-index: 1000001; }}
[data-testid="stMain"] .block-container {{ padding: 0 2.25rem 0 2.25rem; max-width: none; }}

/* ---------- app header ---------- */
.dd-appbar {{ display: flex; align-items: center; justify-content: space-between; gap: 1rem;
  margin: -1rem -2.25rem 1.6rem -2.25rem; padding: .85rem 2.25rem; background: {SURFACE};
  border-bottom: 1px solid {RULE}; box-shadow: inset 0 -3px 0 -1px {PAPER}; }}
.dd-brand {{ display: flex; align-items: center; gap: .6rem; min-width: 0; }}
.dd-brand .name {{ font-family: 'Source Serif 4', Georgia, serif; font-weight: 700; font-size: 1.3rem;
  color: {INK}; letter-spacing: -0.01em; white-space: nowrap; }}
.dd-brand .tagline {{ color: {MUTED}; font-size: .84rem; padding-left: .75rem; margin-left: .15rem;
  border-left: 1px solid {RULE}; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.dd-appbar .right {{ display: flex; align-items: center; gap: .6rem; flex-shrink: 0; }}
.dd-pill {{ font-size: .78rem; font-weight: 500; padding: .2rem .55rem; border-radius: 999px;
  border: 1px solid {RULE}; color: {MUTED}; background: {PAPER}; white-space: nowrap; }}
.dd-pill.demo {{ color: #8A5A0B; background: #FBF0D9; border-color: #EBD3A2; }}
.dd-user {{ display: flex; align-items: center; gap: .45rem; font-size: .84rem; color: {INK}; }}
.dd-avatar {{ width: 28px; height: 28px; border-radius: 50%; background: {INK}; color: #fff;
  display: grid; place-items: center; font-size: .72rem; font-weight: 600; }}

/* ---------- page header ---------- */
.dd-head h1 {{ font-size: 1.85rem; margin: 0; padding: 0; line-height: 1.2; }}
.dd-head p {{ color: {MUTED}; margin: .25rem 0 0 0; max-width: 72ch; font-size: .95rem; }}
.dd-rule {{ height: 3px; width: 56px; background: {BRASS}; margin: .8rem 0 1.4rem 0; border-radius: 2px; }}
.dd-section {{ font-family: 'Source Serif 4', Georgia, serif; font-size: 1.12rem; font-weight: 600;
  color: {INK}; margin: .4rem 0 .55rem 0; line-height: 1.3; }}

/* ---------- footer ---------- */
.dd-footer {{ display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: .5rem 1.5rem;
  margin: 3rem -2.25rem 0 -2.25rem; padding: 1rem 2.25rem 1.1rem; border-top: 1px solid {RULE};
  background: {SURFACE}; color: {MUTED}; font-size: .8rem; }}
.dd-footer .brand {{ display: flex; align-items: center; gap: .45rem; color: {INK}; font-weight: 600; }}
.dd-footer .brand svg {{ width: 16px; height: 16px; }}
.dd-footer .links {{ display: flex; gap: 1.2rem; flex-wrap: wrap; }}

/* ---------- components ---------- */
.dd-chips {{ display: flex; flex-wrap: wrap; gap: .5rem; margin: .2rem 0 .6rem 0; }}
.dd-chip {{ display: inline-flex; align-items: baseline; gap: .45rem; padding: .32rem .7rem;
  border-radius: 6px; font-size: .88rem; font-weight: 500; }}
.dd-chip b {{ font-size: 1.1rem; font-weight: 600; font-variant-numeric: tabular-nums; }}
.dd-bar {{ display: flex; height: 8px; border-radius: 4px; overflow: hidden; background: {RULE}; margin-bottom: .4rem; }}
.dd-meta {{ color: {MUTED}; font-size: .84rem; line-height: 1.45; }}
.dd-panel {{ background: {SURFACE}; border: 1px solid {RULE}; border-radius: 10px; padding: 1rem 1.1rem; font-size: .95rem; }}
.dd-kpis {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: .75rem; margin: .2rem 0 1.2rem 0; }}
.dd-kpi {{ background: {SURFACE}; border: 1px solid {RULE}; border-left: 3px solid {INK};
  border-radius: 8px; padding: .7rem .9rem; display: flex; flex-direction: column; justify-content: space-between; min-height: 82px; }}
.dd-kpi .v {{ font-family: 'Source Serif 4', Georgia, serif; font-size: 1.45rem; color: {INK}; font-weight: 600;
  font-variant-numeric: tabular-nums; line-height: 1.2; }}
.dd-kpi .l {{ color: {MUTED}; font-size: .8rem; margin-top: .25rem; }}
.dd-tag {{ display: inline-block; padding: .05rem .45rem; border-radius: 4px; font-size: .78rem;
  font-weight: 600; color: #fff; }}
.stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"] {{
  background: {INK}; border-color: {INK}; }}
.stButton > button:focus-visible, .stDownloadButton > button:focus-visible {{
  outline: 3px solid {BRASS}; outline-offset: 2px; }}
[data-testid="stImage"] img {{ border: 1px solid {RULE}; border-radius: 4px; box-shadow: 0 1px 2px rgba(20,35,60,.08); }}
footer {{ visibility: hidden; }}

/* ---------- PDF viewer: a whole page fits the screen height ---------- */
[class*="st-key-pdffit_"] {{ background: #E8ECF1; border: 1px solid {RULE}; border-radius: 8px; padding: .75rem; }}
[class*="st-key-pdffit_"] [data-testid="stFullScreenFrame"] > div,
[class*="st-key-pdffit_"] [data-testid="stImage"],
[class*="st-key-pdffit_"] [data-testid="stImageContainer"] {{ display: flex; justify-content: center; width: 100%; }}
[class*="st-key-pdffit_"] img {{ max-height: calc(100vh - 260px); width: auto !important;
  max-width: 100%; object-fit: contain; margin: 0 auto; }}
[role="dialog"] [class*="st-key-pdffit_"] img {{ max-height: calc(100vh - 300px); }}
[class*="st-key-pdfscroll_"] {{ background: #E8ECF1; border-radius: 8px; }}
[class*="st-key-pdfscroll_"] [data-testid="stFullScreenFrame"] > div {{ display: flex; justify-content: center; }}
[class*="st-key-pdfscroll_"] [data-testid="stImage"] {{ max-width: 860px; width: 100%; }}

/* ---------- Template setup: upload card and template grid ---------- */
[class*="st-key-uploadcard"], [class*="st-key-tplgrid"] {{ background: {SURFACE}; border: 1px solid {RULE};
  border-radius: 10px; }}
[class*="st-key-uploadcard"] {{ padding: .9rem 1.1rem .4rem; }}
[class*="st-key-uploadcard"] [data-testid="stFileUploaderDropzone"] {{ box-sizing: border-box; height: 40px;
  min-height: 40px; padding: 0 5px; display: flex; align-items: center; border-radius: 8px; }}
[class*="st-key-uploadcard"] [data-testid="stFileUploaderDropzone"] button {{ height: 30px; min-height: 30px;
  padding: 0 .7rem; font-size: .85rem; }}
[class*="st-key-uploadcard"] [data-testid="stFormSubmitButton"] button {{ height: 40px; min-height: 40px;
  border-radius: 8px; }}
[class*="st-key-uploadcard"] [data-testid="stFileUploaderFile"] {{ padding: .25rem 0 0; }}
/* attached file: a compact one-line chip that stays inside the 40px box */
[class*="st-key-uploadcard"] [data-testid="stFileUploaderDropzone"] > div {{ width: 100%; min-width: 0; }}
[class*="st-key-uploadcard"] [data-testid="stFileChips"] {{ padding: 0; margin: 0; min-width: 0; flex: 1 1 auto; }}
[class*="st-key-uploadcard"] [data-testid="stFileChips"] > div,
[class*="st-key-uploadcard"] [data-testid="stFileChips"] > div > div {{ padding: 0; margin: 0; gap: .35rem;
  align-items: center; flex-wrap: nowrap; min-width: 0; }}
[class*="st-key-uploadcard"] [data-testid="stFileChip"] {{ position: relative; height: 30px; min-height: 0;
  max-width: 100%; padding: 0 .25rem 0 .35rem; gap: .4rem; align-items: center; border-radius: 6px;
  background: {SURFACE}; border: 1px solid {RULE}; overflow: hidden; box-shadow: none; }}
[class*="st-key-uploadcard"] [data-testid="stFileChip"] > div:first-child {{ width: 20px; height: 20px; min-width: 20px;
  border-radius: 50%; display: grid; place-items: center; padding: 0; }}
[class*="st-key-uploadcard"] [data-testid="stFileChip"] > div:first-child svg {{ width: 14px; height: 14px; }}
[class*="st-key-uploadcard"] [data-testid="stFileChip"] > div:nth-child(2) {{ display: flex; flex-direction: row;
  align-items: baseline; gap: .45rem; min-width: 0; }}
[class*="st-key-uploadcard"] [data-testid="stFileChipName"] {{ font-size: .82rem; line-height: 1; color: {INK};
  max-width: 220px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
[class*="st-key-uploadcard"] [data-testid="stFileChip"] > div:nth-child(2) > div:last-child {{ font-size: .72rem;
  line-height: 1; color: {MUTED}; white-space: nowrap; }}
[class*="st-key-uploadcard"] [data-testid="stFileChipDeleteBtn"] button {{ width: 22px; height: 22px; min-height: 0;
  padding: 0; }}
[class*="st-key-uploadcard"] [data-testid="stFileChipDeleteBtn"] svg {{ width: 15px; height: 15px; }}
/* while uploading: spinner icon, "Uploading" label and a moving progress strip along the bottom */
[class*="st-key-uploadcard"] [data-testid="stFileChip"]:has([data-testid="stFileChipIconSpinner"]) > div:nth-child(2) > div:last-child {{
  font-size: 0; }}
[class*="st-key-uploadcard"] [data-testid="stFileChip"]:has([data-testid="stFileChipIconSpinner"]) > div:nth-child(2) > div:last-child::after {{
  content: "Uploading"; font-size: .72rem; color: {MUTED}; }}
[class*="st-key-uploadcard"] [data-testid="stFileChip"]:has([data-testid="stFileChipIconSpinner"])::after {{
  content: ""; position: absolute; left: 0; bottom: 0; height: 3px; width: 40%; border-radius: 2px;
  background: {BRASS}; animation: dd-upload 1s ease-in-out infinite; }}
@keyframes dd-upload {{ 0% {{ left: -40%; }} 100% {{ left: 100%; }} }}
@media (prefers-reduced-motion: reduce) {{
  [class*="st-key-uploadcard"] [data-testid="stFileChip"]:has([data-testid="stFileChipIconSpinner"])::after {{
    animation: none; left: 0; width: 100%; opacity: .6; }} }}
/* upload finished: the file icon becomes a green tick */
[class*="st-key-uploadcard"] [data-testid="stFileChip"]:not(:has([data-testid="stFileChipIconSpinner"])) > div:first-child {{
  background: #1F6B45; }}
[class*="st-key-uploadcard"] [data-testid="stFileChip"]:not(:has([data-testid="stFileChipIconSpinner"])) > div:first-child svg {{
  display: none; }}
[class*="st-key-uploadcard"] [data-testid="stFileChip"]:not(:has([data-testid="stFileChipIconSpinner"])) > div:first-child::after {{
  content: ""; width: 9px; height: 5px; border: 2px solid #fff; border-top: 0; border-right: 0;
  transform: translateY(-1px) rotate(-45deg); }}
[class*="st-key-uploadcard"] [data-testid="stFileChip"]:not(:has([data-testid="stFileChipIconSpinner"])) {{
  border-color: #B9DCC6; }}
[class*="st-key-uploadcard"] [data-testid="stFileUploaderDropzoneInstructions"] {{ display: none; }}
[class*="st-key-tplgrid"] {{ padding: 0 0 .15rem; gap: 0; overflow: hidden; }}
[class*="st-key-tplhead"] {{ padding: 0 1rem; background: {PAPER}; }}
[class*="st-key-tplhead"] [data-testid="stElementContainer"],
[class*="st-key-tplhead"] [data-testid="stMarkdown"],
[class*="st-key-tplhead"] [data-testid="stMarkdownContainer"] {{ margin: 0 !important; }}
.dd-grid-head {{ font-size: .8rem; font-weight: 600; color: {MUTED}; line-height: 1.2; margin: 0;
  height: 2.6rem; display: flex; align-items: center; }}
.dd-grid-head.center {{ justify-content: center; }}
.dd-cell.center {{ text-align: center; }}
[class*="st-key-tplrow_"] {{ padding: .5rem 1rem; border-top: 1px solid {RULE}; }}
[class*="st-key-tplrow_"] [data-testid="stMarkdownContainer"] p, .dd-cell {{ margin: 0; }}
.dd-cell {{ font-size: .9rem; color: {INK}; line-height: 1.35; }}
.dd-cell code {{ font-size: .84rem; color: {INK}; background: {PAPER}; padding: .1rem .4rem; border-radius: 4px; }}
[class*="st-key-tplrow_"] [data-testid="stColumn"] {{ display: flex; flex-direction: column; justify-content: center; }}
[class*="st-key-tplrow_"] [data-testid="stColumn"] [data-testid="stElementContainer"],
[class*="st-key-tplrow_"] [data-testid="stColumn"] [data-testid="stMarkdown"],
[class*="st-key-tplrow_"] [data-testid="stColumn"] [data-testid="stMarkdownContainer"] {{ margin: 0 !important; }}
[class*="st-key-actions_"] {{ justify-content: center; align-items: center; flex-wrap: nowrap; }}
[class*="st-key-actions_"] [data-testid="stElementContainer"] {{ width: auto !important; flex: 0 0 auto; }}
[class*="st-key-prev_"] button, [class*="st-key-del_"] button, [class*="st-key-dl_"] button {{ width: 2.25rem; height: 2.25rem; min-height: 0;
  padding: 0; display: inline-flex; align-items: center; justify-content: center; }}
[class*="st-key-del_"] button:hover {{ color: #9C2F2F; border-color: #9C2F2F; }}
[class*="st-key-tpl_prev"] button, [class*="st-key-tpl_next"] button {{ min-height: 2.25rem; }}

/* ---------- status chips that filter the grid ---------- */
[class*="st-key-chip_"] button {{ border: 1px solid transparent; border-radius: 6px; min-height: 2.15rem;
  padding: .2rem .55rem; font-weight: 500; white-space: nowrap; }}
[class*="st-key-chip_"] button p {{ font-size: .86rem !important; font-variant-numeric: tabular-nums; }}
{{CHIP_COLORS}}
[class*="st-key-chip_"][class*="_on"] button {{ border-color: currentColor; box-shadow: inset 0 0 0 1px currentColor; }}
[class*="st-key-chip_"][class*="_off"] button:hover {{ filter: brightness(.96); border-color: currentColor; }}

/* control rows above the grid and the PDF share one height so both panels start on the same line */
[class*="st-key-panelbar_"] {{ min-height: 2.6rem; display: flex; align-items: center; }}
[class*="st-key-panelbar_"] > div {{ width: 100%; }}

/* scroll-only PDF view: window sized to the screen, pages centred */
[class*="st-key-pdfonly_"] {{ height: calc(100vh - 210px) !important; max-height: calc(100vh - 210px) !important;
  background: #E8ECF1; border-radius: 8px; }}
[class*="st-key-pdfonly_"] [data-testid="stFullScreenFrame"] > div {{ display: flex; justify-content: center; width: 100%; }}
[class*="st-key-pdfonly_"] [data-testid="stImage"] {{ width: 100%; max-width: 860px; margin: 0 auto; }}
[class*="st-key-pdfonly_"] [data-testid="stImage"] img {{ width: 100% !important; height: auto; }}
/* Fill page: the scroll window fills the screen and every page is scaled so the whole page is visible */
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-pdfonly_filltpl"]),
[class*="st-key-pdfonly_filltpl"] {{ height: max(560px, calc(100vh - 190px)) !important;
  max-height: max(560px, calc(100vh - 190px)) !important; }}
[class*="st-key-pdfonly_filltpl"] [data-testid="stImage"] {{ max-width: none; }}
[class*="st-key-pdfonly_filltpl"] [data-testid="stImage"] img {{ width: min(100%, 780px) !important;
  max-width: 100%; height: auto; max-height: none; margin: 0 auto; display: block; }}
/* template preview dialog: same window sizing as before, now applied to the wrapper too */
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-pdfonly_tplprev"]) {{ height: calc(100vh - 210px) !important; }}
/* filled PDF, scroll view: each page fits the panel height */
[class*="st-key-pdfscroll_"] [data-testid="stImage"] img {{ width: auto !important; max-width: 100%;
  max-height: 580px; margin: 0 auto; display: block; }}

/* template format badges (PDF / Word / Web form) */
.dd-fmt {{ flex-shrink: 0; font-size: .74rem; font-weight: 600; border-radius: 4px; padding: .1rem .45rem;
  white-space: nowrap; }}
.dd-fmt.fmt-pdf {{ background: #F8E2E2; color: #9C2F2F; }}
.dd-fmt.fmt-docx {{ background: #E2EEF7; color: #1F5F8B; }}
.dd-fmt.fmt-html {{ background: #ECE8F6; color: #4B3F7A; }}
[class*="st-key-webform_frame"] iframe {{ border: 1px solid {RULE}; border-radius: 8px; background: #EEF1F5; }}

/* company shown beside the form picker */
.dd-company {{ display: flex; flex-direction: column; gap: .2rem; margin-bottom: 14px; }}
.dd-company .lbl {{ font-size: .9rem; color: {INK}; }}
.dd-company .val {{ display: flex; align-items: center; gap: .6rem; min-height: 2.5rem; padding: 0 .75rem;
  background: {PAPER}; border: 1px solid {RULE}; border-radius: 8px; font-size: .95rem; color: {INK};
  white-space: nowrap; overflow: hidden; }}
.dd-company .val b {{ overflow: hidden; text-overflow: ellipsis; font-weight: 600; }}
.dd-id {{ flex-shrink: 0; font-size: .78rem; font-weight: 600; color: {INK}; background: {SURFACE};
  border: 1px solid {RULE}; border-radius: 999px; padding: .1rem .55rem; letter-spacing: .02em; }}

/* ---------- toolbar row on the Fill page ---------- */
[class*="st-key-fillbar"] {{ background: {SURFACE}; border: 1px solid {RULE}; border-radius: 10px;
  padding: .85rem 1rem .9rem; margin-bottom: .3rem; }}

/* ---------- sidebar ---------- */
[data-testid="stSidebar"] {{ background: {INK}; }}
[data-testid="stSidebar"] * {{ color: {SIDEBAR_TEXT} !important; }}
[data-testid="stSidebarNavLink"] p {{ font-size: .92rem !important; }}
[data-testid="stSidebarNavLink"] {{ border-left: 3px solid transparent; }}
[data-testid="stSidebarNavLink"][aria-current="page"] {{
  background: rgba(255,255,255,.10); border-left: 3px solid #F2C14E; }}
[data-testid="stSidebarNavLink"][aria-current="page"] p,
[data-testid="stSidebarNavLink"][aria-current="page"] span {{ color: #FFFFFF !important; font-weight: 600; }}
[data-testid="stSidebarNavLink"]:hover {{ background: rgba(255,255,255,.06); }}
[data-testid="stSidebarNavSeparator"] {{ display: none; }}

/* expanded: a compact menu instead of Streamlit's 300px default */
[data-testid="stSidebar"][data-collapsed="false"] {{
  width: {MENU}px !important; min-width: {MENU}px !important; max-width: {MENU}px !important; }}
[data-testid="stSidebar"][data-collapsed="false"] > div {{ width: {MENU}px !important; }}
[data-testid="stSidebar"] [data-testid="stSidebarResizeHandle"] {{ display: none !important; }}
[data-testid="stSidebar"][data-collapsed="false"] [data-testid="stSidebarNavItems"] {{ padding: 0 .6rem; }}

/* collapsed: an icon rail instead of hiding the menu */
[data-testid="stSidebar"][data-collapsed="true"] {{
  transform: none !important; width: {RAIL}px !important; min-width: {RAIL}px !important;
  max-width: {RAIL}px !important; }}
[data-testid="stSidebar"][data-collapsed="true"] > div {{ width: {RAIL}px !important; overflow: visible; }}
[data-testid="stSidebar"][data-collapsed="true"] [data-testid="stSidebarContent"] {{ overflow: visible; }}
[data-testid="stSidebar"][data-collapsed="true"] [data-testid="stSidebarHeader"],
[data-testid="stSidebar"][data-collapsed="true"] [data-testid="stSidebarUserContent"],
[data-testid="stSidebar"][data-collapsed="true"] [data-testid="stSidebarResizeHandle"] {{ display: none !important; }}
[data-testid="stSidebar"][data-collapsed="true"] [data-testid="stSidebarNav"] {{ padding-top: 4.2rem; }}
[data-testid="stSidebar"][data-collapsed="true"] [data-testid="stSidebarNavItems"] {{ padding: 0 .55rem; }}
[data-testid="stSidebar"][data-collapsed="true"] [data-testid="stSidebarNavLink"] {{
  justify-content: center; padding: .6rem 0; position: relative; }}
[data-testid="stSidebar"][data-collapsed="true"] [data-testid="stSidebarNavLink"] > span:first-child {{ margin: 0; }}
[data-testid="stSidebar"][data-collapsed="true"] [data-testid="stSidebarNavLink"] span[label] {{ display: none; }}
[data-testid="stSidebar"][data-collapsed="true"] [data-testid="stSidebarNavLink"]:hover span[label],
[data-testid="stSidebar"][data-collapsed="true"] [data-testid="stSidebarNavLink"]:focus-visible span[label] {{
  display: block; position: absolute; left: calc(100% + 10px); top: 50%; transform: translateY(-50%);
  background: {INK}; padding: .3rem .6rem; border-radius: 6px; white-space: nowrap; z-index: 1000003;
  box-shadow: 0 4px 12px rgba(20,35,60,.25); }}
[data-testid="stExpandSidebarButton"] {{ position: fixed; left: 16px; top: 16px; z-index: 1000002; }}
[data-testid="stExpandSidebarButton"] span {{ color: {SIDEBAR_TEXT} !important; }}

@media (max-width: 760px) {{
  .dd-brand .tagline {{ display: none; }}
  [data-testid="stMain"] .block-container {{ padding: 0 1rem; }}
  .dd-appbar, .dd-footer {{ margin-left: -1rem; margin-right: -1rem; padding-left: 1rem; padding-right: 1rem; }}
}}
</style>
"""


CHIP_COLORS = "\n".join(
    f'[class*="st-key-chip_{k}_"] button {{ background: {v["bg"]}; color: {v["fg"]}; }}\n'
    f'[class*="st-key-chip_{k}_"] button p {{ color: {v["fg"]} !important; }}'
    for k, v in STATUS.items())
CSS = CSS.replace("{CHIP_COLORS}", CHIP_COLORS)


def apply() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def app_header() -> None:
    st.markdown(
        f'<div class="dd-appbar" role="banner">'
        f'<div class="dd-brand">{MARK_SVG}<span class="name">{APP_NAME}</span>'
        f'<span class="tagline">{html.escape(APP_TAGLINE)}</span></div>'
        f'<div class="right"><span class="dd-pill demo">Demo data</span></div></div>',
        unsafe_allow_html=True)


def app_footer() -> None:
    llm = "Semantic matching on" if llm_available() else "Semantic matching off"
    st.markdown(
        f'<div class="dd-footer" role="contentinfo">'
        f'<span class="brand">{MARK_SVG}{APP_NAME}<span style="font-weight:400;color:{MUTED}">'
        f'&nbsp;{APP_VERSION}</span></span>'
        f'<span>Demo data only. Every company, person and identifier is fictional.</span>'
        f'<span class="links"><span>Data matched on client ID</span><span>{llm}</span></span></div>',
        unsafe_allow_html=True)


def header(title: str, lede: str | None = None) -> None:
    lede_html = f"<p>{html.escape(lede)}</p>" if lede else ""
    st.markdown(f'<div class="dd-head"><h1>{html.escape(title)}</h1>{lede_html}</div>'
                f'<div class="dd-rule"></div>', unsafe_allow_html=True)


def section(title: str) -> None:
    st.markdown(f'<div class="dd-section">{html.escape(title)}</div>', unsafe_allow_html=True)


def status_strip(counts: dict[str, int]) -> None:
    total = sum(counts.values()) or 1
    chips = "".join(
        f'<span class="dd-chip" style="background:{STATUS[s]["bg"]};color:{STATUS[s]["fg"]}">'
        f'<b>{n}</b>{s}</span>' for s, n in counts.items())
    bar = "".join(f'<div style="width:{n / total * 100:.2f}%;background:{STATUS[s]["fg"]}"></div>'
                  for s, n in counts.items() if n)
    st.markdown(f'<div class="dd-chips">{chips}</div><div class="dd-bar">{bar}</div>', unsafe_allow_html=True)


def status_bar(counts: dict[str, int]) -> None:
    total = sum(counts.values()) or 1
    bar = "".join(f'<div style="width:{n / total * 100:.2f}%;background:{STATUS[s]["fg"]}"></div>'
                  for s, n in counts.items() if n)
    st.markdown(f'<div class="dd-bar" style="margin:.35rem 0 1rem">{bar}</div>', unsafe_allow_html=True)


def kpi(label: str, value: str) -> str:
    return (f'<div class="dd-kpi"><div class="v">{html.escape(value)}</div>'
            f'<div class="l">{html.escape(label)}</div></div>')


def kpi_row(items: list[tuple[str, str]]) -> None:
    """One CSS grid, so every card in the row shares the same height and edges."""
    st.markdown(f'<div class="dd-kpis">{"".join(kpi(l, v) for l, v in items)}</div>', unsafe_allow_html=True)


def tag(text: str, color: str) -> str:
    return f'<span class="dd-tag" style="background:{color}">{html.escape(text)}</span>'
