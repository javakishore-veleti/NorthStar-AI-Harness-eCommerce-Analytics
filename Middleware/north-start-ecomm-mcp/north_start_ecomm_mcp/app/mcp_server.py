from __future__ import annotations

from fastmcp import FastMCP
from starlette.applications import Starlette

from north_start_ecomm_mcp.domains.customer.mcp_tools.customer_brief import (
    register as register_customer_brief,
)
from north_start_ecomm_mcp.domains.issues.mcp_tools.issue_lookup import (
    register as register_issue_lookup,
)
from north_start_ecomm_mcp.domains.financials.mcp_tools.revenue_summary import (
    register as register_revenue_summary,
)


def build_mcp_server() -> FastMCP:
    server = FastMCP("north-start-ecomm-mcp")
    register_customer_brief(server)
    register_issue_lookup(server)
    register_revenue_summary(server)
    return server


def build_mcp_app() -> Starlette:
    return build_mcp_server().http_app(path="/")
