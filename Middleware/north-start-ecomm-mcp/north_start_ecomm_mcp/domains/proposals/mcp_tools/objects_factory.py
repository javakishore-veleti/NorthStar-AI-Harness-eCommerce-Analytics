from north_start_ecomm_mcp.domains.proposals.mcp_tools.impl.send_proposal_tool_impl import SendProposalToolImpl
from north_start_ecomm_mcp.domains.proposals.mcp_tools.interfaces import SendProposalTool


class SendProposalToolFactory:
    @staticmethod
    def get_send_proposal_tool() -> SendProposalTool:
        return SendProposalToolImpl()
