from abc import ABC, abstractmethod

from north_start_ecomm_mcp.domains.issues.dtos.domainCtx import IssueCtx


class IssueDao(ABC):
    @abstractmethod
    def find_by_customer(self, ctx: IssueCtx) -> IssueCtx:
        """Read issues by ctx.req.customer. The role is not a filter."""
