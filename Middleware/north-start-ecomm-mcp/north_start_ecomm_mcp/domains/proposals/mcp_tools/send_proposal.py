from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_headers

from north_start_ecomm_mcp.app.http_role import role_from_header
from north_start_ecomm_mcp.domains.proposals.dtos.domainCtx import ProposalCtx
from north_start_ecomm_mcp.domains.proposals.facades.objects_factory import (
    ProposalFacadeFactory,
)

_DESCRIPTION = (
    "record a customer proposal in the local outbox. The body carries "
    "Customer goal, Proposed scope, Assumptions, and Next steps. Repeated "
    "identical proposals reuse the receipt. The tool does not send email."
)


def send_proposal(ctx: ProposalCtx) -> ProposalCtx:
    headers = get_http_headers(include={"x-employee-role"})
    ctx.req.role = role_from_header(headers.get("x-employee-role"))
    return ProposalFacadeFactory.get_proposal_facade().send(ctx)


def register(server: FastMCP) -> None:
    server.tool(send_proposal, name="send_proposal", description=_DESCRIPTION)
