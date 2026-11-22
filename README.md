# DD Autofill (proof of concept)

DD Autofill fills due diligence forms for US commercial insurance automatically. An administrator uploads each
client company's empty form (fillable PDF, Word document or web form) once. An analyst picks the form and clicks
**Fill form**. The application reads that company's **LLM-extracted JSON** and its **database rows**, matches every
form field to the right value, converts it to US formats, fills the form and shows a field-by-field review. Anything
doubtful is flagged for a person, never guessed.

> All companies, people, carriers and identifiers are **fictional** demo data (FEIN `00-000000N`, NAIC `99xxx`,
> licences `MOCK-…`, phones `555-01xx`, domains `.example`).

## Features

- **Template setup:** upload a PDF, Word (.docx) or web form (.html) per company, with the company name and a unique
  identifier; preview, download and delete; paginated grid (10 per page by default).
- **Fill template:** pick a form, see the blank form at once, fill it in under a second, filter by status
  (Filled, Review, Missing, Unmapped, Manual), correct values and **Apply edits**, highlight fields, flatten PDFs,
  download. A **Data is not available** popup appears when a company has no data yet.
- **Smart matching at fill time:** exact name, then a 77-concept insurance glossary, then fuzzy similarity
  (flagged for review); an optional AI tier (Anthropic Claude) is switched off.
- **US formatting:** currency, dates (ambiguous dates flagged), phone numbers, states, e-mail, yes/no, choices.
- **Source rules:** database first for master data, documents first for document facts; conflicts, low confidence
  and approximate values are flagged for review.
- **Data** and **Audit** screens: the JSON and database rows behind each company, and every fill and edit.

Full details: [`docs/DD_Autofill_Features_Guide.docx`](docs/DD_Autofill_Features_Guide.docx).
Architecture and functional flow diagrams: [`docs/DD_Autofill_Architecture_and_Flow.pptx`](docs/DD_Autofill_Architecture_and_Flow.pptx).

## Run locally

Requires Python 3.11 or later.

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\streamlit run app.py             # http://localhost:8501
.venv\Scripts\python -m pytest                 # 140 tests
```

The demo data, templates and registry are already in the repository. To rebuild everything from scratch
(this resets the template registry to the demo set):

```powershell
.venv\Scripts\python -m scripts.build_all
```

The demo runs offline and needs no sign-in. Copy `.env.example` to `.env` only if you want to switch on the
optional AI matching tier.

## Deploy on Streamlit Community Cloud

1. Sign in at [share.streamlit.io](https://share.streamlit.io) with GitHub.
2. **Create app** → **Deploy a public app from GitHub**.
3. Repository `Sneha-Srinath/ddautofillpoc`, branch `main`, main file `app.py`.
4. Under **Advanced settings**, choose Python **3.12**. No secrets are needed.
5. **Deploy**. The first build takes a few minutes.

Notes for the hosted app:

- Exact Word previews need Microsoft Word, which the cloud server does not have, so Word templates show an
  approximate preview there. Filling and downloading Word templates work normally.
- The cloud server does not keep files written while the app runs. Templates uploaded, fills and audit entries made
  on the hosted app are lost when it restarts; the demo set in the repository is always restored.

## Template formats

Each company can have one template of each type:

| Type | How fields are marked | Output |
|---|---|---|
| Fillable PDF | Form fields (name and tooltip) | Filled PDF, optionally flattened |
| Word (.docx) | Placeholders: `{{Applicant Legal Name}}`, `{{Uses TPA?}}` for yes/no, `{{Binding Authority: Full \| Limited \| Referral Only}}` for a choice | Filled .docx (yes/no and choices shown as ☒/☐) |
| Web form (.html) | `<input>`, `<select>`, `<textarea>`, checkboxes and radio groups, labelled with `<label for>` or a `<fieldset>` legend | Filled .html |

## How templates link to data

Each template has a **company name** and a **unique identifier** (2 to 20 letters and numbers, stored upper case).
The identifier is the company's `client_id`: Fill reads `data/extracted/<ID>.json` and every database row with
`client_id = '<ID>'`, so one client's data can never appear on another client's form.

## Project layout

| Path | Purpose |
|---|---|
| `app.py`, `views/` | Streamlit screens: Fill template, Template setup, Data, Audit |
| `ui/` | Theme, PDF viewer, Word and web form viewers |
| `core/` | Fill engine in plain Python (no Streamlit), reusable from an API or batch job |
| `core/adapters/` | PDF, Word and web form discovery and filling; Word to PDF previews |
| `core/catalog.py`, `core/matcher.py`, `core/convert.py`, `core/resolver.py` | Load one client's data, match fields, convert values, decide sources and statuses |
| `core/registry.py`, `core/engine.py`, `core/audit.py` | Uploaded templates, the fill pipeline, the audit log |
| `config/` | Insurance glossary, settings and the template registry |
| `data/` | Demo SQLite database and extracted JSON |
| `templates/` | Uploaded template files |
| `scripts/` | Builders for the demo data, templates and Mock Data Report |
| `reports/Mock_Data_Report.pdf` | Report on the demo data |
| `docs/` | Features guide, architecture and flow deck, POC plan |
| `tests/` | Automated tests |

## Demo companies

| ID | Company | Templates | Shows |
|---|---|---|---|
| C001 | Harbor Point Insurance Group, LLC | PDF, Word, web form | Clean fill |
| C002 | Delta Pine Mutual Insurance Company | PDF, Word, web form | Conflicts, approximate value, rating not an option |
| C003 | Summit Ridge Specialty Brokers, Inc. | PDF | Low confidence, format conversion |
| C004 | Bluewater Re Partners, LLC | PDF | Single-source values, ambiguous date, fuzzy matches |
| C005 | Keystone Benefits Brokerage, Inc. | PDF | Missing data, unclear yes/no |
| C006 | Ironwood Specialty Underwriters, LLC | PDF | Premium conflict |
| C007 | Lakeshore Mutual Casualty Company | PDF | Value missing from documents, database used |
| C008 | Granite Peak Captive Managers, Inc. | PDF | Unanswered question |
| C009 | Crestline Claims Services, Inc. | PDF | "N/A" yes/no, approximate count |
| C010 | Northstar Premium Finance Company | PDF | Database only, two unmapped fields |
| C011 | BrightPath Digital Insurance Agency, Inc. | PDF | Low-confidence chart figure |
| C012 | Cascade Surplus Lines Brokerage, LLC | PDF | Clean fill, section-coded field names |
| C013 | Harborline Marine Underwriters, LLC | PDF, Word | Template before data: "Data is not available" |
| C014 | Prairie Ag Risk Services, Inc. | PDF | Template before data: "Data is not available" |

## Path to production

Wrap `core/` in FastAPI, move to SQL Server or PostgreSQL and Blob storage, add Entra ID sign-in and per-client
access, render Word previews on a server-side converter, and support repeating sections and scanned forms
(see `docs/POC_PLAN.md`).
