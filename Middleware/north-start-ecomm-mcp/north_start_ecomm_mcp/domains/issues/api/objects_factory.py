from north_start_ecomm_mcp.domains.issues.api.impl.issue_lookup_api_impl import IssueLookupApiImpl
from north_start_ecomm_mcp.domains.issues.api.interfaces import IssueLookupApi


class IssueLookupApiFactory:
    @staticmethod
    def get_issue_lookup_api() -> IssueLookupApi:
        return IssueLookupApiImpl()
