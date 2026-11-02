from north_start_ecomm_mcp.domains.customer.facades.customer_facade.customer_facade_impl import (
    CustomerFacadeImpl,
)
from north_start_ecomm_mcp.domains.customer.facades.interfaces.customer_facade import (
    CustomerFacade,
)


class CustomerFacadeFactory:
    @staticmethod
    def get_customer_facade() -> CustomerFacade:
        return CustomerFacadeImpl()
