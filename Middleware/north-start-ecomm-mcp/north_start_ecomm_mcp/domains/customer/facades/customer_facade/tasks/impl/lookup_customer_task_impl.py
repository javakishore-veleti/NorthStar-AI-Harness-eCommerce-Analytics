from north_start_ecomm_mcp.common.singleton import Singleton
from north_start_ecomm_mcp.domains.customer.daos.objects_factory import CustomerDaoFactory
from north_start_ecomm_mcp.domains.customer.dtos.domainCtx import CustomerCtx
from north_start_ecomm_mcp.domains.customer.facades.customer_facade.tasks.interfaces import LookupCustomerTask


class LookupCustomerTaskImpl(LookupCustomerTask, metaclass=Singleton):
    def execute(self, ctx: CustomerCtx) -> CustomerCtx:
        return CustomerDaoFactory.get_customer_dao().find_by_name(ctx)
