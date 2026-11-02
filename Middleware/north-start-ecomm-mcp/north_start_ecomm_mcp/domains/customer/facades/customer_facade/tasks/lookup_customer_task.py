from north_start_ecomm_mcp.domains.customer.daos.objects_factory import (
    CustomerDaoFactory,
)
from north_start_ecomm_mcp.domains.customer.dtos.domainCtx import CustomerCtx


class LookupCustomerTask:
    def execute(self, ctx: CustomerCtx) -> CustomerCtx:
        return CustomerDaoFactory.get_customer_dao().find_by_name(ctx)
