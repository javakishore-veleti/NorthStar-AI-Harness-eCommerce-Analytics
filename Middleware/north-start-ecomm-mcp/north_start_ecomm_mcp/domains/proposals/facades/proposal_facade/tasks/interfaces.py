from abc import ABC, abstractmethod

from north_start_ecomm_mcp.domains.proposals.dtos.domainCtx import ProposalCtx


class SendProposalTask(ABC):
    @abstractmethod
    def execute(self, ctx: ProposalCtx) -> ProposalCtx:
        """Run the task. The only argument is the domain context."""
