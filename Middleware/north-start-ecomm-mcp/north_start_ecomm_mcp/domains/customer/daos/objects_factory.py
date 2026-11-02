from north_start_ecomm_mcp.domains.customer.daos.impl.customer_dao_impl import (
    CustomerDaoImpl,
)
from north_start_ecomm_mcp.domains.customer.daos.interfaces import CustomerDao


class CustomerDaoFactory:
    @staticmethod
    def get_customer_dao() -> CustomerDao:
        return CustomerDaoImpl()
