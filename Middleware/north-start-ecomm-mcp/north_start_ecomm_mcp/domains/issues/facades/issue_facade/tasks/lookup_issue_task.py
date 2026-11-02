from north_start_ecomm_mcp.domains.issues.daos.objects_factory import IssueDaoFactory
from north_start_ecomm_mcp.domains.issues.dtos.domainCtx import IssueCtx


class LookupIssueTask:
    def execute(self, ctx: IssueCtx) -> IssueCtx:
        return IssueDaoFactory.get_issue_dao().find_by_customer(ctx)
