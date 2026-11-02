from north_start_ecomm_mcp.domains.customer.mcp_tools.impl.customer_brief_tool_impl import CustomerBriefToolImpl
from north_start_ecomm_mcp.domains.customer.mcp_tools.interfaces import CustomerBriefTool


class CustomerBriefToolFactory:
    @staticmethod
    def get_customer_brief_tool() -> CustomerBriefTool:
        return CustomerBriefToolImpl()
