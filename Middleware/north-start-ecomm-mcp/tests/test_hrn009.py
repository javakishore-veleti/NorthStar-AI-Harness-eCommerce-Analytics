import os
import socket
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "harness"))


class TeachingPromptTests(unittest.TestCase):
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

    def _outbox_count(self) -> int:
        from north_start_ecomm_mcp.common.singleton import Singleton
        from north_start_ecomm_mcp.common.database import DatabaseGateway

        Singleton._instances.clear()
        rows = DatabaseGateway().read("SELECT COUNT(*) AS n FROM outbox")
        return int(rows[0]["n"])

    def test_cost_note_names_credentials_without_copying_values(self) -> None:
        from teaching_prompts import provider_cost_note

        os.environ["OPENAI_API_KEY"] = "sk-do-not-print"
        try:
            note = provider_cost_note()
        finally:
            os.environ.pop("OPENAI_API_KEY", None)
        self.assertFalse(note["provider_called"])
        self.assertEqual(note["cost_usd"], 0)
        self.assertIsNone(note["observed_model_output"])
        self.assertIn("OPENAI_API_KEY", note["credential_names_present"])
        self.assertNotIn("sk-do-not-print", str(note))

    def test_three_scripted_prompts_cite_the_seed_and_do_not_send(self) -> None:
        import httpx
        import uvicorn
        from mcp_client import CompanyMcpClient
        from north_start_ecomm_mcp.app.main import create_app
        from teaching_prompts import engineering_triage, finance_revenue, sales_proposal

        sock = socket.socket()
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
        sock.close()
        server = uvicorn.Server(
            uvicorn.Config(create_app(), host="127.0.0.1", port=port, log_level="error")
        )
        server.install_signal_handlers = False
        thread = threading.Thread(target=server.run, daemon=True)
        thread.start()
        deadline = time.time() + 10
        while time.time() < deadline:
            try:
                if httpx.get(f"http://127.0.0.1:{port}/health").status_code == 200:
                    break
            except httpx.HTTPError:
                time.sleep(0.05)
        else:
            self.fail("middleware did not start")
        try:
            sales = CompanyMcpClient(f"http://127.0.0.1:{port}/mcp", "sales")
            proposal = sales_proposal(sales, Path(self.tmp.name), "sales-acme")
            self.assertEqual(proposal["record_id"], "C-101")
            self.assertFalse(proposal["sent"])
            text = proposal["path"].read_text(encoding="utf-8")
            for section in ("Customer goal", "Proposed scope", "Assumptions", "Next steps"):
                self.assertIn(section, text)
            self.assertIn("awaiting confirmation", text)
            self.assertIn("C-101", text)
            self.assertEqual(self._outbox_count(), 0)

            engineering = CompanyMcpClient(f"http://127.0.0.1:{port}/mcp", "engineering")
            triage = engineering_triage(engineering)
            self.assertEqual(triage["issue_id"], "INC-42")
            self.assertEqual(triage["customer_id"], "C-102")

            finance = CompanyMcpClient(f"http://127.0.0.1:{port}/mcp", "finance")
            revenue = finance_revenue(finance)
            self.assertEqual(revenue["quarter"], "2026-Q3")
            self.assertEqual(revenue["amount_usd"], 480000)
            self.assertEqual(self._outbox_count(), 0)
        finally:
            server.should_exit = True
            thread.join(timeout=5)
