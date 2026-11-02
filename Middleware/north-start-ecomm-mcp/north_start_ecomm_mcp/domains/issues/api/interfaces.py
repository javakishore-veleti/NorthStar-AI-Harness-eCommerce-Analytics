from abc import ABC, abstractmethod
from typing import Annotated

from fastapi import Header
from fastapi.responses import JSONResponse

from north_start_ecomm_mcp.domains.issues.dtos.domainCtx import IssueCtx


class IssueLookupApi(ABC):
    @abstractmethod
    def issue_lookup(
        self,
        ctx: IssueCtx,
        x_employee_role: Annotated[str | None, Header(alias="X-Employee-Role")] = None,
    ) -> JSONResponse:
        """Read the role header, then call the facade with the context."""
