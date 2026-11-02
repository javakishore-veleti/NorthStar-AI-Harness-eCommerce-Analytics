import asyncio
import os
import tempfile
import unittest
from pathlib import Path

from starlette.requests import Request

_BODY = "Customer goal: unify reporting\nProposed scope: one dashboard"
_PAIRS = (
    ("sales", "customer_brief", True),
    ("sales", "send_proposal", True),
    ("sales", "issue_lookup", False),
    ("sales", "revenue_summary", False),
    ("engineering", "customer_brief", True),
    ("engineering", "issue_lookup", True),
    ("engineering", "send_proposal", False),
    ("engineering", "revenue_summary", False),
    ("finance", "customer_brief", True),
    ("finance", "revenue_summary", True),
    ("finance", "issue_lookup", False),
    ("finance", "send_proposal", False),
)


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


class RoleMatrixTests(unittest.TestCase):
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
        from north_start_ecomm_mcp.common.database import DatabaseGateway

        rows = DatabaseGateway().read("SELECT COUNT(*) AS n FROM outbox")
        return int(rows[0]["n"])

    def _rest(self, role: str, operation: str):
        from fastapi.testclient import TestClient
        from north_start_ecomm_mcp.app.main import create_app

        payloads = {
            "customer_brief": (
                "/api/customer/brief",
                {"req": {"customer": "Acme", "role": "finance"}, "resp": {}},
            ),
            "issue_lookup": (
                "/api/issues/lookup",
                {"req": {"customer": "Beacon", "role": "sales"}, "resp": {}},
            ),
            "revenue_summary": (
                "/api/financials/revenue",
                {"req": {"quarter": "2026-Q3", "role": "sales"}, "resp": {}},
            ),
            "send_proposal": (
                "/api/proposals/send",
                {"req": {"customer": "Acme", "body": _BODY, "role": "engineering"}, "resp": {}},
            ),
        }
        path, payload = payloads[operation]
        with TestClient(create_app()) as client:
            return client.post(path, headers={"X-Employee-Role": role}, json=payload)

    def _mcp(self, role: str, operation: str):
        from fastmcp.server.http import _current_http_request

        from north_start_ecomm_mcp.domains.customer.dtos.domainCtx import CustomerCtx
        from north_start_ecomm_mcp.domains.customer.dtos.domainReq import CustomerReq
        from north_start_ecomm_mcp.domains.customer.mcp_tools.objects_factory import (
            CustomerBriefToolFactory,
        )
        from north_start_ecomm_mcp.domains.financials.dtos.domainCtx import FinancialsCtx
        from north_start_ecomm_mcp.domains.financials.dtos.domainReq import FinancialsReq
        from north_start_ecomm_mcp.domains.financials.mcp_tools.objects_factory import (
            RevenueSummaryToolFactory,
        )
        from north_start_ecomm_mcp.domains.issues.dtos.domainCtx import IssueCtx
        from north_start_ecomm_mcp.domains.issues.dtos.domainReq import IssueReq
        from north_start_ecomm_mcp.domains.issues.mcp_tools.objects_factory import (
            IssueLookupToolFactory,
        )
        from north_start_ecomm_mcp.domains.proposals.dtos.domainCtx import ProposalCtx
        from north_start_ecomm_mcp.domains.proposals.dtos.domainReq import ProposalReq
        from north_start_ecomm_mcp.domains.proposals.mcp_tools.objects_factory import (
            SendProposalToolFactory,
        )

        token = _current_http_request.set(_request(role))
        try:
            if operation == "customer_brief":
                return CustomerBriefToolFactory.get_customer_brief_tool().customer_brief(
                    CustomerCtx(req=CustomerReq(customer="Acme", role="finance"))
                )
            if operation == "issue_lookup":
                return IssueLookupToolFactory.get_issue_lookup_tool().issue_lookup(
                    IssueCtx(req=IssueReq(customer="Beacon", role="sales"))
                )
            if operation == "revenue_summary":
                return RevenueSummaryToolFactory.get_revenue_summary_tool().revenue_summary(
                    FinancialsCtx(req=FinancialsReq(quarter="2026-Q3", role="sales"))
                )
            return SendProposalToolFactory.get_send_proposal_tool().send_proposal(
                ProposalCtx(req=ProposalReq(customer="Acme", body=_BODY, role="engineering"))
            )
        finally:
            _current_http_request.reset(token)

    def _assert_granted(self, operation: str, body: dict) -> None:
        resp = body["resp"]
        self.assertFalse(resp["denied"])
        if operation == "customer_brief":
            self.assertEqual(resp["records"][0]["id"], "C-101")
        elif operation == "issue_lookup":
            self.assertEqual(resp["records"][0]["id"], "INC-42")
        elif operation == "revenue_summary":
            self.assertEqual(resp["records"][0]["amount_usd"], 480000)
        else:
            self.assertEqual(resp["status"], "simulated_send")
            self.assertEqual(len(resp["receipt"]), 16)

    def test_twelve_pairs_match_the_matrix(self) -> None:
        self.assertEqual(len(_PAIRS), 12)
        for role, operation, allowed in _PAIRS:
            before = self._outbox_count()
            response = self._rest(role, operation)
            body = response.json()
            self.assertEqual(body["req"]["role"], role)
            if allowed:
                self.assertEqual(response.status_code, 200, msg=f"{role} {operation}")
                self._assert_granted(operation, body)
            else:
                self.assertEqual(response.status_code, 403, msg=f"{role} {operation}")
                self.assertTrue(body["resp"]["denied"])
                self.assertEqual(
                    body["resp"]["message"],
                    f"Access denied: {role} cannot use {operation}.",
                )
                self.assertEqual(self._outbox_count(), before)
            mcp = self._mcp(role, operation)
            self.assertEqual(mcp.resp.denied, body["resp"]["denied"])
            self.assertEqual(mcp.resp.message, body["resp"]["message"])

    def test_unknown_role_uses_the_unknown_role_message(self) -> None:
        response = self._rest("intern", "customer_brief")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.json()["resp"]["message"],
            "Unknown employee role: intern.",
        )
        mcp = self._mcp("intern", "customer_brief")
        self.assertEqual(mcp.resp.message, "Unknown employee role: intern.")
