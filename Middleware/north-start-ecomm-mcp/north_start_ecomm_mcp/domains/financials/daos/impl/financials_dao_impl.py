from north_start_ecomm_mcp.common.database import DatabaseGateway
from north_start_ecomm_mcp.common.singleton import Singleton
from north_start_ecomm_mcp.domains.financials.daos.interfaces import FinancialsDao
from north_start_ecomm_mcp.domains.financials.dtos.domainCtx import FinancialsCtx
from north_start_ecomm_mcp.domains.financials.dtos.domainResp import RevenueRecord

_BY_QUARTER = """
SELECT quarter, amount_usd
FROM revenue
WHERE quarter = ?
"""


class FinancialsDaoImpl(FinancialsDao, metaclass=Singleton):
    def find_by_quarter(self, ctx: FinancialsCtx) -> FinancialsCtx:
        rows = DatabaseGateway().read(_BY_QUARTER, (ctx.req.quarter,))
        ctx.resp.records = [
            RevenueRecord(quarter=row["quarter"], amount_usd=row["amount_usd"])
            for row in rows
        ]
        return ctx
