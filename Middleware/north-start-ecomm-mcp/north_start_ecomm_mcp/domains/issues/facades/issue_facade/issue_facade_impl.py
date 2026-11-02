from north_start_ecomm_mcp.common.access import denial_message
from north_start_ecomm_mcp.common.singleton import Singleton
from north_start_ecomm_mcp.domains.issues.dtos.domainCtx import IssueCtx
from north_start_ecomm_mcp.domains.issues.dtos.domainResp import IssueResp
from north_start_ecomm_mcp.domains.issues.facades.interfaces.issue_facade import (
    IssueFacade,
)
from north_start_ecomm_mcp.domains.issues.facades.issue_facade.tasks.objects_factory import (
    LookupIssueTaskFactory,
)

_OPERATION = "issue_lookup"


class IssueFacadeImpl(IssueFacade, metaclass=Singleton):
    def lookup(self, ctx: IssueCtx) -> IssueCtx:
        ctx.resp = IssueResp()
        message = denial_message(ctx.req.role, _OPERATION)
        if message is not None:
            ctx.resp.denied = True
            ctx.resp.message = message
            return ctx
        return LookupIssueTaskFactory.get_lookup_issue_task().execute(ctx)
