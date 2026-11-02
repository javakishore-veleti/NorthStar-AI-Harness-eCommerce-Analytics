from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_headers

from north_start_ecomm_mcp.app.http_role import role_from_header
from north_start_ecomm_mcp.common.singleton import Singleton
from north_start_ecomm_mcp.domains.financials.dtos.domainCtx import FinancialsCtx
from north_start_ecomm_mcp.domains.financials.facades.objects_factory import FinancialsFacadeFactory
from north_start_ecomm_mcp.domains.financials.mcp_tools.interfaces import RevenueSummaryTool

_DESCRIPTION = (
    "read the recorded revenue total for a quarter. Do not estimate a missing quarter. The tool does not modify financial records."
)


class RevenueSummaryToolImpl(RevenueSummaryTool, metaclass=Singleton):
    def revenue_summary(self, ctx: FinancialsCtx) -> FinancialsCtx:
        headers = get_http_headers(include={"x-employee-role"})
        ctx.req.role = role_from_header(headers.get("x-employee-role"))
        return FinancialsFacadeFactory.get_financials_facade().summarize(ctx)

    def register(self, server: FastMCP) -> None:
        server.tool(self.revenue_summary, name="revenue_summary", description=_DESCRIPTION)
