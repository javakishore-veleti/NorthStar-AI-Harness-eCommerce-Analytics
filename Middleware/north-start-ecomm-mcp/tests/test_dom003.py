import os
import tempfile
import unittest
from pathlib import Path

from starlette.requests import Request

PACKAGE = Path(__file__).resolve().parents[1] / "north_start_ecomm_mcp"

_BEACON = {
    "id": "INC-42",
    "customer": "Beacon",
    "symptom": "Sync stalls when the upstream API returns HTTP 429",
    "owner": "Data Platform",
}


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


class IssueLookupTests(unittest.TestCase):
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

    def _lookup(self, customer: str, role: str | None, body_role: str = "") -> object:
        from fastapi.testclient import TestClient
        from north_start_ecomm_mcp.app.main import create_app

        headers = {} if role is None else {"X-Employee-Role": role}
        with TestClient(create_app()) as client:
            return client.post(
                "/api/issues/lookup",
                headers=headers,
                json={
                    "req": {"customer": customer, "role": body_role},
                    "resp": {"records": [_BEACON]},
                },
            )

    def test_engineering_lookup_of_beacon_returns_the_seed(self) -> None:
        response = self._lookup("Beacon", "engineering", body_role="finance")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["req"]["role"], "engineering")
        self.assertFalse(body["resp"]["denied"])
        self.assertEqual(body["resp"]["records"], [_BEACON])

    def test_unknown_customer_returns_an_empty_list(self) -> None:
        response = self._lookup("Nobody", "engineering")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["resp"]["records"], [])
        self.assertFalse(body["resp"]["denied"])

    def test_name_match_is_case_insensitive(self) -> None:
        response = self._lookup("beacon", "engineering")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["resp"]["records"], [_BEACON])

    def test_finance_is_denied(self) -> None:
        response = self._lookup("Beacon", "finance")
        self.assertEqual(response.status_code, 403)
        body = response.json()
        self.assertEqual(body["resp"]["records"], [])
        self.assertTrue(body["resp"]["denied"])
        self.assertEqual(
            body["resp"]["message"],
            "Access denied: finance cannot use issue_lookup.",
        )

    def test_mcp_tool_returns_the_seed_and_catalog_text(self) -> None:
        import asyncio

        from fastmcp.server.http import _current_http_request

        from north_start_ecomm_mcp.app.mcp_server import build_mcp_server
        from north_start_ecomm_mcp.domains.issues.dtos.domainCtx import IssueCtx
        from north_start_ecomm_mcp.domains.issues.dtos.domainReq import IssueReq
        from north_start_ecomm_mcp.domains.issues.mcp_tools.issue_lookup import (
            issue_lookup,
        )

        server = build_mcp_server()
        tools = asyncio.run(server.list_tools())
        tool = next(item for item in tools if item.name == "issue_lookup")
        self.assertIn("does not resolve or modify the issue", tool.description)

        token = _current_http_request.set(_request("engineering"))
        try:
            result = issue_lookup(IssueCtx(req=IssueReq(customer="Beacon", role="finance")))
        finally:
            _current_http_request.reset(token)
        self.assertEqual(result.req.role, "engineering")
        self.assertEqual(result.resp.records[0].id, "INC-42")
        self.assertFalse(result.resp.denied)

    def test_closed_layer_audit_passes(self) -> None:
        from tests.closed_layer_audit import audit_package

        self.assertEqual(audit_package(PACKAGE), [])
