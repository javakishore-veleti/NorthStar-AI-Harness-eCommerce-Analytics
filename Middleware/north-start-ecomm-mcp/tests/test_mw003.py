import ast
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1] / "north_start_ecomm_mcp"


class DatabaseTests(unittest.TestCase):
    def setUp(self) -> None:
        from north_start_ecomm_mcp.common.database import DatabaseGateway

        DatabaseGateway.clear()
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "company.db"

    def tearDown(self) -> None:
        from north_start_ecomm_mcp.common.database import DatabaseGateway

        DatabaseGateway.clear()
        self.tmp.cleanup()

    def test_gateway_is_a_singleton(self) -> None:
        from north_start_ecomm_mcp.common.database import DatabaseGateway

        self.assertIs(DatabaseGateway(self.path), DatabaseGateway(self.path))

    def test_fresh_file_contains_the_design_seed(self) -> None:
        from north_start_ecomm_mcp.common.database import DatabaseGateway

        gateway = DatabaseGateway(self.path)
        customers = gateway.read(
            "SELECT id, name, need, contact FROM customers ORDER BY id"
        )
        issues = gateway.read(
            "SELECT id, customer, symptom, owner FROM issues ORDER BY id"
        )
        revenue = gateway.read(
            "SELECT quarter, amount_usd FROM revenue ORDER BY quarter"
        )
        outbox = gateway.read("SELECT id FROM outbox")
        self.assertEqual(
            [tuple(row) for row in customers],
            [
                (
                    "C-101",
                    "Acme",
                    "Unify weekly sales reporting across three teams",
                    "buyer@acme.example",
                ),
                (
                    "C-102",
                    "Beacon",
                    "Investigate delayed dashboard refreshes",
                    "ops@beacon.example",
                ),
            ],
        )
        self.assertEqual(
            [tuple(row) for row in issues],
            [
                (
                    "INC-42",
                    "Beacon",
                    "Sync stalls when the upstream API returns HTTP 429",
                    "Data Platform",
                )
            ],
        )
        self.assertEqual([tuple(row) for row in revenue], [("2026-Q3", 480000)])
        self.assertEqual(list(outbox), [])

    def test_second_open_keeps_existing_outbox_rows(self) -> None:
        from north_start_ecomm_mcp.common.database import DatabaseGateway

        gateway = DatabaseGateway(self.path)
        gateway.write(
            "INSERT INTO outbox (id, customer, body) VALUES (?, ?, ?)",
            ("receipt-1", "Acme", "scope"),
        )
        DatabaseGateway.clear()
        reopened = DatabaseGateway(self.path)
        customers = reopened.read("SELECT COUNT(*) AS n FROM customers")
        revenue = reopened.read("SELECT amount_usd FROM revenue WHERE quarter = ?", ("2026-Q3",))
        outbox = reopened.read("SELECT id, customer, body FROM outbox")
        self.assertEqual(customers[0]["n"], 2)
        self.assertEqual(revenue[0]["amount_usd"], 480000)
        self.assertEqual([tuple(row) for row in outbox], [("receipt-1", "Acme", "scope")])

    def test_read_connection_is_read_only(self) -> None:
        from north_start_ecomm_mcp.common.database import DatabaseGateway

        gateway = DatabaseGateway(self.path)
        with self.assertRaises(sqlite3.OperationalError):
            gateway.read(
                "INSERT INTO outbox (id, customer, body) VALUES ('x', 'y', 'z')"
            )
        remaining = gateway.read("SELECT COUNT(*) AS n FROM outbox")
        self.assertEqual(remaining[0]["n"], 0)

    def test_default_path_is_under_runtime(self) -> None:
        from north_start_ecomm_mcp.common.database import company_db_path

        previous = os.environ.pop("NORTHSTAR_COMPANY_DB", None)
        try:
            path = company_db_path()
        finally:
            if previous is not None:
                os.environ["NORTHSTAR_COMPANY_DB"] = previous
        self.assertEqual(path.name, "company.db")
        self.assertEqual(path.parent.name, ".runtime")
        self.assertEqual(path.parent.parent.name, "north-start-ecomm-mcp")

    def test_domain_packages_do_not_import_the_gateway(self) -> None:
        domains = PACKAGE / "domains"
        files = list(domains.rglob("*.py")) if domains.exists() else []
        for path in files:
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                modules: list[str] = []
                if isinstance(node, ast.Import):
                    modules = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module:
                    modules = [node.module]
                for name in modules:
                    self.assertNotIn("common.database", name)
