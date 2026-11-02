from north_start_ecomm_mcp.common.singleton import Singleton
from north_start_ecomm_mcp.domains.issues.daos.objects_factory import IssueDaoFactory
from north_start_ecomm_mcp.domains.issues.dtos.domainCtx import IssueCtx
from north_start_ecomm_mcp.domains.issues.facades.issue_facade.tasks.interfaces import LookupIssueTask


class LookupIssueTaskImpl(LookupIssueTask, metaclass=Singleton):
    def execute(self, ctx: IssueCtx) -> IssueCtx:
        return IssueDaoFactory.get_issue_dao().find_by_customer(ctx)
