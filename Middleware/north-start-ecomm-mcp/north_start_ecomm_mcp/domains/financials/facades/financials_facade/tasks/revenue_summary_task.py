from north_start_ecomm_mcp.domains.financials.daos.objects_factory import (
    FinancialsDaoFactory,
)
from north_start_ecomm_mcp.domains.financials.dtos.domainCtx import FinancialsCtx


class RevenueSummaryTask:
    def execute(self, ctx: FinancialsCtx) -> FinancialsCtx:
        return FinancialsDaoFactory.get_financials_dao().find_by_quarter(ctx)
