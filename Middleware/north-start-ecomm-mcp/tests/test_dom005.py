import asyncio
import hashlib
import os
import tempfile
import unittest
from pathlib import Path

from starlette.requests import Request

PACKAGE = Path(__file__).resolve().parents[1] / "north_start_ecomm_mcp"
_BODY = "Customer goal: unify reporting\nProposed scope: one dashboard"


def _request(role: str | None) -> Request:
    headers: list[tuple[bytes, bytes]] = []
    if role is not None:
        headers.append((b"x-employee-role", role.encode()))
    scope = {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.3"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": "/mcp",
        "raw_path": b"/mcp",
        "query_string": b"",
        "headers": headers,
        "client": ("127.0.0.1", 12345),
        "server": ("127.0.0.1", 8080),
    }
    return Request(scope)


def _receipt(customer: str, body: str) -> str:
    return hashlib.sha256(f"{customer}\0{body}".encode()).hexdigest()[:16]


class SendProposalTests(unittest.TestCase):
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
                    "resp": {
                        "status": "planted",
                        "receipt": "planted",
                        "customer": "planted",
                    },
                },
            )

    def _outbox(self) -> list[tuple]:
        from north_start_ecomm_mcp.common.database import DatabaseGateway

        rows = DatabaseGateway().read("SELECT id, customer, body FROM outbox")
        return [tuple(row) for row in rows]

    def test_sales_send_for_acme_returns_simulated_send(self) -> None:
        response = self._send("acme", "sales", body_role="engineering")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["req"]["role"], "sales")
        self.assertEqual(body["req"]["customer"], "Acme")
        self.assertFalse(body["resp"]["denied"])
        self.assertEqual(body["resp"]["status"], "simulated_send")
        self.assertEqual(body["resp"]["customer"], "Acme")
        self.assertEqual(body["resp"]["receipt"], _receipt("Acme", _BODY))
        self.assertEqual(len(body["resp"]["receipt"]), 16)
        self.assertEqual(self._outbox(), [(body["resp"]["receipt"], "Acme", _BODY)])

    def test_repeat_send_reuses_the_receipt(self) -> None:
        first = self._send("Acme", "sales")
        second = self._send("Acme", "sales")
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        receipt = first.json()["resp"]["receipt"]
        self.assertEqual(second.json()["resp"]["receipt"], receipt)
        self.assertEqual(self._outbox(), [(receipt, "Acme", _BODY)])

    def test_mcp_tool_records_the_outbox_and_states_email_is_not_sent(self) -> None:
        from fastmcp.server.http import _current_http_request

        from north_start_ecomm_mcp.app.mcp_server import build_mcp_server
        from north_start_ecomm_mcp.domains.proposals.dtos.domainCtx import ProposalCtx
        from north_start_ecomm_mcp.domains.proposals.dtos.domainReq import ProposalReq
        from north_start_ecomm_mcp.domains.proposals.mcp_tools.send_proposal import (
            send_proposal,
        )

        server = build_mcp_server()
        tools = asyncio.run(server.list_tools())
        tool = next(item for item in tools if item.name == "send_proposal")
        self.assertIn("The tool does not send email.", tool.description)

        token = _current_http_request.set(_request("sales"))
        try:
            result = send_proposal(
                ProposalCtx(req=ProposalReq(customer="Acme", body=_BODY, role="finance"))
            )
        finally:
            _current_http_request.reset(token)
        self.assertEqual(result.req.role, "sales")
        self.assertEqual(result.resp.status, "simulated_send")
        self.assertEqual(result.resp.receipt, _receipt("Acme", _BODY))
        self.assertFalse(result.resp.denied)

    def test_closed_layer_audit_passes(self) -> None:
        from tests.closed_layer_audit import audit_package

        self.assertEqual(audit_package(PACKAGE), [])
