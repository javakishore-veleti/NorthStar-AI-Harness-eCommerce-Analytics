from north_start_ecomm_mcp.domains.financials.api.impl.revenue_summary_api_impl import RevenueSummaryApiImpl
from north_start_ecomm_mcp.domains.financials.api.interfaces import RevenueSummaryApi


class RevenueSummaryApiFactory:
    @staticmethod
    def get_revenue_summary_api() -> RevenueSummaryApi:
        return RevenueSummaryApiImpl()
