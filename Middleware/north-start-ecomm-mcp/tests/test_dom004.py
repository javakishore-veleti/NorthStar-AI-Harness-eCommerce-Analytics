import asyncio
import os
import tempfile
import unittest
from pathlib import Path

from starlette.requests import Request

PACKAGE = Path(__file__).resolve().parents[1] / "north_start_ecomm_mcp"


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


class RevenueSummaryTests(unittest.TestCase):
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

    def _summarize(self, quarter: str, role: str | None, body_role: str = "") -> object:
        from fastapi.testclient import TestClient
        from north_start_ecomm_mcp.app.main import create_app

        headers = {} if role is None else {"X-Employee-Role": role}
        with TestClient(create_app()) as client:
            return client.post(
                "/api/financials/revenue",
                headers=headers,
                json={
                    "req": {"quarter": quarter, "role": body_role},
                    "resp": {"records": [{"quarter": "planted", "amount_usd": 1}]},
                },
            )

    def test_finance_2026_q3_returns_the_seed(self) -> None:
        response = self._summarize("2026-Q3", "finance", body_role="engineering")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["req"]["role"], "finance")
        self.assertFalse(body["resp"]["denied"])
        self.assertEqual(
            body["resp"]["records"],
            [{"quarter": "2026-Q3", "amount_usd": 480000}],
        )

    def test_unknown_quarter_returns_an_empty_list(self) -> None:
        response = self._summarize("1999-Q1", "finance")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["resp"]["records"], [])
        self.assertFalse(body["resp"]["denied"])

    def test_quarter_match_is_exact(self) -> None:
        response = self._summarize("2026-q3", "finance")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["resp"]["records"], [])

    def test_engineering_is_denied(self) -> None:
        response = self._summarize("2026-Q3", "engineering")
        self.assertEqual(response.status_code, 403)
        body = response.json()
        self.assertEqual(body["resp"]["records"], [])
        self.assertTrue(body["resp"]["denied"])
        self.assertEqual(
            body["resp"]["message"],
            "Access denied: engineering cannot use revenue_summary.",
        )

    def test_mcp_tool_returns_the_seed_and_catalog_text(self) -> None:
        from fastmcp.server.http import _current_http_request

        from north_start_ecomm_mcp.app.mcp_server import build_mcp_server
        from north_start_ecomm_mcp.domains.financials.dtos.domainCtx import FinancialsCtx
        from north_start_ecomm_mcp.domains.financials.dtos.domainReq import FinancialsReq
        from north_start_ecomm_mcp.domains.financials.mcp_tools.revenue_summary import (
            revenue_summary,
        )

        server = build_mcp_server()
        tools = asyncio.run(server.list_tools())
        tool = next(item for item in tools if item.name == "revenue_summary")
        self.assertIn("Do not estimate a missing quarter", tool.description)

        token = _current_http_request.set(_request("finance"))
        try:
            result = revenue_summary(
                FinancialsCtx(req=FinancialsReq(quarter="2026-Q3", role="engineering"))
            )
        finally:
            _current_http_request.reset(token)
        self.assertEqual(result.req.role, "finance")
        self.assertEqual(result.resp.records[0].amount_usd, 480000)
        self.assertFalse(result.resp.denied)

    def test_closed_layer_audit_passes(self) -> None:
        from tests.closed_layer_audit import audit_package

        self.assertEqual(audit_package(PACKAGE), [])
