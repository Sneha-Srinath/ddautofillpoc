"""Generate the demo web form (.html) templates."""
from __future__ import annotations

import html
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ENTITY_TYPES = ["Limited Liability Company", "Corporation", "Partnership", "Mutual Company", "Reciprocal Exchange"]
STATES = ["AL", "DE", "FL", "GA", "LA", "MA", "MS", "NC", "NY", "PA", "SC", "TN", "TX", "VA"]
AM_BEST = ["A++", "A+", "A", "A-", "B++", "B+", "B", "NR"]

# (kind, name, label, extra)   kind: text | email | tel | date | number | textarea | select | radio | checkbox
HTML_TEMPLATES = [
    {
        "client_id": "C001", "company_name": "Harbor Point Insurance Group, LLC",
        "name": "Online MGA Onboarding Form", "file": "templates/C001_Online_MGA_Onboarding_Form.html",
        "issuer": "Granite Shield Casualty Co.", "color": "#1B365D", "accent": "#C9A23F",
        "intro": "Complete this form to onboard as a managing general agent. Fields marked * are required.",
        "sections": [
            ("Company", [("text", "legal_entity_name", "Legal Entity Name *", {}),
                         ("text", "fein", "FEIN *", {"maxlength": "10"}),
                         ("text", "dba", "Doing Business As", {}),
                         ("date", "established", "Date Established", {}),
                         ("select", "domicile", "State of Domicile", {"options": STATES}),
                         ("select", "entity_type", "Entity Type", {"options": ENTITY_TYPES}),
                         ("text", "website", "Website", {})]),
            ("Mailing address", [("text", "street", "Mailing Street", {}), ("text", "city", "Mailing City", {}),
                                 ("select", "state", "Mailing State", {"options": STATES}),
                                 ("text", "zip", "Mailing ZIP", {"maxlength": "10"})]),
            ("Primary contact", [("text", "contact_name", "Primary Contact Name", {}),
                                 ("text", "contact_title", "Primary Contact Title", {}),
                                 ("tel", "contact_phone", "Telephone", {}),
                                 ("email", "contact_email", "Email Address", {})]),
            ("Program", [("text", "gwp", "Gross Written Premium (last fiscal year)", {}),
                         ("number", "programs", "Number of Active Programs", {}),
                         ("text", "loss_ratio", "Three Year Loss Ratio", {}),
                         ("textarea", "lines", "Lines of Business Written", {}),
                         ("radio", "binding_authority", "Binding Authority",
                          {"options": ["Full", "Limited", "Referral Only"]}),
                         ("checkbox", "uses_tpa", "Uses a Third Party Administrator (TPA)", {}),
                         ("checkbox", "regulatory_action", "Regulatory Action in Last 5 Years", {}),
                         ("checkbox", "cyber", "Cyber Coverage in Force", {})]),
            ("Attestation", [("text", "signature", "Authorized Signature", {})]),
        ],
    },
    {
        "client_id": "C002", "company_name": "Delta Pine Mutual Insurance Company",
        "name": "Carrier Portal Registration", "file": "templates/C002_Carrier_Portal_Registration.html",
        "issuer": "Northgate Specialty Insurance Co.", "color": "#1E5631", "accent": "#8DB663",
        "intro": "Register your company for the Northgate carrier partner portal.",
        "sections": [
            ("Carrier", [("text", "insured_name", "Insured Name", {}),
                         ("text", "naic", "NAIC Company Code", {}),
                         ("date", "incorporated", "Date of Incorporation", {}),
                         ("text", "domicile", "State of Domicile", {"maxlength": "2"})]),
            ("Home office", [("text", "street", "Street Address", {}), ("text", "city", "City", {}),
                             ("text", "state", "State", {"maxlength": "2"}),
                             ("text", "zip", "Zip Code", {"maxlength": "10"})]),
            ("Portal administrator", [("text", "contact", "Contact Person", {}),
                                      ("text", "title", "Contact Title", {}),
                                      ("tel", "phone", "Telephone", {}),
                                      ("email", "email", "E-mail Address", {})]),
            ("Financials", [("text", "dwp", "Direct Written Premium", {}),
                            ("text", "surplus", "Policyholder Surplus", {}),
                            ("select", "am_best", "AM Best Rating", {"options": AM_BEST}),
                            ("radio", "outlook", "Rating Outlook", {"options": ["Positive", "Stable", "Negative"]}),
                            ("checkbox", "reinsurance", "Reinsurance Program in Place", {}),
                            ("checkbox", "cat_model", "Uses Catastrophe Modeling", {})]),
            ("Certification", [("text", "officer_signature", "Officer Signature", {})]),
        ],
    },
]

CSS = """
*{box-sizing:border-box} body{margin:0;background:#EEF1F5;font-family:'Segoe UI',Arial,sans-serif;color:#1C2533}
.page{max-width:760px;margin:24px auto;background:#fff;border-radius:10px;overflow:hidden;
  box-shadow:0 2px 10px rgba(20,35,60,.08)}
header{background:var(--brand);color:#fff;padding:22px 28px;border-bottom:4px solid var(--accent)}
header small{letter-spacing:.06em;font-weight:600;opacity:.85} header h1{margin:6px 0 0;font-size:24px}
.intro{padding:14px 28px 0;color:#5B6676;font-size:13px}
form{padding:8px 28px 28px} fieldset{border:1px solid #D5DBE3;border-radius:8px;margin:16px 0 0;padding:12px 16px 14px}
legend{font-weight:700;color:var(--brand);padding:0 6px;font-size:14px}
.row{display:grid;grid-template-columns:repeat(2,1fr);gap:10px 16px}
.f{display:flex;flex-direction:column;gap:4px;font-size:12px;color:#5B6676;font-weight:600}
.f.wide{grid-column:1 / -1}
input[type=text],input[type=email],input[type=tel],input[type=date],input[type=number],select,textarea{
  font:inherit;font-size:14px;font-weight:400;color:#1C2533;padding:8px 10px;border:1px solid #C9D1DC;border-radius:6px;background:#F8FAFC}
textarea{min-height:64px}
.opts{display:flex;gap:18px;flex-wrap:wrap;font-weight:400;color:#1C2533;font-size:14px}
.check{display:flex;align-items:center;gap:8px;font-weight:400;color:#1C2533;font-size:14px}
footer{padding:12px 28px;font-size:11px;color:#5B6676;border-top:1px solid #E3E7ED}
button{background:var(--brand);color:#fff;border:0;border-radius:6px;padding:10px 18px;font-weight:600;margin-top:16px}
"""


def _field(kind: str, name: str, label: str, extra: dict) -> str:
    lab = html.escape(label)
    fid = f"f_{name}"
    if kind == "radio":
        opts = "".join(f'<label><input type="radio" name="{name}" value="{html.escape(o)}"> {html.escape(o)}</label>'
                       for o in extra["options"])
        return f'<fieldset class="f wide"><legend>{lab}</legend><div class="opts">{opts}</div></fieldset>'
    if kind == "checkbox":
        return f'<div class="f wide"><label class="check"><input type="checkbox" id="{fid}" name="{name}"> {lab}</label></div>'
    if kind == "select":
        opts = '<option value=""></option>' + "".join(f"<option>{html.escape(o)}</option>" for o in extra["options"])
        return f'<div class="f"><label for="{fid}">{lab}</label><select id="{fid}" name="{name}">{opts}</select></div>'
    if kind == "textarea":
        return f'<div class="f wide"><label for="{fid}">{lab}</label><textarea id="{fid}" name="{name}"></textarea></div>'
    attrs = "".join(f' {k}="{html.escape(v)}"' for k, v in extra.items() if k != "options")
    wide = " wide" if len(label) > 32 else ""
    return (f'<div class="f{wide}"><label for="{fid}">{lab}</label>'
            f'<input type="{kind}" id="{fid}" name="{name}"{attrs}></div>')


def build(spec: dict) -> Path:
    body = []
    for title, fields in spec["sections"]:
        inner = "".join(_field(*f) for f in fields)
        body.append(f'<fieldset><legend>{html.escape(title)}</legend><div class="row">{inner}</div></fieldset>')
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>{html.escape(spec['name'])}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>:root{{--brand:{spec['color']};--accent:{spec['accent']}}}{CSS}</style></head>
<body><div class="page">
<header><small>{html.escape(spec['issuer'].upper())}</small><h1>{html.escape(spec['name'])}</h1></header>
<p class="intro">{html.escape(spec['intro'])}</p>
<form>{''.join(body)}<button type="submit">Submit</button></form>
<footer>Fictional demo form. All names and identifiers are mock data.</footer>
</div></body></html>
"""
    out = ROOT / spec["file"]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    return out


def build_all() -> list[Path]:
    return [build(s) for s in HTML_TEMPLATES]


if __name__ == "__main__":
    for p in build_all():
        print("built", p.relative_to(ROOT))
