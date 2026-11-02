import asyncio
import os
import tempfile
import unittest
from pathlib import Path

from starlette.requests import Request

PROJECT = Path(__file__).resolve().parents[1]
PACKAGE = PROJECT / "north_start_ecomm_mcp"


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


class CustomerBriefTests(unittest.TestCase):
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

    def test_sales_lookup_of_acme_returns_the_seed(self) -> None:
        from fastapi.testclient import TestClient
        from north_start_ecomm_mcp.app.main import create_app

        with TestClient(create_app()) as client:
            response = client.post(
                "/api/customer/brief",
                headers={"X-Employee-Role": "sales"},
                json={"req": {"customer": "Acme"}, "resp": {}},
            )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["req"]["role"], "sales")
        self.assertFalse(body["resp"]["denied"])
        self.assertEqual(
            body["resp"]["records"],
            [
                {
                    "id": "C-101",
                    "name": "Acme",
                    "need": "Unify weekly sales reporting across three teams",
                    "contact": "buyer@acme.example",
                }
            ],
        )

    def test_unknown_name_returns_an_empty_list(self) -> None:
        from fastapi.testclient import TestClient
        from north_start_ecomm_mcp.app.main import create_app

        with TestClient(create_app()) as client:
            response = client.post(
                "/api/customer/brief",
                headers={"X-Employee-Role": "sales"},
                json={"req": {"customer": "Nobody"}, "resp": {}},
            )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["resp"]["records"], [])
        self.assertFalse(body["resp"]["denied"])

    def test_name_match_is_case_insensitive(self) -> None:
        from fastapi.testclient import TestClient
        from north_start_ecomm_mcp.app.main import create_app

        with TestClient(create_app()) as client:
            response = client.post(
                "/api/customer/brief",
                headers={"X-Employee-Role": "engineering"},
                json={"req": {"customer": "acme", "role": "finance"}, "resp": {}},
            )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["req"]["role"], "engineering")
        self.assertEqual(body["resp"]["records"][0]["id"], "C-101")
        self.assertEqual(body["resp"]["records"][0]["name"], "Acme")

    def test_missing_role_is_denied_and_discards_client_records(self) -> None:
        from fastapi.testclient import TestClient
        from north_start_ecomm_mcp.app.main import create_app

        planted = {
            "id": "FAKE",
            "name": "Acme",
            "need": "planted",
            "contact": "planted@example",
        }
        with TestClient(create_app()) as client:
            response = client.post(
                "/api/customer/brief",
                json={
                    "req": {"customer": "Acme", "role": "sales"},
                    "resp": {"records": [planted]},
                },
            )
        self.assertEqual(response.status_code, 403)
        body = response.json()
        self.assertTrue(body["resp"]["denied"])
        self.assertEqual(body["resp"]["records"], [])
        self.assertEqual(body["resp"]["message"], "Unknown employee role: unknown.")
        self.assertEqual(body["req"]["role"], "")

    def test_dao_reads_the_customer_field_and_ignores_role(self) -> None:
        from north_start_ecomm_mcp.domains.customer.daos.objects_factory import (
            CustomerDaoFactory,
        )
        from north_start_ecomm_mcp.domains.customer.dtos.domainCtx import CustomerCtx
        from north_start_ecomm_mcp.domains.customer.dtos.domainReq import CustomerReq

        ctx = CustomerCtx(req=CustomerReq(customer="ACME", role="not-a-filter"))
        found = CustomerDaoFactory.get_customer_dao().find_by_name(ctx)
        self.assertEqual(found.resp.records[0].id, "C-101")
        self.assertEqual(found.req.role, "not-a-filter")

    def test_mcp_tool_uses_the_header_and_the_catalog_text(self) -> None:
        from fastmcp.server.http import _current_http_request

        from north_start_ecomm_mcp.app.mcp_server import build_mcp_server
        from north_start_ecomm_mcp.domains.customer.dtos.domainCtx import CustomerCtx
        from north_start_ecomm_mcp.domains.customer.dtos.domainReq import CustomerReq
        from north_start_ecomm_mcp.domains.customer.mcp_tools.objects_factory import (
            CustomerBriefToolFactory,
        )

        server = build_mcp_server()
        tools = asyncio.run(server.list_tools())
        tool = next(item for item in tools if item.name == "customer_brief")
        self.assertIn("Cite the record id", tool.description)

        token = _current_http_request.set(_request("sales"))
        try:
            result = CustomerBriefToolFactory.get_customer_brief_tool().customer_brief(
                CustomerCtx(req=CustomerReq(customer="Acme", role="finance"))
            )
        finally:
            _current_http_request.reset(token)
        self.assertEqual(result.req.role, "sales")
        self.assertEqual(result.resp.records[0].id, "C-101")
        self.assertFalse(result.resp.denied)

    def test_closed_layer_audit_passes(self) -> None:
        from tests.closed_layer_audit import audit_package

        self.assertEqual(audit_package(PACKAGE), [])
