from abc import ABC, abstractmethod

from fastmcp import FastMCP

from north_start_ecomm_mcp.domains.proposals.dtos.domainCtx import ProposalCtx


class SendProposalTool(ABC):
    @abstractmethod
    def send_proposal(self, ctx: ProposalCtx) -> ProposalCtx:
        """Run the tool. The only argument is the domain context."""

    @abstractmethod
    def register(self, server: FastMCP) -> None:
        """Bind this tool on the MCP server."""
