"""Generate the demo Word (.docx) templates with {{placeholders}}."""
from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]

ENTITY = "Entity Type: Limited Liability Company | Corporation | Partnership | Mutual Company"
AUTHORITY = "Binding Authority: Full | Limited | Referral Only"

DOCX_TEMPLATES = [
    {
        "client_id": "C001", "company_name": "Harbor Point Insurance Group, LLC",
        "name": "Program Administrator Annual Review",
        "file": "templates/C001_Program_Administrator_Annual_Review.docx",
        "issuer": "Granite Shield Casualty Co.", "ref": "GSC-PAR-2027", "color": "1B365D",
        "intro": ("Granite Shield Casualty Co. reviews each program administrator holding delegated authority "
                  "once a year. Please confirm the details below and return the signed review."),
        "sections": [
            ("Program administrator", [("Legal entity name", "Legal Entity Name"), ("FEIN", "FEIN"),
                                       ("Date established", "Date Established"),
                                       ("State of domicile", "State of Domicile"), ("Entity type", ENTITY)]),
            ("Mailing address", [("Street", "Mailing Address"), ("City", "City"), ("State", "State"),
                                 ("ZIP", "Zip Code")]),
            ("Primary contact", [("Name", "Contact Person"), ("Title", "Contact Title"),
                                 ("Telephone", "Telephone"), ("E-mail", "E-mail Address")]),
            ("Program results", [("Gross written premium", "Gross Written Premium"),
                                 ("Three-year loss ratio", "Three Year Loss Ratio"),
                                 ("Active programs", "Number of Active Programs"),
                                 ("Lines of business", "Lines of Business Written"),
                                 ("E&O limit", "E&O Limit"), ("Binding authority", AUTHORITY)]),
            ("Controls", [("Uses a third party administrator", "Uses a Third Party Administrator (TPA)?"),
                          ("Regulatory action in the last five years", "Regulatory Action in Last 5 Years?"),
                          ("Cyber insurance in force", "Cyber Coverage in Force?")]),
        ],
        "sign": ["Authorized Signature", "Date Signed"],
    },
    {
        "client_id": "C002", "company_name": "Delta Pine Mutual Insurance Company",
        "name": "Carrier Partner Annual Attestation",
        "file": "templates/C002_Carrier_Partner_Annual_Attestation.docx",
        "issuer": "Northgate Specialty Insurance Co.", "ref": "NSI-CPA-2027", "color": "1E5631",
        "intro": ("Annual attestation for carrier partners. Statutory figures should match the most recent "
                  "annual statement; ratings should reflect the current AM Best report."),
        "sections": [
            ("Company", [("Company name", "Company Name"), ("NAIC company code", "NAIC Company Code"),
                         ("Date of incorporation", "Date of Incorporation"),
                         ("State of domicile", "State of Domicile")]),
            ("Home office", [("Street", "Street Address"), ("City", "City"), ("State", "State"),
                             ("ZIP", "Zip Code")]),
            ("Partnership contact", [("Name", "Contact Person"), ("Title", "Contact Title"),
                                     ("Telephone", "Telephone"), ("E-mail", "E-mail Address")]),
            ("Financial strength", [("Direct written premium", "Direct Written Premium"),
                                    ("Policyholder surplus", "Policyholder Surplus"),
                                    ("Net income", "Net Income"), ("Combined ratio", "Combined Ratio"),
                                    ("AM Best rating", "AM Best Rating: A++ | A+ | A | A- | B++ | B+ | NR"),
                                    ("Rating outlook", "Rating Outlook: Positive | Stable | Negative")]),
            ("Reinsurance", [("Reinsurance program in place", "Reinsurance Program in Place?"),
                             ("Uses catastrophe modeling", "Uses Catastrophe Modeling?")]),
        ],
        "sign": ["Officer Signature"],
    },
    {
        "client_id": "C013", "company_name": "Harborline Marine Underwriters, LLC",
        "name": "Marine Program Underwriting Submission",
        "file": "templates/C013_Marine_Program_Underwriting_Submission.docx",
        "issuer": "Keel Marine Insurance Co.", "ref": "KMI-MUS-2027", "color": "0A3D62",
        "intro": "Underwriting submission for new marine programs. Attach vessel schedules separately.",
        "sections": [
            ("Applicant", [("Applicant legal name", "Applicant Legal Name"), ("FEIN", "FEIN"),
                           ("Date established", "Date Established")]),
            ("Contact", [("Primary contact", "Primary Contact Name"), ("Telephone", "Telephone"),
                         ("E-mail", "E-mail Address")]),
            ("Program", [("Gross written premium", "Gross Written Premium"), ("Binding authority", AUTHORITY),
                         ("Cyber insurance in force", "Cyber Coverage in Force?")]),
        ],
        "sign": ["Authorized Signature"],
    },
]


def _shade(cell, hex_color: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tc_pr.append(shd)


def _run(par, text, bold=False, size=10, color=None, italic=False):
    r = par.add_run(text)
    r.bold, r.italic = bold, italic
    r.font.size = Pt(size)
    if color:
        r.font.color.rgb = RGBColor.from_string(color)
    return r


def build(spec: dict) -> Path:
    doc = Document()
    doc.core_properties.title = spec["name"]
    doc.core_properties.author = spec["issuer"] + " (fictional)"
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(10)
    sec = doc.sections[0]
    sec.left_margin = sec.right_margin = Pt(54)

    hdr = sec.header.paragraphs[0]
    _run(hdr, spec["issuer"].upper(), bold=True, size=9, color=spec["color"])
    _run(hdr, f"     Ref. {spec['ref']}", size=8, color="5B6676")
    ftr = sec.footer.paragraphs[0]
    ftr.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _run(ftr, "FICTIONAL DEMO FORM - all names and identifiers are mock data.", size=7, color="5B6676")

    title = doc.add_paragraph()
    _run(title, spec["name"], bold=True, size=20, color=spec["color"])
    intro = doc.add_paragraph()
    _run(intro, spec["intro"], italic=True, size=9.5, color="5B6676")

    for heading, rows in spec["sections"]:
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(10)
        _run(h, heading, bold=True, size=12, color=spec["color"])
        table = doc.add_table(rows=0, cols=2)
        table.style = "Table Grid"
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        for label, placeholder in rows:
            cells = table.add_row().cells
            _shade(cells[0], "F3F5F8")
            _run(cells[0].paragraphs[0], label, bold=True, size=9.5, color="1C2533")
            _run(cells[1].paragraphs[0], "{{" + placeholder + "}}", size=10)
            cells[0].width, cells[1].width = Pt(170), Pt(330)

    doc.add_paragraph()
    att = doc.add_paragraph()
    _run(att, "Attestation. ", bold=True, size=10)
    _run(att, "I confirm the information above is complete and accurate to the best of my knowledge.", size=10)
    for label in spec["sign"]:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        _run(p, f"{label}:  ", bold=True, size=10)
        _run(p, "{{" + label + "}}", size=10)

    out = ROOT / spec["file"]
    out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out))
    return out


def build_all() -> list[Path]:
    return [build(s) for s in DOCX_TEMPLATES]


if __name__ == "__main__":
    for p in build_all():
        print("built", p.relative_to(ROOT))
