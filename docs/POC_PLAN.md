# DD AutoFill POC — End-to-End Build Plan (US Commercial Insurance)

## Context
We are an analytics provider serving several US insurance companies. For each client we hold LLM-extracted JSON and SQL rows. Today analysts re-key this data into each client's due diligence (DD) form. The POC proves a one-click flow: pick a client's fillable-PDF template → **Fill** → review flagged values → download. Demo to US insurance stakeholders on **23 Nov 2026** (4 working days from today, 19 Nov).

**Baseline:** `due-diligence-autofill-plan_updated.md` (v2). Decisions confirmed with you:
- Fillable PDF only (no Word/Excel); one template per client; `client_id` is the only key; Streamlit UI; Python end to end.
- Client mix = v2 mix (MGA, carrier, wholesale broker, reinsurance intermediary, benefits agency). Client 1 is the flagship **MGA / program administrator** in the style of a US commercial-lines program MGA (all names fictional).
- Mock-data report delivered as **an in-app Data page** and **a branded PDF report**.
- Optional semantic matching tier uses **Anthropic Claude**, off by default (demo runs offline).

Workspace `C:\workspace\SnehaAutoFilledUtility` is empty — greenfield build.

## Skills applied
| Skill | Used for |
|---|---|
| `pdf` | AcroForm template creation (ReportLab), field discovery/fill/flatten (PyMuPDF), mock-data report PDF |
| `ui-ux-pro-max` + `frontend-design` | Professional insurance look: navy/slate + muted gold palette, IBM Plex Sans, status chips, dense review tables |
| `dataviz` | KPI tiles, status distribution bar, confidence bars, loss-ratio sparkline on the Data page and in the report |
| `design-system` | Tokens in one place (`ui/theme.py` + `.streamlit/config.toml`) so app and PDF report share colors/type |

## Architecture (engine separate from UI)
```
dd-autofill/
├── app.py                         # Streamlit entry, sidebar nav, theme injection
├── pages/ 1_Fill_Template.py  2_Template_Setup.py  3_Data.py  4_Audit.py
├── ui/ theme.py  components.py    # CSS, status chips, KPI tiles, PDF page preview
├── core/                          # pure Python, no Streamlit imports
│   ├── models.py      # Pydantic: ExtractedJson, DiscoveredField, FieldMapping, TemplateConfig, ResolvedField, FillResult
│   ├── discovery.py   # PyMuPDF widgets → name, tooltip, type, options, page, rect, maxlen
│   ├── catalog.py     # flatten JSON (unwrap {value,confidence,source_ref}) + SQL rows (filters like [role=Primary], latest fiscal_year)
│   ├── matcher.py     # tier1 exact-normalized → tier2 synonyms.yaml → tier3 rapidfuzz token_set ≥85 → tier4 Claude (flag) ; type-compatibility check
│   ├── llm.py         # Anthropic client; sends only field names/labels + path names (NFR-7)
│   ├── convert.py     # text, currency, date, phone, email, state, checkbox, radio/dropdown (US rules, §5.4)
│   ├── resolver.py    # precedence (DB-first master data, JSON-first doc facts), conflicts, confidence <0.80, statuses
│   ├── filler.py      # write widgets, optional flatten, page PNG previews, output file naming
│   ├── registry.py    # load/save config/templates/<id>.yaml with versioning (keeps old versions)
│   ├── db.py          # SQLAlchemy engine on data/dd.sqlite, client-scoped queries only
│   └── audit.py       # audit_log table: ts, user, template+mapping version, client_id, status counts, edits, file, input hash
├── config/ settings.yaml  synonyms.yaml  templates/tpl-*.yaml
├── data/ dd.sqlite  extracted/C00x.json
├── templates/ 5 fillable PDFs
├── scripts/ build_db.py  build_json.py  build_templates.py  build_data_report.py  automatch_all.py
├── reports/ Mock_Data_Report.pdf   output/ (gitignored)
├── tests/
├── requirements.txt  .env.example  .streamlit/config.toml  README.md
```
Libraries: streamlit, pydantic v2, sqlalchemy, pymupdf, reportlab, rapidfuzz, dateparser, phonenumbers, pyyaml, pandas, python-dotenv, anthropic (optional), pytest.

## Mock data design (the stakeholder centrepiece)
All entities fictional; FEINs `00-000000N`, NAIC codes `99xxx`, license numbers prefixed `MOCK-`, all phone numbers `555-01xx`.

### The five clients
| ID | Client | Type / HQ | Business story | Template (issuer) | Field naming style |
|---|---|---|---|---|---|
| C001 | Harbor Point Insurance Group, LLC | MGA / program administrator, Charlotte NC | 6 commercial programs (habitational, artisan contractors, restaurants, light auto/transport, self-storage, umbrella); $48.6M GWP; binding authority from 3 A-rated carriers; in-house claims + one TPA | MGA Due Diligence Questionnaire (fictional carrier "Granite Shield Casualty") | `Applicant_Legal_Name` snake case |
| C002 | Delta Pine Mutual Insurance Co. | Regional P&C carrier, Jackson MS | Commercial package & farmowners; $212M DWP; AM Best A-; surplus $96M; quota share + cat XOL | Carrier Partner Due Diligence Form | `Insured Name` spaced labels |
| C003 | Summit Ridge Specialty Brokers, Inc. | Wholesale E&S broker, Dallas TX | E&S property, GL, excess; licensed in 38 states; E&O $5M | Agency Appointment & Licensing Form | `Name of Agency` question style |
| C004 | Bluewater Re Partners, LLC | Reinsurance intermediary, Boston MA | Treaty/fac placements for regional carriers; collateral trust arrangements; OFAC screening | Reinsurance Counterparty DD Checklist | `EntityName` Pascal case |
| C005 | Keystone Benefits Brokerage, Inc. | Employee benefits agency, Pittsburgh PA | 1,140 group clients; $18.4M revenue; top carrier = 41% of commissions; acquisition target | Acquisition Due Diligence Information Request | `Company` short labels |

### SQL schema (`data/dd.sqlite`, every table keyed by `client_id`)
v2 core tables: `client`, `client_address` (Mailing/Physical), `client_contact` (Primary/CFO/Compliance/Claims), `client_license`, `client_financials` (FY2023–FY2025), `client_insurance` (E&O, Cyber, D&O, Crime, Fidelity bond).
DD-specific additions (make the Data page and report rich; single-value fields picked by filter):
- `client_program` — program name, line of business, carrier, binding authority (Full/Limited/Referral), GWP, 3-yr loss ratio
- `client_loss_run` — year, earned premium, incurred losses, loss ratio, claim count, large losses >$250K
- `client_carrier_relationship` — carrier, AM Best, relationship since, % of premium, contract expiry
- `client_ownership` — owner/entity, % held, PE-backed flag
- `client_dd_assessment` — our analytics scores: financial strength, underwriting controls, claims handling, compliance, cyber/IT, overall risk rating (Low/Moderate/Elevated)
- `audit_log`, created by the app

### Extracted JSON (`data/extracted/C00x.json`)
Each carries `client_id`, `client_name`, `extracted_at`, `source_documents` (realistic names: audited statutory statements, producer agreements, carrier audit letters, SOC 2 report, loss runs). Sections: entity, operations, financial_highlights, underwriting (authority, referral thresholds, last carrier UW audit score), claims (TPA use, avg closing days), compliance (regulatory actions 5 yrs, pending litigation, OFAC screening, licensing in good standing), cyber_it (MFA, SOC 2, incident last 3 yrs), reinsurance, key_personnel, risk_findings[] (area, rating, finding). Leaves are `{value, confidence, source_ref}`. Key names deliberately differ per client (`legal_name` / `registered_entity` / `company_name` …) to prove auto-matching.

### Scenario matrix (each maps to an expected status, tested)
| Case | Where | Expected |
|---|---|---|
| Clean fill | C001 all fields | Filled (manual signature = Manual) |
| JSON vs DB conflict | C002 phone and GWP differ | Review, DB value used, both shown in note |
| Low confidence | C003 E&O limit conf 0.64 | Review |
| JSON-only / DB-only | C004 rating only in JSON, FEIN only in DB | Filled from the single source |
| Format conversion | `March 3, 2024`→`03/03/2024`, `$1.2M`→`$1,200,000.00`, `Texas`→`TX`, `2145550142`→`(214) 555-0142` | Filled |
| Approximate amount | C002 "approx $96M" surplus | Review |
| Ambiguous date | C004 `04/05/2019` where field order unclear | Review |
| Ambiguous yes/no | C005 litigation "under review" | Blank + Review, not guessed |
| Missing | C005 two fields absent from both sources | Missing |
| Dropdown no match | C002 rating "A minus-ish" | Blank + Review |

### Five templates (`scripts/build_templates.py`, ReportLab AcroForm)
20–26 fields each, different layout and issuer branding; each has legal name, mailing address block, primary contact name/phone/email, ≥1 date, ≥1 currency, ≥2 checkboxes, 1 radio group, 1 dropdown, 1 manual signature/attestation field; tooltips set on every field. Mappings saved after running `automatch_all.py` and a scripted "admin review" so AC-1 holds offline.

### Mock Data Report (`reports/Mock_Data_Report.pdf`, `scripts/build_data_report.py`)
Branded cover → purpose & data lineage diagram → one 2-page profile per client (KPI tiles, program table, 3-yr loss-ratio chart, carrier mix, DD assessment scores, source documents) → data dictionary (JSON paths + SQL columns) → scenario matrix → "all data is fictional" disclaimer. The **Data** page shows the same per-client view live (JSON tree, SQL tables, KPI tiles) plus a download button for the report.

## UI (Streamlit, insurance-professional theme)
- **Fill Template:** template cards (template + client name + type badge) → Fill → status chips (Filled/Review/Missing/Unmapped/Manual) → split view: PDF page previews | review table (`st.data_editor`: field, value, source badge JSON/DB/User, path, confidence bar, status, note; "Needs attention" filter) → Apply edits → Download (optional flatten). File name `<ClientName>_<TemplateName>_<YYYY-MM-DD>.pdf`.
- **Template Setup:** pick template → discovered fields → Auto-match (LLM toggle disabled when no key) → mapping table with method/score/sample value, searchable source picker, accept/clear/manual, precedence → Save as version N+1.
- **Data:** client selector, KPI tiles, JSON viewer, SQL tables per table, report download.
- **Audit:** newest-first log with status counts and edited fields.

## Build sequence (fits 19–22 Nov, rehearsal 22 Nov)
1. **Scaffold** — venv, requirements, settings/synonyms YAML, theme, Pydantic models. *Check:* `pytest` runs, `streamlit run app.py` shows themed shell.
2. **Mock data** — `build_db.py`, `build_json.py`, `build_templates.py`. *Check:* 5 PDFs open in a viewer with fields; DB row counts; JSON validate against models.
3. **Core engine** — catalog, convert, matcher, resolver, filler, registry, audit; `automatch_all.py` saves mappings. *Check:* unit tests per conversion rule, tier, precedence, status; AC-2 ≥90% tiers 1–3.
4. **UI pages** — Fill, Setup, Data, Audit.
5. **Mock Data Report PDF** + Data page polish.
6. **Tests & rehearsal** — end-to-end fill test per template asserting the scenario matrix; timing <3 s; run demo flow v2 §7.3 with LLM off.

## Verification
- `pytest -q`: conversion rules, matcher tiers, type compatibility, precedence/conflict, statuses, wrong-`client_id` refusal (AC-6), e2e fill of all 5 templates reading values back from the output PDF with PyMuPDF (AC-4/AC-5), fill timing <3 s (AC-3).
- `streamlit run app.py`, driven in the built-in browser pane: walk demo flow §7.3, edit a value → Apply edits → confirm audit entry (AC-7), screenshot each page.
- Open `reports/Mock_Data_Report.pdf` and a downloaded filled PDF; render page 1 to PNG for visual check.
- Run with `LLM_ENABLED=false` and no API key to confirm AC-8.

## Risks
- Radio/dropdown widgets created by ReportLab may behave differently in PyMuPDF → fallback: build templates with PyMuPDF widgets; covered by e2e read-back tests.
- Python not yet confirmed on this Windows machine → first step checks `python --version` (3.11+); install via python.org if missing.

## Build status (19 Nov 2026)

| Step | Status |
|---|---|
| Scaffold, config, Pydantic models | Done |
| Mock SQL (11 tables, 139 rows), 5 extracted JSON files, 5 fillable PDFs | Done |
| Engine: discovery, catalog, matcher, converter, resolver, filler, registry, audit | Done |
| Streamlit UI: Fill, Template setup, Data, Audit | Done, checked in the browser |
| Mock Data Report PDF (9 pages) | Done |
| Tests (68) incl. end-to-end fill of all 5 templates against the scenario matrix | Passing |

Acceptance criteria: AC-1 to AC-8 covered by `tests/` and the demo walk-through (auto-match 100% with
tiers 1-3 on every template; fills ~0.1-0.3 s; LLM off throughout).

Deviations from the plan: templates are drawn with ReportLab AcroForm and the radio appearances are
redrawn with PyMuPDF so they render identically in every viewer; the LLM tier uses `claude-opus-5-5`
with structured output and server-side fallback, and stays off by default.
