from north_start_ecomm_mcp.domains.proposals.api.impl.send_proposal_api_impl import SendProposalApiImpl
from north_start_ecomm_mcp.domains.proposals.api.interfaces import SendProposalApi


class SendProposalApiFactory:
    @staticmethod
    def get_send_proposal_api() -> SendProposalApi:
        return SendProposalApiImpl()
