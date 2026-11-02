from typing import Annotated

from fastapi import Header
from fastapi.responses import JSONResponse

from north_start_ecomm_mcp.app.http_role import role_from_header
from north_start_ecomm_mcp.common.singleton import Singleton
from north_start_ecomm_mcp.domains.financials.api.interfaces import RevenueSummaryApi
from north_start_ecomm_mcp.domains.financials.dtos.domainCtx import FinancialsCtx
from north_start_ecomm_mcp.domains.financials.facades.objects_factory import FinancialsFacadeFactory


class RevenueSummaryApiImpl(RevenueSummaryApi, metaclass=Singleton):
    def revenue_summary(
        self,
        ctx: FinancialsCtx,
        x_employee_role: Annotated[str | None, Header(alias="X-Employee-Role")] = None,
    ) -> JSONResponse:
        ctx.req.role = role_from_header(x_employee_role)
        result = FinancialsFacadeFactory.get_financials_facade().summarize(ctx)
        status_code = 403 if result.resp.denied else 200
        return JSONResponse(status_code=status_code, content=result.model_dump())
