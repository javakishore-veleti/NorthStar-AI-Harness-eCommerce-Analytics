from north_start_ecomm_mcp.common.singleton import Singleton
from north_start_ecomm_mcp.domains.proposals.daos.objects_factory import ProposalDaoFactory
from north_start_ecomm_mcp.domains.proposals.dtos.domainCtx import ProposalCtx
from north_start_ecomm_mcp.domains.proposals.facades.proposal_facade.tasks.interfaces import SendProposalTask


class SendProposalTaskImpl(SendProposalTask, metaclass=Singleton):
    def execute(self, ctx: ProposalCtx) -> ProposalCtx:
        return ProposalDaoFactory.get_proposal_dao().insert_outbox(ctx)
