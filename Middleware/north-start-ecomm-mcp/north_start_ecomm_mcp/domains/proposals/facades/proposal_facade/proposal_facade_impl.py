from north_start_ecomm_mcp.common.access import denial_message
from north_start_ecomm_mcp.common.singleton import Singleton
from north_start_ecomm_mcp.domains.customer.dtos.domainCtx import CustomerCtx
from north_start_ecomm_mcp.domains.customer.dtos.domainReq import CustomerReq
from north_start_ecomm_mcp.domains.customer.facades.objects_factory import (
    CustomerFacadeFactory,
)
from north_start_ecomm_mcp.domains.proposals.dtos.domainCtx import ProposalCtx
from north_start_ecomm_mcp.domains.proposals.dtos.domainResp import ProposalResp
from north_start_ecomm_mcp.domains.proposals.facades.interfaces.proposal_facade import (
    ProposalFacade,
)
from north_start_ecomm_mcp.domains.proposals.facades.proposal_facade.tasks.send_proposal_task import (
    SendProposalTask,
)

_OPERATION = "send_proposal"
_UNKNOWN = "Unknown customer. Look up the customer before sending."


class ProposalFacadeImpl(ProposalFacade, metaclass=Singleton):
    def send(self, ctx: ProposalCtx) -> ProposalCtx:
        ctx.resp = ProposalResp()
        message = denial_message(ctx.req.role, _OPERATION)
        if message is not None:
            ctx.resp.denied = True
            ctx.resp.message = message
            return ctx
        looked = CustomerFacadeFactory.get_customer_facade().lookup(
            CustomerCtx(req=CustomerReq(customer=ctx.req.customer, role=ctx.req.role))
        )
        if looked.resp.denied or not looked.resp.records:
            ctx.resp.message = _UNKNOWN
            return ctx
        ctx.req.customer = looked.resp.records[0].name
        return SendProposalTask().execute(ctx)
