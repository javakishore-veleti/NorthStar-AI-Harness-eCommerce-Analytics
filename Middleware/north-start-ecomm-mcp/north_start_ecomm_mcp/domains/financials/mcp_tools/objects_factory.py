from north_start_ecomm_mcp.domains.financials.mcp_tools.impl.revenue_summary_tool_impl import RevenueSummaryToolImpl
from north_start_ecomm_mcp.domains.financials.mcp_tools.interfaces import RevenueSummaryTool


class RevenueSummaryToolFactory:
    @staticmethod
    def get_revenue_summary_tool() -> RevenueSummaryTool:
        return RevenueSummaryToolImpl()
