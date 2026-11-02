from north_start_ecomm_mcp.common.access import denial_message
from north_start_ecomm_mcp.common.singleton import Singleton
from north_start_ecomm_mcp.domains.financials.dtos.domainCtx import FinancialsCtx
from north_start_ecomm_mcp.domains.financials.dtos.domainResp import FinancialsResp
from north_start_ecomm_mcp.domains.financials.facades.financials_facade.tasks.objects_factory import (
    RevenueSummaryTaskFactory,
)
from north_start_ecomm_mcp.domains.financials.facades.interfaces.financials_facade import (
    FinancialsFacade,
)

_OPERATION = "revenue_summary"


class FinancialsFacadeImpl(FinancialsFacade, metaclass=Singleton):
    def summarize(self, ctx: FinancialsCtx) -> FinancialsCtx:
        ctx.resp = FinancialsResp()
        message = denial_message(ctx.req.role, _OPERATION)
        if message is not None:
            ctx.resp.denied = True
            ctx.resp.message = message
            return ctx
        return RevenueSummaryTaskFactory.get_revenue_summary_task().execute(ctx)
