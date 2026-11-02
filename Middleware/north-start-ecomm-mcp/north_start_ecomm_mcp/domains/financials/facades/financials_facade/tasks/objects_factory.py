from north_start_ecomm_mcp.domains.financials.facades.financials_facade.tasks.impl.revenue_summary_task_impl import (
    RevenueSummaryTaskImpl,
)
from north_start_ecomm_mcp.domains.financials.facades.financials_facade.tasks.interfaces import RevenueSummaryTask


class RevenueSummaryTaskFactory:
    @staticmethod
    def get_revenue_summary_task() -> RevenueSummaryTask:
        return RevenueSummaryTaskImpl()
