from north_start_ecomm_mcp.domains.proposals.daos.impl.proposal_dao_impl import (
    ProposalDaoImpl,
)
from north_start_ecomm_mcp.domains.proposals.daos.interfaces import ProposalDao


class ProposalDaoFactory:
    @staticmethod
    def get_proposal_dao() -> ProposalDao:
        return ProposalDaoImpl()
