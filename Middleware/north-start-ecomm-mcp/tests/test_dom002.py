import os
import tempfile
import unittest
from pathlib import Path

from starlette.requests import Request


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


class CustomerRoleTests(unittest.TestCase):
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

    def _lookup(self, role: str | None, body_role: str = "") -> object:
        from fastapi.testclient import TestClient
        from north_start_ecomm_mcp.app.main import create_app

        headers = {} if role is None else {"X-Employee-Role": role}
        with TestClient(create_app()) as client:
            return client.post(
                "/api/customer/brief",
                headers=headers,
                json={
                    "req": {"customer": "Acme", "role": body_role},
                    "resp": {
                        "records": [
                            {
                                "id": "FAKE",
                                "name": "Acme",
                                "need": "planted",
                                "contact": "planted@example",
                            }
                        ]
                    },
                },
            )

    def test_sales_engineering_and_finance_can_look_up_acme(self) -> None:
        for role in ("sales", "engineering", "finance"):
            with self.subTest(role=role):
                response = self._lookup(role, body_role="finance")
                self.assertEqual(response.status_code, 200)
                body = response.json()
                self.assertEqual(body["req"]["role"], role)
                self.assertFalse(body["resp"]["denied"])
                self.assertEqual(body["resp"]["records"][0]["id"], "C-101")
                self.assertEqual(
                    body["resp"]["records"][0]["contact"], "buyer@acme.example"
                )

    def test_header_wins_over_the_body_role(self) -> None:
        response = self._lookup("engineering", body_role="finance")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["req"]["role"], "engineering")

    def test_missing_role_is_denied_and_clears_client_records(self) -> None:
        response = self._lookup(None, body_role="sales")
        self.assertEqual(response.status_code, 403)
        body = response.json()
        self.assertEqual(body["req"]["role"], "")
        self.assertTrue(body["resp"]["denied"])
        self.assertEqual(body["resp"]["records"], [])
        self.assertEqual(body["resp"]["message"], "Unknown employee role: unknown.")

    def test_unknown_role_is_denied(self) -> None:
        response = self._lookup("intern", body_role="sales")
        self.assertEqual(response.status_code, 403)
        body = response.json()
        self.assertEqual(body["req"]["role"], "intern")
        self.assertEqual(body["resp"]["records"], [])
        self.assertEqual(body["resp"]["message"], "Unknown employee role: intern.")

    def test_known_role_without_the_operation_is_denied(self) -> None:
        from north_start_ecomm_mcp.common.access import denial_message

        self.assertIsNone(denial_message("finance", "customer_brief"))
        self.assertEqual(
            denial_message("finance", "issue_lookup"),
            "Access denied: finance cannot use issue_lookup.",
        )

    def test_mcp_denial_returns_the_context(self) -> None:
        from fastmcp.server.http import _current_http_request

        from north_start_ecomm_mcp.domains.customer.dtos.domainCtx import CustomerCtx
        from north_start_ecomm_mcp.domains.customer.dtos.domainReq import CustomerReq
        from north_start_ecomm_mcp.domains.customer.mcp_tools.objects_factory import (
            CustomerBriefToolFactory,
        )

        token = _current_http_request.set(_request(None))
        try:
            result = CustomerBriefToolFactory.get_customer_brief_tool().customer_brief(
                CustomerCtx(req=CustomerReq(customer="Acme", role="sales"))
            )
        finally:
            _current_http_request.reset(token)
        self.assertTrue(result.resp.denied)
        self.assertEqual(result.resp.records, [])
        self.assertEqual(result.resp.message, "Unknown employee role: unknown.")
        self.assertEqual(result.req.role, "")
