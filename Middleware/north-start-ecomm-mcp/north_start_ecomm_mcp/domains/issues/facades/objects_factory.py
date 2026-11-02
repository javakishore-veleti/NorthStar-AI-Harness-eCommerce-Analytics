from north_start_ecomm_mcp.domains.issues.facades.interfaces.issue_facade import (
    IssueFacade,
)
from north_start_ecomm_mcp.domains.issues.facades.issue_facade.issue_facade_impl import (
    IssueFacadeImpl,
)


class IssueFacadeFactory:
    @staticmethod
    def get_issue_facade() -> IssueFacade:
        return IssueFacadeImpl()
