from abc import ABC, abstractmethod

from north_start_ecomm_mcp.domains.issues.dtos.domainCtx import IssueCtx


class IssueFacade(ABC):
    @abstractmethod
    def lookup(self, ctx: IssueCtx) -> IssueCtx:
        """Look up an issue. The only argument is the domain context."""
