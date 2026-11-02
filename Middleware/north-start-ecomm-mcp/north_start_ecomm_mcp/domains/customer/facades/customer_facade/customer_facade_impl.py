from north_start_ecomm_mcp.common.access import denial_message
from north_start_ecomm_mcp.common.singleton import Singleton
from north_start_ecomm_mcp.domains.customer.dtos.domainCtx import CustomerCtx
from north_start_ecomm_mcp.domains.customer.dtos.domainResp import CustomerResp
from north_start_ecomm_mcp.domains.customer.facades.customer_facade.tasks.lookup_customer_task import (
    LookupCustomerTask,
)
from north_start_ecomm_mcp.domains.customer.facades.interfaces.customer_facade import (
    CustomerFacade,
)

_OPERATION = "customer_brief"


class CustomerFacadeImpl(CustomerFacade, metaclass=Singleton):
    def lookup(self, ctx: CustomerCtx) -> CustomerCtx:
        ctx.resp = CustomerResp()
        message = denial_message(ctx.req.role, _OPERATION)
        if message is not None:
            ctx.resp.denied = True
            ctx.resp.message = message
            return ctx
        return LookupCustomerTask().execute(ctx)
