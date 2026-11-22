"""Build reports/Mock_Data_Report.pdf - the stakeholder-facing description of the demo data.

Statuses in the scenario section are produced by running the real fill engine, so the report
always matches what the demo shows.
"""
from __future__ import annotations

import re
from datetime import date

from reportlab.graphics.charts.barcharts import HorizontalBarChart, VerticalBarChart
from reportlab.graphics.shapes import Drawing, Line, Rect, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

from core import db, engine, registry
from core.catalog import flatten_json
from core.config import REPORTS_DIR
from scripts import mock_data as M
from core.catalog import DataError
from scripts.template_specs import NO_DATA_TEMPLATES, TEMPLATES
from ui.theme import BRASS, INK, MUTED, RULE, STATUS

C_INK, C_BRASS, C_MUTED, C_RULE = (colors.HexColor(x) for x in (INK, BRASS, MUTED, RULE))
C_PAPER = colors.HexColor("#F3F5F8")
C_BLUE = colors.HexColor("#1F5F8B")
W, H = letter
MARGIN = 0.75 * inch
CW = W - 2 * MARGIN

S = {
    "h1": ParagraphStyle("h1", fontName="Times-Bold", fontSize=22, leading=26, textColor=C_INK, spaceAfter=4),
    "h2": ParagraphStyle("h2", fontName="Times-Bold", fontSize=15, leading=19, textColor=C_INK,
                         spaceBefore=10, spaceAfter=6),
    "h3": ParagraphStyle("h3", fontName="Helvetica-Bold", fontSize=9.5, leading=12, textColor=C_INK,
                         spaceBefore=8, spaceAfter=4),
    "body": ParagraphStyle("body", fontName="Helvetica", fontSize=9.2, leading=13.4, textColor=colors.HexColor("#1C2533")),
    "small": ParagraphStyle("small", fontName="Helvetica", fontSize=7.8, leading=10, textColor=C_MUTED),
    "cell": ParagraphStyle("cell", fontName="Helvetica", fontSize=7.8, leading=9.6, alignment=TA_LEFT),
    "cellb": ParagraphStyle("cellb", fontName="Helvetica-Bold", fontSize=7.8, leading=9.6),
    "kpiv": ParagraphStyle("kpiv", fontName="Times-Bold", fontSize=14, leading=16, textColor=C_INK),
    "kpil": ParagraphStyle("kpil", fontName="Helvetica", fontSize=7.4, leading=9, textColor=C_MUTED),
}


_AMP = re.compile(r"&(?!amp;|lt;|gt;|quot;|#)")


def esc(text: str) -> str:
    return _AMP.sub("&amp;", text)


def P(text, style="body"):
    return Paragraph(esc(text), S[style])


def money(v):
    return "n/a" if v is None else f"${v / 1e6:,.1f}M"


def table(rows, widths, header=True, zebra=True, font=7.8):
    data = [[c if not isinstance(c, str) else Paragraph(esc(c), S["cellb" if header and i == 0 else "cell"])
             for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    st = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("FONTSIZE", (0, 0), (-1, -1), font),
          ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
          ("LINEBELOW", (0, 0), (-1, -1), 0.4, C_RULE)]
    if header:
        st += [("LINEBELOW", (0, 0), (-1, 0), 1.0, C_INK)]
    if zebra:
        for i in range(1 if header else 0, len(rows)):
            if i % 2 == 0:
                st.append(("BACKGROUND", (0, i), (-1, i), C_PAPER))
    t.setStyle(TableStyle(st))
    return t


def kpi_strip(items):
    cells = [[P(v, "kpiv") for _, v in items], [P(l, "kpil") for l, _ in items]]
    t = Table(cells, colWidths=[CW / len(items)] * len(items))
    t.setStyle(TableStyle([("LINEABOVE", (0, 0), (-1, 0), 2, C_INK), ("LEFTPADDING", (0, 0), (-1, -1), 6),
                           ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                           ("BOX", (0, 0), (-1, -1), 0.4, C_RULE)]))
    return t


# ------------------------------------------------------------------ charts
def loss_chart(cid):
    rows = [r for r in M.LOSS_RUNS if r[0] == cid]
    d = Drawing(CW * 0.47, 128)
    if not rows:
        d.add(String(0, 70, "No loss runs: this client does not bear or place risk directly.",
                     fontName="Helvetica", fontSize=8, fillColor=C_MUTED))
        return d
    c = VerticalBarChart()
    c.x, c.y, c.width, c.height = 30, 18, CW * 0.47 - 45, 92
    c.data = [[round(il / ep * 100, 1) for _, _, ep, il, _, _ in rows]]
    c.categoryAxis.categoryNames = [str(r[1]) for r in rows]
    c.valueAxis.valueMin, c.valueAxis.valueMax, c.valueAxis.valueStep = 0, 80, 20
    c.bars[0].fillColor = C_INK
    c.bars[0].strokeColor = None
    c.barWidth = 18
    c.valueAxis.labels.fontSize = c.categoryAxis.labels.fontSize = 7
    c.valueAxis.gridStrokeColor = C_RULE
    c.valueAxis.visibleGrid = True
    c.barLabelFormat = "%.1f%%"
    c.barLabels.fontSize = 7
    c.barLabels.nudge = 7
    d.add(c)
    y = 18 + 92 * 65 / 80
    d.add(Line(30, y, 30 + c.width, y, strokeColor=C_BRASS, strokeDashArray=[3, 2], strokeWidth=1))
    d.add(String(0, 118, "Loss ratio by accident year (dashed line: 65% target)", fontName="Helvetica-Bold", fontSize=8, fillColor=C_INK))
    return d


def carrier_chart(cid):
    rows = [r for r in M.CARRIER_RELATIONSHIPS if r[0] == cid]
    h = 30 + 18 * len(rows)
    d = Drawing(CW * 0.5, h + 14)
    c = HorizontalBarChart()
    c.x, c.y, c.width, c.height = 150, 8, CW * 0.5 - 185, h - 10
    c.data = [[r[4] for r in reversed(rows)]]
    c.categoryAxis.categoryNames = [(r[1][:30] + "…") if len(r[1]) > 31 else r[1] for r in reversed(rows)]
    c.valueAxis.valueMin, c.valueAxis.valueMax = 0, 60
    c.valueAxis.visible = False
    c.bars[0].fillColor = C_BLUE
    c.bars[0].strokeColor = None
    c.categoryAxis.labels.fontSize = 6.8
    c.categoryAxis.visibleAxis = False
    c.barLabelFormat = "%.0f%%"
    c.barLabels.fontSize = 6.8
    c.barLabels.nudge = 9
    d.add(c)
    d.add(String(0, h + 4, "Share of premium by carrier / reinsurer", fontName="Helvetica-Bold", fontSize=8,
                 fillColor=C_INK))
    return d


def lineage():
    d = Drawing(CW, 150)

    def box(x, y, w, h, title, sub, fill):
        d.add(Rect(x, y, w, h, fillColor=fill, strokeColor=None, rx=4, ry=4))
        d.add(String(x + 8, y + h - 15, title, fontName="Helvetica-Bold", fontSize=8.5, fillColor=colors.white))
        for i, line in enumerate(sub):
            d.add(String(x + 8, y + h - 28 - i * 10, line, fontName="Helvetica", fontSize=7,
                         fillColor=colors.HexColor("#DCE3EC")))

    def arrow(x1, y1, x2, y2):
        d.add(Line(x1, y1, x2, y2, strokeColor=C_MUTED, strokeWidth=1.1))
        d.add(Line(x2, y2, x2 - 5, y2 + 3, strokeColor=C_MUTED, strokeWidth=1.1))
        d.add(Line(x2, y2, x2 - 5, y2 - 3, strokeColor=C_MUTED, strokeWidth=1.1))

    bw = (CW - 3 * 26) / 4
    box(0, 86, bw, 54, "Client documents", ["Statutory statements,", "agreements, loss runs"], C_MUTED)
    box(0, 10, bw, 54, "Client database", ["11 tables keyed", "by client_id"], C_MUTED)
    box(bw + 26, 86, bw, 54, "Extracted JSON", ["value + confidence", "+ source page"], C_BLUE)
    box(2 * (bw + 26), 48, bw, 54, "Match and resolve", ["glossary, precedence,", "US formats, statuses"], C_INK)
    box(3 * (bw + 26), 48, bw, 54, "Filled PDF + review", ["Filled / Review /", "Missing / Manual"], C_BRASS)
    arrow(bw, 113, bw + 26, 113)
    arrow(2 * bw + 26, 113, 2 * (bw + 26), 85)
    arrow(bw, 37, 2 * (bw + 26), 65)
    arrow(3 * bw + 2 * 26, 75, 3 * (bw + 26), 75)
    return d


# ------------------------------------------------------------------ page furniture
def on_page(canvas, doc):
    canvas.saveState()
    if doc.page == 1:
        canvas.setFillColor(C_INK)
        canvas.rect(0, H - 3.1 * inch, W, 3.1 * inch, stroke=0, fill=1)
        canvas.setFillColor(C_BRASS)
        canvas.rect(MARGIN, H - 3.1 * inch - 5, 1.1 * inch, 5, stroke=0, fill=1)
    else:
        canvas.setStrokeColor(C_RULE)
        canvas.line(MARGIN, H - 0.55 * inch, W - MARGIN, H - 0.55 * inch)
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(C_MUTED)
        canvas.drawString(MARGIN, H - 0.48 * inch, "DD Autofill POC  |  Mock Data Report")
        canvas.drawRightString(W - MARGIN, H - 0.48 * inch, "Fictional data - not for external use")
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(C_MUTED)
    canvas.drawRightString(W - MARGIN, 0.45 * inch, f"Page {doc.page}")
    canvas.restoreState()


def cover():
    white = ParagraphStyle("w", parent=S["h1"], textColor=colors.white, fontSize=30, leading=34)
    sub = ParagraphStyle("ws", parent=S["body"], textColor=colors.HexColor("#DCE3EC"), fontSize=11.5, leading=16)
    out = [Spacer(1, 0.35 * inch), Paragraph("Mock Data Report", white),
           Paragraph("Due diligence auto-fill proof of concept for US commercial insurance", sub),
           Spacer(1, 1.55 * inch)]
    total_rows = sum(len(x) for x in (M.CLIENTS, M.ADDRESSES, M.CONTACTS, M.LICENSES, M.FINANCIALS, M.INSURANCE,
                                      M.PROGRAMS, M.LOSS_RUNS, M.CARRIER_RELATIONSHIPS, M.OWNERSHIP,
                                      M.DD_ASSESSMENTS))
    leaves = sum(len(flatten_json(doc)) for doc in M.EXTRACTED.values())
    out += [kpi_strip([("Fictional client companies", str(len(M.CLIENTS))), ("Fillable PDF forms", str(len(TEMPLATES))),
                       ("Database rows across 11 tables", f"{total_rows}"),
                       ("Extracted JSON data points", f"{leaves}")]),
            Spacer(1, 16),
            P(f"Prepared {date.today():%B %d, %Y} for the stakeholder demonstration on November 23, 2026.", "small"),
            Spacer(1, 10),
            P("<b>What this report covers.</b> The fictional insurance businesses behind the demo, the "
              "data held for each one (extracted JSON and database rows), the due diligence form each one "
              "fills, and the data situations deliberately built in to show how the system behaves when "
              "data is clean, conflicting, uncertain or missing."),
            Spacer(1, 8),
            P("<b>All data is fictional.</b> Company names, people, carriers, FEINs (00-000000N), NAIC codes "
              "(99xxx), licence numbers (MOCK-), phone numbers (555-01xx) and web domains (.example) are "
              "invented. Any resemblance to real organisations is coincidental."),
            PageBreak()]
    return out


def overview(results):
    out = [P("How the demo data fits together", "h1"),
           P("Each client is linked by a single key, <b>client_id</b>. A form is registered to one client; "
             "pressing Fill loads only that client's extracted JSON and only the database rows where "
             "client_id matches. A JSON file carrying a different client_id is refused before any value "
             "is read."),
           Spacer(1, 8), lineage(), Spacer(1, 6),
           P(f"The {len(M.CLIENTS)} clients", "h2")]
    rows = [["ID", "Client", "Business", "Form it fills (issuer)", "Fields", "Result of a fill"]]
    for spec in TEMPLATES:
        c = next(x for x in M.CLIENTS if x["client_id"] == spec["client_id"])
        r = results.get(spec["client_id"])
        k = r.counts() if r else None
        rows.append([c["client_id"], f"<b>{c['legal_name']}</b><br/>{c['hq_city']}",
                     f"{c['client_type']}<br/>{c['segment']}", f"{spec['name']}<br/>({spec['issuer']})",
                     str(len(r.fields)) if r else "-",
                     (f"{k['Filled']} filled, {k['Review']} review, {k['Missing']} missing, {k['Manual']} manual"
                      if k else "Template not registered")])
    out.append(table(rows, [0.45 * inch, 1.55 * inch, 1.45 * inch, 1.65 * inch, 0.5 * inch, 1.4 * inch]))
    out += [Spacer(1, 8),
            P("Every form uses its own naming style for the same facts (for example <i>Applicant_Legal_Name</i>, "
              "<i>Insured Name</i>, <i>Name of Agency</i>, <i>EntityName</i> and <i>Company</i>), so the demo shows "
              "auto-matching working across naming conventions rather than on one fixed schema.", "small"),
            P("Templates onboarded before their data", "h2"),
            P("These companies' forms are registered, but no extracted JSON or database rows exist for them "
              "yet. Fill form explains that there is no data instead of filling anything; once their JSON "
              "or database rows arrive with the same identifier, the same template fills with no setup."),
            Spacer(1, 4),
            table([["ID", "Company", "Form (issuer)", "Fields", "Result of a fill"]] +
                  [[t["client_id"], f"<b>{t['company_name']}</b>", f"{t['name']}<br/>({t['issuer']})",
                    str(sum(len(sec[1]) for sec in t["sections"])), "No data found: not filled"]
                   for t in NO_DATA_TEMPLATES],
                  [0.45 * inch, 1.9 * inch, 2.45 * inch, 0.5 * inch, 1.7 * inch]),
            P("Word and web form templates", "h2"),
            P("Besides fillable PDFs, a company can have one Word document (fields marked with {{placeholders}}) "
              "and one web form (HTML inputs). They are filled from the same JSON and database data."),
            Spacer(1, 4),
            table([["ID", "Company", "Template", "Type", "Fields"]] +
                  [[t.client_id, f"<b>{t.company_name}</b>", t.name, {"docx": "Word", "html": "Web form"}[t.format],
                    str(t.field_count)] for t in registry.list_templates() if t.format != "pdf"],
                  [0.45 * inch, 2.0 * inch, 2.75 * inch, 0.8 * inch, 0.5 * inch]),
            PageBreak()]
    return out


def client_profile(cid, result):
    c = next(x for x in M.CLIENTS if x["client_id"] == cid)
    spec = next(t for t in TEMPLATES if t["client_id"] == cid)
    fin = sorted([f for f in M.FINANCIALS if f[0] == cid], key=lambda r: r[1])
    last = fin[-1]
    dd = next(x for x in M.DD_ASSESSMENTS if x[0] == cid)
    doc = M.EXTRACTED.get(cid)
    vol = "Gross written premium" if c["client_type"].startswith(("Managing", "Regional")) else "Premium placed"
    out = [P(f"{c['legal_name']}", "h1"),
           P(f"{c['client_type']}, {c['hq_city']}. Client ID {cid}. Established {c['year_established']}. "
             f"{c['segment'][0].upper() + c['segment'][1:]}.", "small"), Spacer(1, 8),
           kpi_strip([(f"{vol}, FY{last[1]}", money(last[2])), (f"Revenue, FY{last[1]}", money(last[3])),
                      ("Employees", f"{c['employee_count']:,}"), ("Our overall risk rating", dd[6])]),
           Spacer(1, 6), P(dd[9] + f" Assessed by {dd[7]} on {dd[8]}."),
           P(("Source documents behind the extracted JSON: " + ", ".join(doc["source_documents"])) if doc else
             "No extracted JSON yet: every value for this company comes from the database.", "small")]

    progs = [p for p in M.PROGRAMS if p[0] == cid]
    rows = [["Program / practice", "Line of business", "Carrier", "Authority", "Premium", "3-yr LR"]]
    rows += [[p[1], p[2], p[3], p[4], money(p[5]), "n/a" if p[6] is None else f"{p[6]:.1f}%"] for p in progs]
    out += [P("Programs and practices", "h3"),
            table(rows, [1.6 * inch, 1.6 * inch, 1.55 * inch, 0.65 * inch, 0.8 * inch, 0.8 * inch])]

    charts = Table([[loss_chart(cid), carrier_chart(cid)]], colWidths=[CW * 0.48, CW * 0.52])
    charts.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    out += [Spacer(1, 6), charts]

    scores = [["Area", "Financial strength", "Underwriting controls", "Claims handling", "Compliance",
               "Cyber and IT"], ["Score (of 5)", *[f"{s:.1f}" for s in dd[1:6]]]]
    fy = [["Fiscal year", *[str(f[1]) for f in fin]],
          [vol, *[money(f[2]) for f in fin]], ["Revenue", *[money(f[3]) for f in fin]],
          ["Net income", *[money(f[5]) for f in fin]]]
    out += [KeepTogether([P("Financial history (database)", "h3"),
                          table(fy, [1.9 * inch] + [1.2 * inch] * len(fin), zebra=False)]),
            KeepTogether([P("Our due diligence assessment (database)", "h3"),
                          table(scores, [1.2 * inch] + [1.1 * inch] * 5, zebra=False)])]

    if result is None:
        out += [P(f"What happens when the {spec['name']} is filled", "h3"),
                P("This company's template is not registered at the moment, so it was not filled for this report."),
                PageBreak()]
        return out
    flagged = [f for f in result.fields if f.status in ("Review", "Missing")]
    rows = [["Form field", "Status", "Why"]]
    rows += [[f.label or f.name,
              f'<font color="{STATUS[f.status]["fg"]}"><b>{f.status}</b></font>', f.note] for f in flagged]
    out += [P(f"What happens when the {spec['name']} is filled", "h3")]
    if flagged:
        out.append(table(rows, [1.7 * inch, 0.65 * inch, CW - 2.35 * inch]))
    else:
        out.append(P(f"All {sum(1 for f in result.fields if f.status == 'Filled')} mapped fields fill cleanly "
                     "from agreeing JSON and database values; signature and attestation fields are left for a person."))
    out.append(PageBreak())
    return out


SCENARIOS = [
    ("Clean fill", "C001", "Every mapped field filled from agreeing JSON and database values.", "Filled"),
    ("JSON and database disagree", "C002", "Partnership phone (601) 555-0147 in the onboarding letter vs "
     "(601) 555-0142 in the database; database wins for contact data. Premium $214.5M (annual statement) vs "
     "$212.0M (database); the document wins for financial facts.", "Review"),
    ("Approximate amount", "C002", '"approx $96M" surplus is written as $96,000,000.00 but flagged.', "Review"),
    ("Value is not a form option", "C002", '"Excellent" is an AM Best category, not a rating; the database '
     'rating A- is used and the fallback is flagged.', "Review"),
    ("Low extraction confidence", "C003", "E&O limit read at confidence 0.64, below the 0.80 threshold.", "Review"),
    ("Format conversion", "C003", '"March 3, 2024"-style dates to MM/DD/YYYY, "Texas" to TX, '
     '"214.555.0142" to (214) 555-0142, "$12.4M" to $12,400,000.00.', "Filled"),
    ("Value only in one source", "C004", "Counterparty rating exists only in the JSON; FEIN only in the "
     "database.", "Filled"),
    ("Fuzzy field-name match", "C004", '"YrsInBusiness" and "KeyContactEmailAddr" match their data only by '
     'similarity, so the values are filled but flagged for a person to confirm.', "Review"),
    ("Ambiguous date", "C004", '"04/05/2019" could be April 5 or May 4; read as MM/DD and flagged.', "Review"),
    ("Ambiguous yes/no", "C005", 'Pending litigation "Under review - see disclosure schedule" is not a yes '
     'or no, so the box is left blank and flagged.', "Review"),
    ("Missing data", "C005", "Top-10 client concentration and non-compete agreements have no value in "
     "either source.", "Missing"),
    ("Premium conflict", "C006", "Program premium $72.9M in the reviewed financials vs $72.4M in the database; "
     "the document value is kept and flagged.", "Review"),
    ("Value missing from the document", "C007", "Policyholder surplus was not extracted; the database figure "
     "($184M) fills the field.", "Filled"),
    ("Low confidence, catastrophe retention", "C007", "Cat retention read at confidence 0.69.", "Review"),
    ("Unanswered question", "C008", "Domiciles served has no answer in either source.", "Missing"),
    ("N/A on a yes/no question", "C009", 'Pending litigation "N/A" is not a yes or no, so the box is left '
     "blank.", "Review"),
    ("Approximate count", "C009", '"approx 38" average days to close is filled as 38 and flagged.', "Review"),
    ("Database only", "C010", "No extracted JSON yet; 19 fields fill from database rows alone.", "Filled"),
    ("No matching data", "C010", "Automated collections and regulator consent exist in neither source and "
     "match nothing.", "Unmapped"),
    ("Low confidence, chart figure", "C011", "Written premium read from an investor chart at confidence 0.72.",
     "Review"),
    ("Section-coded field names", "C012", 'Names like "S1_LegalName" and "S4_SLLicenseNumber" match after the '
     "section code is ignored; clean fill.", "Filled"),
    ("Template onboarded before data", "C013, C014", "Forms registered with an identifier that has no JSON or "
     "database rows yet; Fill form reports that there is no data and fills nothing.", "No data found"),
    ("Signature and attestation", "All", "Marked manual; never auto-filled.", "Manual"),
]


def scenarios():
    rows = [["Situation", "Client", "What the data contains", "Expected status"]]
    rows += [[a, b, c, f'<font color="{STATUS.get(d, {"fg": MUTED})["fg"]}"><b>{d}</b></font>']
             for a, b, c, d in SCENARIOS]
    return [P("Data situations built into the demo", "h1"),
            P("Each situation below is present in the mock data on purpose. The automated tests fill every "
              "forms and check that every one produces the status shown."), Spacer(1, 6),
            table(rows, [1.45 * inch, 0.5 * inch, 3.75 * inch, 1.3 * inch]), PageBreak()]


TABLE_DOCS = [
    ("client", "Master record: legal and DBA name, FEIN, entity type, domicile, website, establishment date, "
               "employees, NAIC code, ownership structure."),
    ("client_address", "Mailing and physical addresses."),
    ("client_contact", "Primary, CFO, compliance and claims contacts with title, phone and e-mail."),
    ("client_license", "Resident and non-resident licences with number and expiry date."),
    ("client_financials", "FY2023 to FY2025 premium, revenue, EBITDA, net income, AM Best rating, surplus, "
                          "combined ratio."),
    ("client_insurance", "The client's own E&O, cyber, D&O, crime and fidelity cover with limits."),
    ("client_program", "Programs or practices: line of business, carrier, binding authority, premium, "
                       "3-year loss ratio."),
    ("client_loss_run", "Accident-year earned premium, incurred losses, loss ratio, claim counts, large losses."),
    ("client_carrier_relationship", "Carrier or reinsurer panel with AM Best rating, tenure and share."),
    ("client_ownership", "Owners, percentage held and private-equity flag."),
    ("client_lending", "Premium finance book: loans outstanding, default rate, contracts financed."),
    ("client_dd_assessment", "Our analysts' scores (financial, underwriting, claims, compliance, cyber) and "
                             "overall risk rating."),
]


def dictionary():
    rows = [["Table", "Rows", "What it holds"]]
    for name, desc in TABLE_DOCS:
        rows.append([f"<b>{name}</b>", str(len(db.client_rows_all(name))), desc])
    jrows = [["Client", "JSON sections (names differ on purpose)", "Data points", "Lowest confidence"]]
    for cid, doc in M.EXTRACTED.items():
        leaves = flatten_json(doc)
        confs = [e.confidence for e in leaves if e.confidence is not None and e.value is not None]
        sections = [k for k in doc if k not in ("client_id", "client_name", "extracted_at", "source_documents")]
        jrows.append([cid, ", ".join(sections), str(len(leaves)), f"{min(confs):.2f}" if confs else "n/a"])
    return [P("Data dictionary", "h1"), P("Database (SQLite in the demo; SQL Server or PostgreSQL in production)", "h2"),
            table(rows, [1.8 * inch, 0.5 * inch, 4.7 * inch]), Spacer(1, 6),
            P("Extracted JSON (one document per client)", "h2"),
            P("Every leaf is either a plain value or <i>{value, confidence, source_ref}</i>, where source_ref "
              "points at the document page the value came from. client_id is mandatory."),
            Spacer(1, 4), table(jrows, [0.6 * inch, 4.2 * inch, 0.9 * inch, 1.3 * inch])]


def build(path=None):
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = path or REPORTS_DIR / "Mock_Data_Report.pdf"
    results = {}
    for t in registry.list_templates():
        try:
            results[t.client_id] = engine.fill(t.template_id, log=False)
        except DataError:
            continue                    # onboarded before its data: listed separately, not filled
    doc = SimpleDocTemplate(str(path), pagesize=letter, leftMargin=MARGIN, rightMargin=MARGIN,
                            topMargin=0.8 * inch, bottomMargin=0.7 * inch,
                            title="DD Autofill - Mock Data Report", author="DD Autofill POC")
    story = cover() + overview(results)
    for spec in TEMPLATES:
        story += client_profile(spec["client_id"], results.get(spec["client_id"]))
    story += scenarios() + dictionary()
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    return path


if __name__ == "__main__":
    print("built", build())
