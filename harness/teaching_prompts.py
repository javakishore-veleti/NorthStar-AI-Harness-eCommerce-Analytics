"""Scripted teaching contracts. These do not call a model provider."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from mcp_client import CompanyMcpClient
from workspace import save_work_file

_CREDENTIAL_NAMES = ("OPENAI_API_KEY", "ANTHROPIC_API_KEY")


def provider_cost_note() -> dict[str, Any]:
    """Names of set credentials only. Values are never copied into the note."""
    return {
        "provider_called": False,
        "cost_usd": 0,
        "credential_names_present": [name for name in _CREDENTIAL_NAMES if os.environ.get(name)],
        "observed_model_output": None,
        "note": "Scripted contract. No model transcript.",
    }


def _records(result: Any) -> list[Any]:
    data = getattr(result, "data", result)
    resp = data.get("resp", data) if isinstance(data, dict) else getattr(data, "resp", data)
    records = resp.get("records", []) if isinstance(resp, dict) else getattr(resp, "records", [])
    return list(records)


def _field(record: Any, name: str) -> Any:
    if isinstance(record, dict):
        return record.get(name)
    return getattr(record, name)


def sales_proposal(client: CompanyMcpClient, repo_root: Path, task_id: str) -> dict[str, Any]:
    records = _records(client.call("customer_brief", {"customer": "Acme"}))
    record = records[0]
    record_id = str(_field(record, "id"))
    need = str(_field(record, "need"))
    draft = (
        f"Customer goal: {need}\n"
        "Proposed scope: Connect the three teams to one weekly sales report.\n"
        "Assumptions: Pricing and timeline are awaiting confirmation.\n"
        "Next steps: Review the draft with the employee before any send.\n"
        f"Record: {record_id}\n"
    )
    path = save_work_file(repo_root, task_id, "proposal.md", draft)
    return {"record_id": record_id, "path": path, "draft": draft, "sent": False}


def engineering_triage(client: CompanyMcpClient) -> dict[str, str]:
    issues = _records(client.call("issue_lookup", {"customer": "Beacon"}))
    customers = _records(client.call("customer_brief", {"customer": "Beacon"}))
    return {
        "issue_id": str(_field(issues[0], "id")),
        "customer_id": str(_field(customers[0], "id")),
        "symptom": str(_field(issues[0], "symptom")),
    }


def finance_revenue(client: CompanyMcpClient) -> dict[str, Any]:
    records = _records(client.call("revenue_summary", {"quarter": "2026-Q3"}))
    record = records[0]
    return {
        "quarter": str(_field(record, "quarter")),
        "amount_usd": int(_field(record, "amount_usd")),
    }
