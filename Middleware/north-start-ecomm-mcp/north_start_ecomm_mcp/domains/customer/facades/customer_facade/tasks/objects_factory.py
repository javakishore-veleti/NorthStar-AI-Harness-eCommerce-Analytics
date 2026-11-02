from north_start_ecomm_mcp.domains.customer.facades.customer_facade.tasks.impl.lookup_customer_task_impl import (
    LookupCustomerTaskImpl,
)
from north_start_ecomm_mcp.domains.customer.facades.customer_facade.tasks.interfaces import LookupCustomerTask


class LookupCustomerTaskFactory:
    @staticmethod
    def get_lookup_customer_task() -> LookupCustomerTask:
        return LookupCustomerTaskImpl()
