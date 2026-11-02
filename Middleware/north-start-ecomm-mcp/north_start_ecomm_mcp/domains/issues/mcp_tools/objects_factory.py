from north_start_ecomm_mcp.domains.issues.mcp_tools.impl.issue_lookup_tool_impl import IssueLookupToolImpl
from north_start_ecomm_mcp.domains.issues.mcp_tools.interfaces import IssueLookupTool


class IssueLookupToolFactory:
    @staticmethod
    def get_issue_lookup_tool() -> IssueLookupTool:
        return IssueLookupToolImpl()
