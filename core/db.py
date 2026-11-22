"""SQLAlchemy access to the client database. Every query is filtered by client_id (NFR-2)."""
from __future__ import annotations

from functools import lru_cache

import pandas as pd
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine

from core.config import DB_PATH

DD_TABLES = ["client", "client_address", "client_contact", "client_license", "client_financials",
             "client_insurance", "client_program", "client_loss_run", "client_carrier_relationship",
             "client_ownership", "client_dd_assessment", "client_lending"]


@lru_cache
def engine(path: str | None = None) -> Engine:
    return create_engine(f"sqlite:///{path or DB_PATH}", future=True)


def client_rows(client_id: str, table: str) -> list[dict]:
    if table not in DD_TABLES:
        raise ValueError(f"unknown table {table}")
    with engine().connect() as con:
        res = con.execute(text(f"SELECT * FROM {table} WHERE client_id = :cid"), {"cid": client_id})
        return [dict(r._mapping) for r in res]


def client_frame(client_id: str, table: str) -> pd.DataFrame:
    with engine().connect() as con:
        return pd.read_sql(text(f"SELECT * FROM {table} WHERE client_id = :cid"), con,
                           params={"cid": client_id})


def client_names() -> dict[str, str]:
    with engine().connect() as con:
        return {r[0]: r[1] for r in con.execute(text("SELECT client_id, legal_name FROM client"))}


def client_record(client_id: str) -> dict | None:
    rows = client_rows(client_id, "client")
    return rows[0] if rows else None


def table_exists(name: str) -> bool:
    return inspect(engine()).has_table(name)


def client_rows_all(table: str) -> list[dict]:
    """All rows of a table across clients - reporting only, never used by a fill."""
    if table not in DD_TABLES:
        raise ValueError(f"unknown table {table}")
    with engine().connect() as con:
        return [dict(r._mapping) for r in con.execute(text(f"SELECT * FROM {table}"))]
