from north_start_ecomm_mcp.domains.proposals.facades.proposal_facade.tasks.impl.send_proposal_task_impl import (
    SendProposalTaskImpl,
)
from north_start_ecomm_mcp.domains.proposals.facades.proposal_facade.tasks.interfaces import SendProposalTask


class SendProposalTaskFactory:
    @staticmethod
    def get_send_proposal_task() -> SendProposalTask:
        return SendProposalTaskImpl()
