from north_start_ecomm_mcp.domains.customer.api.impl.customer_brief_api_impl import CustomerBriefApiImpl
from north_start_ecomm_mcp.domains.customer.api.interfaces import CustomerBriefApi


class CustomerBriefApiFactory:
    @staticmethod
    def get_customer_brief_api() -> CustomerBriefApi:
        return CustomerBriefApiImpl()
