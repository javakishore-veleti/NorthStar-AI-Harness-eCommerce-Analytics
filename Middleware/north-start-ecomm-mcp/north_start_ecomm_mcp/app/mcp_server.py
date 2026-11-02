from __future__ import annotations

from fastmcp import FastMCP
from starlette.applications import Starlette

from north_start_ecomm_mcp.domains.customer.mcp_tools.objects_factory import (
    CustomerBriefToolFactory,
)
from north_start_ecomm_mcp.domains.financials.mcp_tools.objects_factory import (
    RevenueSummaryToolFactory,
)
from north_start_ecomm_mcp.domains.issues.mcp_tools.objects_factory import (
    IssueLookupToolFactory,
)
from north_start_ecomm_mcp.domains.proposals.mcp_tools.objects_factory import (
    SendProposalToolFactory,
)


def build_mcp_server() -> FastMCP:
    server = FastMCP("north-start-ecomm-mcp")
    CustomerBriefToolFactory.get_customer_brief_tool().register(server)
    IssueLookupToolFactory.get_issue_lookup_tool().register(server)
    RevenueSummaryToolFactory.get_revenue_summary_tool().register(server)
    SendProposalToolFactory.get_send_proposal_tool().register(server)
    return server


def build_mcp_app() -> Starlette:
    return build_mcp_server().http_app(path="/")
