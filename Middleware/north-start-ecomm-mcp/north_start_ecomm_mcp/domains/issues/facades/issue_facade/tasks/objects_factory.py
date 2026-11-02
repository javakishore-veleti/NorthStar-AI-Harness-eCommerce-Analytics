from north_start_ecomm_mcp.domains.issues.facades.issue_facade.tasks.impl.lookup_issue_task_impl import (
    LookupIssueTaskImpl,
)
from north_start_ecomm_mcp.domains.issues.facades.issue_facade.tasks.interfaces import LookupIssueTask


class LookupIssueTaskFactory:
    @staticmethod
    def get_lookup_issue_task() -> LookupIssueTask:
        return LookupIssueTaskImpl()
