"""Human approval before send_proposal. The middleware writes the outbox. This module does not."""

from __future__ import annotations

from typing import Any

from mcp_client import CompanyMcpClient

INTERRUPT_ON = {"send_proposal": {"allowed_decisions": ["approve", "reject"]}}


class SendApproval:
    def __init__(self, client: CompanyMcpClient) -> None:
        self.client = client

    def decide(self, decision: str, customer: str, body: str) -> Any:
        if decision == "reject":
            return {"decision": "reject"}
        if decision != "approve":
            raise ValueError(f"Unknown approval decision: {decision}.")
        return self.client.call("send_proposal", {"customer": customer, "body": body})
