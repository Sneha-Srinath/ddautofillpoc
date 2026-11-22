"""Audit log of every fill (FR-26, FR-27), stored in the same SQLite database."""
from __future__ import annotations

import json
from datetime import datetime

import pandas as pd
from sqlalchemy import text

from core.db import engine

DDL = """
CREATE TABLE IF NOT EXISTS audit_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, user TEXT, action TEXT, template_id TEXT,
  template_version INTEGER, mapping_version INTEGER, client_id TEXT, filled INTEGER, review INTEGER,
  missing INTEGER, unmapped INTEGER, manual INTEGER, edited_fields TEXT, output_file TEXT,
  input_hash TEXT, elapsed_ms INTEGER)
"""


def _ensure():
    with engine().begin() as con:
        con.execute(text(DDL))


def log_fill(*, user: str, action: str, template_id: str, template_version: int, mapping_version: int,
             client_id: str, counts: dict[str, int], edited: dict[str, object], output_file: str,
             input_hash: str, elapsed_ms: int) -> None:
    _ensure()
    with engine().begin() as con:
        con.execute(text(
            "INSERT INTO audit_log (ts,user,action,template_id,template_version,mapping_version,client_id,"
            "filled,review,missing,unmapped,manual,edited_fields,output_file,input_hash,elapsed_ms) VALUES "
            "(:ts,:user,:action,:tid,:tv,:mv,:cid,:f,:r,:m,:u,:man,:ed,:out,:h,:ms)"),
            dict(ts=datetime.now().isoformat(timespec="seconds"), user=user, action=action, tid=template_id,
                 tv=template_version, mv=mapping_version, cid=client_id, f=counts["Filled"],
                 r=counts["Review"], m=counts["Missing"], u=counts["Unmapped"], man=counts["Manual"],
                 ed=json.dumps(edited, default=str) if edited else "", out=output_file, h=input_hash,
                 ms=elapsed_ms))


def entries(limit: int = 500) -> pd.DataFrame:
    _ensure()
    with engine().connect() as con:
        return pd.read_sql(text("SELECT * FROM audit_log ORDER BY id DESC LIMIT :n"), con, params={"n": limit})
