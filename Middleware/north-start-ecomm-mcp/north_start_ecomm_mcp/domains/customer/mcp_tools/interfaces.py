from abc import ABC, abstractmethod

from fastmcp import FastMCP

from north_start_ecomm_mcp.domains.customer.dtos.domainCtx import CustomerCtx


class CustomerBriefTool(ABC):
    @abstractmethod
    def customer_brief(self, ctx: CustomerCtx) -> CustomerCtx:
        """Run the tool. The only argument is the domain context."""

    @abstractmethod
    def register(self, server: FastMCP) -> None:
        """Bind this tool on the MCP server."""
