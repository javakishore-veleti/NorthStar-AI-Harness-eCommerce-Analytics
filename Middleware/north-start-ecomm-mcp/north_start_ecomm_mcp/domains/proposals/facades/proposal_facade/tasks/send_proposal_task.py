from north_start_ecomm_mcp.domains.proposals.daos.objects_factory import (
    ProposalDaoFactory,
)
from north_start_ecomm_mcp.domains.proposals.dtos.domainCtx import ProposalCtx


class SendProposalTask:
    def execute(self, ctx: ProposalCtx) -> ProposalCtx:
        return ProposalDaoFactory.get_proposal_dao().insert_outbox(ctx)
