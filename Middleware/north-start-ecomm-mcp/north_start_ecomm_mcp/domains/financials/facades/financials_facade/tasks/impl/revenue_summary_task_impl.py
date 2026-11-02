from north_start_ecomm_mcp.common.singleton import Singleton
from north_start_ecomm_mcp.domains.financials.daos.objects_factory import FinancialsDaoFactory
from north_start_ecomm_mcp.domains.financials.dtos.domainCtx import FinancialsCtx
from north_start_ecomm_mcp.domains.financials.facades.financials_facade.tasks.interfaces import RevenueSummaryTask


class RevenueSummaryTaskImpl(RevenueSummaryTask, metaclass=Singleton):
    def execute(self, ctx: FinancialsCtx) -> FinancialsCtx:
        return FinancialsDaoFactory.get_financials_dao().find_by_quarter(ctx)
