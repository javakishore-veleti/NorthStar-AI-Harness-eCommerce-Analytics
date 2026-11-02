import os
import tempfile
import unittest
from pathlib import Path


class MiddlewareDenialTests(unittest.TestCase):
    def setUp(self) -> None:
        from north_start_ecomm_mcp.common.singleton import Singleton

        self.tmp = tempfile.TemporaryDirectory()
        self.previous_db = os.environ.get("NORTHSTAR_COMPANY_DB")
        os.environ["NORTHSTAR_COMPANY_DB"] = str(Path(self.tmp.name) / "company.db")
        Singleton._instances.clear()

    def tearDown(self) -> None:
        from north_start_ecomm_mcp.common.singleton import Singleton

        Singleton._instances.clear()
        if self.previous_db is None:
            os.environ.pop("NORTHSTAR_COMPANY_DB", None)
        else:
            os.environ["NORTHSTAR_COMPANY_DB"] = self.previous_db
        self.tmp.cleanup()

    def test_engineering_header_still_denies_send_proposal(self) -> None:
        from fastapi.testclient import TestClient
        from north_start_ecomm_mcp.app.main import create_app
        from north_start_ecomm_mcp.common.database import DatabaseGateway

        before = int(DatabaseGateway().read("SELECT COUNT(*) AS n FROM outbox")[0]["n"])
        payload = {
            "req": {"customer": "Acme", "body": "Customer goal: x", "role": "sales"},
            "resp": {},
        }
        with TestClient(create_app()) as client:
            response = client.post(
                "/api/proposals/send",
                headers={"X-Employee-Role": "engineering"},
                json=payload,
            )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.json()["resp"]["message"],
            "Access denied: engineering cannot use send_proposal.",
        )
        after = int(DatabaseGateway().read("SELECT COUNT(*) AS n FROM outbox")[0]["n"])
        self.assertEqual(after, before)
