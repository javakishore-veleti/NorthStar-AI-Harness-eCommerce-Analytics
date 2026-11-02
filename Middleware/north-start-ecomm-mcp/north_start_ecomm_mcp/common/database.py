from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from north_start_ecomm_mcp.common.singleton import Singleton

_PROJECT_ROOT = Path(__file__).resolve().parents[2]


def company_db_path() -> Path:
    override = os.environ.get("NORTHSTAR_COMPANY_DB")
    if override:
        return Path(override)
    return _PROJECT_ROOT / ".runtime" / "company.db"


class DatabaseGateway(metaclass=Singleton):
    def __init__(self, path: Path | None = None) -> None:
        self.path = Path(path) if path is not None else company_db_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._create_schema_and_seed()

    def read(self, sql: str, params: tuple = ()) -> list[sqlite3.Row]:
        connection = self._connect_read()
        try:
            return list(connection.execute(sql, params))
        finally:
            connection.close()

    def write(self, sql: str, params: tuple = ()) -> None:
        connection = self._connect_write()
        try:
            connection.execute(sql, params)
            connection.commit()
        finally:
            connection.close()

    def _connect_read(self) -> sqlite3.Connection:
        uri = f"{self.path.resolve().as_uri()}?mode=ro"
        connection = sqlite3.connect(uri, uri=True)
        connection.row_factory = sqlite3.Row
        return connection

    def _connect_write(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _create_schema_and_seed(self) -> None:
        connection = self._connect_write()
        try:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS customers (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL COLLATE NOCASE,
                    need TEXT NOT NULL,
                    contact TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS issues (
                    id TEXT PRIMARY KEY,
                    customer TEXT NOT NULL COLLATE NOCASE,
                    symptom TEXT NOT NULL,
                    owner TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS revenue (
                    quarter TEXT PRIMARY KEY,
                    amount_usd INTEGER NOT NULL
                );
                CREATE TABLE IF NOT EXISTS outbox (
                    id TEXT PRIMARY KEY,
                    customer TEXT NOT NULL,
                    body TEXT NOT NULL
                );
                INSERT OR IGNORE INTO customers (id, name, need, contact) VALUES
                    (
                        'C-101',
                        'Acme',
                        'Unify weekly sales reporting across three teams',
                        'buyer@acme.example'
                    ),
                    (
                        'C-102',
                        'Beacon',
                        'Investigate delayed dashboard refreshes',
                        'ops@beacon.example'
                    );
                INSERT OR IGNORE INTO issues (id, customer, symptom, owner) VALUES
                    (
                        'INC-42',
                        'Beacon',
                        'Sync stalls when the upstream API returns HTTP 429',
                        'Data Platform'
                    );
                INSERT OR IGNORE INTO revenue (quarter, amount_usd) VALUES
                    ('2026-Q3', 480000);
                """
            )
            connection.commit()
        finally:
            connection.close()
