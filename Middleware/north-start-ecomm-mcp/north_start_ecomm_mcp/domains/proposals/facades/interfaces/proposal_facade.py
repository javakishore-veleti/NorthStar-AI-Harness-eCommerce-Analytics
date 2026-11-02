from abc import ABC, abstractmethod

from north_start_ecomm_mcp.domains.proposals.dtos.domainCtx import ProposalCtx


class ProposalFacade(ABC):
    @abstractmethod
    def send(self, ctx: ProposalCtx) -> ProposalCtx:
        """Record a proposal. The only argument is the domain context."""
