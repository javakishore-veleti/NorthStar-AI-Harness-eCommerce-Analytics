"""Role-to-operation matrix from DESIGN.md. Facades read it. DAOs do not."""

from __future__ import annotations

MATRIX: dict[str, frozenset[str]] = {
    "sales": frozenset({"customer_brief", "send_proposal"}),
    "engineering": frozenset({"customer_brief", "issue_lookup"}),
    "finance": frozenset({"customer_brief", "revenue_summary"}),
}


def denial_message(role: str, operation: str) -> str | None:
    if role not in MATRIX:
        shown = role if role else "unknown"
        return f"Unknown employee role: {shown}."
    if operation not in MATRIX[role]:
        return f"Access denied: {role} cannot use {operation}."
    return None
