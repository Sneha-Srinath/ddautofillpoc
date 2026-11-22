"""Build data/dd.sqlite (mock SQL) and data/extracted/<client_id>.json from mock_data."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from scripts import mock_data as M

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "dd.sqlite"
JSON_DIR = ROOT / "data" / "extracted"

SCHEMA = """
CREATE TABLE client (
  client_id TEXT PRIMARY KEY, legal_name TEXT NOT NULL, dba_name TEXT, fein TEXT,
  entity_type TEXT, client_type TEXT, state_of_domicile TEXT, website TEXT,
  year_established INTEGER, established_date TEXT, employee_count INTEGER, naic_code TEXT,
  ownership_structure TEXT, segment TEXT, hq_city TEXT);
CREATE TABLE client_address (
  client_id TEXT REFERENCES client, address_type TEXT, street TEXT, city TEXT, state TEXT, zip TEXT);
CREATE TABLE client_contact (
  client_id TEXT REFERENCES client, role TEXT, full_name TEXT, title TEXT, phone TEXT, email TEXT);
CREATE TABLE client_license (
  client_id TEXT REFERENCES client, state TEXT, license_type TEXT, license_number TEXT, expiry_date TEXT);
CREATE TABLE client_financials (
  client_id TEXT REFERENCES client, fiscal_year INTEGER, gross_written_premium REAL, revenue REAL,
  ebitda REAL, net_income REAL, am_best_rating TEXT, policyholder_surplus REAL, combined_ratio REAL);
CREATE TABLE client_insurance (
  client_id TEXT REFERENCES client, coverage_type TEXT, carrier TEXT, limit_amount REAL, expiry_date TEXT);
CREATE TABLE client_program (
  client_id TEXT REFERENCES client, program_name TEXT, line_of_business TEXT, carrier TEXT,
  binding_authority TEXT, gwp REAL, loss_ratio_3yr REAL);
CREATE TABLE client_loss_run (
  client_id TEXT REFERENCES client, year INTEGER, earned_premium REAL, incurred_losses REAL,
  loss_ratio REAL, claim_count INTEGER, large_losses_over_250k INTEGER);
CREATE TABLE client_carrier_relationship (
  client_id TEXT REFERENCES client, carrier TEXT, am_best TEXT, relationship_since INTEGER,
  pct_of_premium REAL, contract_expiry TEXT);
CREATE TABLE client_ownership (
  client_id TEXT REFERENCES client, owner TEXT, pct_held REAL, pe_backed INTEGER);
CREATE TABLE client_lending (
  client_id TEXT REFERENCES client, fiscal_year INTEGER, loans_outstanding REAL, default_rate REAL,
  contracts_financed INTEGER);
CREATE TABLE client_dd_assessment (
  client_id TEXT REFERENCES client, financial_strength REAL, underwriting_controls REAL,
  claims_handling REAL, compliance REAL, cyber_it REAL, overall_risk_rating TEXT, analyst TEXT,
  assessed_on TEXT, summary TEXT);
"""


def build_db(path: Path = DB_PATH) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    for t in ["client_lending", "client_dd_assessment", "client_ownership", "client_carrier_relationship", "client_loss_run",
              "client_program", "client_insurance", "client_financials", "client_license", "client_contact",
              "client_address", "client"]:
        con.execute(f"DROP TABLE IF EXISTS {t}")     # audit_log is kept
    con.executescript(SCHEMA)
    cols = list(M.CLIENTS[0].keys())
    con.executemany(f"INSERT INTO client ({','.join(cols)}) VALUES ({','.join('?' * len(cols))})",
                    [tuple(c[k] for k in cols) for c in M.CLIENTS])
    con.executemany("INSERT INTO client_address VALUES (?,?,?,?,?,?)", M.ADDRESSES)
    con.executemany("INSERT INTO client_contact VALUES (?,?,?,?,?,?)", M.CONTACTS)
    con.executemany("INSERT INTO client_license VALUES (?,?,?,?,?)", M.LICENSES)
    con.executemany("INSERT INTO client_financials VALUES (?,?,?,?,?,?,?,?,?)", M.FINANCIALS)
    con.executemany("INSERT INTO client_insurance VALUES (?,?,?,?,?)", M.INSURANCE)
    con.executemany("INSERT INTO client_program VALUES (?,?,?,?,?,?,?)", M.PROGRAMS)
    con.executemany("INSERT INTO client_loss_run VALUES (?,?,?,?,?,?,?)",
                    [(c, y, ep, il, round(il / ep * 100, 1), n, big) for c, y, ep, il, n, big in M.LOSS_RUNS])
    con.executemany("INSERT INTO client_carrier_relationship VALUES (?,?,?,?,?,?)", M.CARRIER_RELATIONSHIPS)
    con.executemany("INSERT INTO client_ownership VALUES (?,?,?,?)", M.OWNERSHIP)
    con.executemany("INSERT INTO client_dd_assessment VALUES (?,?,?,?,?,?,?,?,?,?)", M.DD_ASSESSMENTS)
    con.executemany("INSERT INTO client_lending VALUES (?,?,?,?,?)", M.LENDING)
    con.commit()
    con.close()
    return path


def build_json(folder: Path = JSON_DIR) -> list[Path]:
    folder.mkdir(parents=True, exist_ok=True)
    out = []
    for cid, doc in M.EXTRACTED.items():
        p = folder / f"{cid}.json"
        p.write_text(json.dumps(doc, indent=2), encoding="utf-8")
        out.append(p)
    return out


if __name__ == "__main__":
    print("built", build_db().relative_to(ROOT))
    for p in build_json():
        print("built", p.relative_to(ROOT))
