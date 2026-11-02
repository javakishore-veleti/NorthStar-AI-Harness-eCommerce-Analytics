from north_start_ecomm_mcp.domains.financials.facades.financials_facade.financials_facade_impl import (
    FinancialsFacadeImpl,
)
from north_start_ecomm_mcp.domains.financials.facades.interfaces.financials_facade import (
    FinancialsFacade,
)


class FinancialsFacadeFactory:
    @staticmethod
    def get_financials_facade() -> FinancialsFacade:
        return FinancialsFacadeImpl()
