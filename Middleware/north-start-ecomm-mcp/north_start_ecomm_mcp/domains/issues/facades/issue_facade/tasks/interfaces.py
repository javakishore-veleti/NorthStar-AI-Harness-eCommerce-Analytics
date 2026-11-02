from abc import ABC, abstractmethod

from north_start_ecomm_mcp.domains.issues.dtos.domainCtx import IssueCtx


class LookupIssueTask(ABC):
    @abstractmethod
    def execute(self, ctx: IssueCtx) -> IssueCtx:
        """Run the task. The only argument is the domain context."""
