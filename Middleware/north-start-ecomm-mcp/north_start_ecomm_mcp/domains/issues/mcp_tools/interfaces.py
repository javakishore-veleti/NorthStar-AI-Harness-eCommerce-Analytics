from abc import ABC, abstractmethod

from fastmcp import FastMCP

from north_start_ecomm_mcp.domains.issues.dtos.domainCtx import IssueCtx


class IssueLookupTool(ABC):
    @abstractmethod
    def issue_lookup(self, ctx: IssueCtx) -> IssueCtx:
        """Run the tool. The only argument is the domain context."""

    @abstractmethod
    def register(self, server: FastMCP) -> None:
        """Bind this tool on the MCP server."""
