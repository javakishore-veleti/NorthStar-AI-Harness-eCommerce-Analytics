import os
import tempfile
import unittest
from pathlib import Path

_BODY = "Customer goal: unify reporting\nProposed scope: one dashboard"
_UNKNOWN = "Unknown customer. Look up the customer before sending."
_SEEDED = ("receipt-1", "Acme", "already recorded")


class ProposalDenialTests(unittest.TestCase):
    def setUp(self) -> None:
        from north_start_ecomm_mcp.common.database import DatabaseGateway
        from north_start_ecomm_mcp.common.singleton import Singleton

        self.tmp = tempfile.TemporaryDirectory()
        self.previous_db = os.environ.get("NORTHSTAR_COMPANY_DB")
        os.environ["NORTHSTAR_COMPANY_DB"] = str(Path(self.tmp.name) / "company.db")
        Singleton._instances.clear()
        DatabaseGateway().write(
            "INSERT INTO outbox (id, customer, body) VALUES (?, ?, ?)",
            _SEEDED,
        )

    def tearDown(self) -> None:
        from north_start_ecomm_mcp.common.singleton import Singleton

        Singleton._instances.clear()
        if self.previous_db is None:
            os.environ.pop("NORTHSTAR_COMPANY_DB", None)
        else:
            os.environ["NORTHSTAR_COMPANY_DB"] = self.previous_db
        self.tmp.cleanup()

    def _send(self, customer: str, role: str | None, body_role: str = "") -> object:
        from fastapi.testclient import TestClient
        from north_start_ecomm_mcp.app.main import create_app

        headers = {} if role is None else {"X-Employee-Role": role}
        with TestClient(create_app()) as client:
            return client.post(
                "/api/proposals/send",
                headers=headers,
                json={
                    "req": {"customer": customer, "body": _BODY, "role": body_role},
                    "resp": {"status": "planted", "receipt": "planted", "customer": "planted"},
                },
            )

    def _outbox(self) -> list[tuple]:
        from north_start_ecomm_mcp.common.database import DatabaseGateway

        rows = DatabaseGateway().read("SELECT id, customer, body FROM outbox")
        return [tuple(row) for row in rows]

    def test_unknown_customer_writes_no_outbox_row(self) -> None:
        response = self._send("Nobody", "sales")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertFalse(body["resp"]["denied"])
        self.assertEqual(body["resp"]["message"], _UNKNOWN)
        self.assertEqual(body["resp"]["status"], "")
        self.assertEqual(body["resp"]["receipt"], "")
        self.assertEqual(self._outbox(), [_SEEDED])

    def test_engineering_is_denied_before_lookup(self) -> None:
        response = self._send("Acme", "engineering", body_role="sales")
        self.assertEqual(response.status_code, 403)
        body = response.json()
        self.assertEqual(body["req"]["role"], "engineering")
        self.assertTrue(body["resp"]["denied"])
        self.assertEqual(
            body["resp"]["message"],
            "Access denied: engineering cannot use send_proposal.",
        )
        self.assertEqual(body["resp"]["status"], "")
        self.assertEqual(self._outbox(), [_SEEDED])

    def test_finance_is_denied_and_leaves_the_outbox_unchanged(self) -> None:
        response = self._send("Acme", "finance")
        self.assertEqual(response.status_code, 403)
        body = response.json()
        self.assertTrue(body["resp"]["denied"])
        self.assertEqual(
            body["resp"]["message"],
            "Access denied: finance cannot use send_proposal.",
        )
        self.assertEqual(self._outbox(), [_SEEDED])
