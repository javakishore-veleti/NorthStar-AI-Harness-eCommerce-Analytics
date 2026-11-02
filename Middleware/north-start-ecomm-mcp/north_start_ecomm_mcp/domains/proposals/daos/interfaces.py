from abc import ABC, abstractmethod

from north_start_ecomm_mcp.domains.proposals.dtos.domainCtx import ProposalCtx


class ProposalDao(ABC):
    @abstractmethod
    def insert_outbox(self, ctx: ProposalCtx) -> ProposalCtx:
        """Insert the proposal once. The receipt is the outbox id."""
