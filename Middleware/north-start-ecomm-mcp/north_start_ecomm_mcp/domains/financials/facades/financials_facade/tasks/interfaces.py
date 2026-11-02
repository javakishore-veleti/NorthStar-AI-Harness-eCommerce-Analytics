from abc import ABC, abstractmethod

from north_start_ecomm_mcp.domains.financials.dtos.domainCtx import FinancialsCtx


class RevenueSummaryTask(ABC):
    @abstractmethod
    def execute(self, ctx: FinancialsCtx) -> FinancialsCtx:
        """Run the task. The only argument is the domain context."""
