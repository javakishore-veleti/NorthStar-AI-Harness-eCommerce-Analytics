from north_start_ecomm_mcp.domains.financials.daos.impl.financials_dao_impl import (
    FinancialsDaoImpl,
)
from north_start_ecomm_mcp.domains.financials.daos.interfaces import FinancialsDao


class FinancialsDaoFactory:
    @staticmethod
    def get_financials_dao() -> FinancialsDao:
        return FinancialsDaoImpl()
