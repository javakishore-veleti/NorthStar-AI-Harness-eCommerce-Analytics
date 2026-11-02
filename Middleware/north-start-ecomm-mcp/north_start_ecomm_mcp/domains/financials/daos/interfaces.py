from abc import ABC, abstractmethod

from north_start_ecomm_mcp.domains.financials.dtos.domainCtx import FinancialsCtx


class FinancialsDao(ABC):
    @abstractmethod
    def find_by_quarter(self, ctx: FinancialsCtx) -> FinancialsCtx:
        """Read revenue by ctx.req.quarter. The match is exact."""
