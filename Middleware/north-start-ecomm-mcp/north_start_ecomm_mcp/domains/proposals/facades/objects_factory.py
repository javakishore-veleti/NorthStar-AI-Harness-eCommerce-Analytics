from north_start_ecomm_mcp.domains.proposals.facades.interfaces.proposal_facade import (
    ProposalFacade,
)
from north_start_ecomm_mcp.domains.proposals.facades.proposal_facade.proposal_facade_impl import (
    ProposalFacadeImpl,
)


class ProposalFacadeFactory:
    @staticmethod
    def get_proposal_facade() -> ProposalFacade:
        return ProposalFacadeImpl()
