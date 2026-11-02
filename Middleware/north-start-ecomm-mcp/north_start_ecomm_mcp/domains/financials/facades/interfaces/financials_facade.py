from abc import ABC, abstractmethod

from north_start_ecomm_mcp.domains.financials.dtos.domainCtx import FinancialsCtx


class FinancialsFacade(ABC):
    @abstractmethod
    def summarize(self, ctx: FinancialsCtx) -> FinancialsCtx:
        """Read a quarter's revenue. The only argument is the domain context."""
