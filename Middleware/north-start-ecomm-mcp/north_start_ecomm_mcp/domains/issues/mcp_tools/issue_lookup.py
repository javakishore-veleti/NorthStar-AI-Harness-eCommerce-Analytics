from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_headers

from north_start_ecomm_mcp.app.http_role import role_from_header
from north_start_ecomm_mcp.domains.issues.dtos.domainCtx import IssueCtx
from north_start_ecomm_mcp.domains.issues.facades.objects_factory import (
    IssueFacadeFactory,
)

_DESCRIPTION = (
    "look up a customer's reported engineering issue. The lookup does not "
    "resolve or modify the issue."
)


def issue_lookup(ctx: IssueCtx) -> IssueCtx:
    headers = get_http_headers(include={"x-employee-role"})
    ctx.req.role = role_from_header(headers.get("x-employee-role"))
    return IssueFacadeFactory.get_issue_facade().lookup(ctx)


def register(server: FastMCP) -> None:
    server.tool(issue_lookup, name="issue_lookup", description=_DESCRIPTION)
