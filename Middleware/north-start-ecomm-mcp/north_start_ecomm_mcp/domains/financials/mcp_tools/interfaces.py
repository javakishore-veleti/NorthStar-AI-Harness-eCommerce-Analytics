from abc import ABC, abstractmethod

from fastmcp import FastMCP

from north_start_ecomm_mcp.domains.financials.dtos.domainCtx import FinancialsCtx


class RevenueSummaryTool(ABC):
    @abstractmethod
    def revenue_summary(self, ctx: FinancialsCtx) -> FinancialsCtx:
        """Run the tool. The only argument is the domain context."""

    @abstractmethod
    def register(self, server: FastMCP) -> None:
        """Bind this tool on the MCP server."""
