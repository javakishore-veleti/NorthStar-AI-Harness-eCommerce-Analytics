import os
import socket
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

HARNESS = Path(__file__).resolve().parents[3] / "harness"
sys.path.insert(0, str(HARNESS))

_BODY = "Customer goal: unify reporting\nProposed scope: one dashboard"


def _status(result):
    data = getattr(result, "data", result)
    if isinstance(data, dict):
        resp = data.get("resp", data)
        return resp.get("status")
    resp = getattr(data, "resp", None)
    return getattr(resp, "status", None)


class SendApprovalTests(unittest.TestCase):
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

    def test_reject_writes_zero_outbox_rows(self) -> None:
        from approval import SendApproval

        class Boom:
            def call(self, tool_name, req):
                raise AssertionError("reject must not call the middleware")

        before = self._outbox_count()
        result = SendApproval(Boom()).decide("reject", "Acme", _BODY)
        self.assertEqual(result, {"decision": "reject"})
        self.assertEqual(self._outbox_count(), before)
        self.assertEqual(before, 0)

    def test_approve_writes_one_row_and_returns_simulated_send(self) -> None:
        import httpx
        import uvicorn
        from approval import SendApproval
        from mcp_client import CompanyMcpClient
        from north_start_ecomm_mcp.app.main import create_app

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
            self.assertEqual(self._outbox_count(), 0)
            client = CompanyMcpClient(f"http://127.0.0.1:{port}/mcp", "sales")
            result = SendApproval(client).decide("approve", "Acme", _BODY)
            self.assertEqual(_status(result), "simulated_send")
            self.assertEqual(self._outbox_count(), 1)
        finally:
            server.should_exit = True
            thread.join(timeout=5)
