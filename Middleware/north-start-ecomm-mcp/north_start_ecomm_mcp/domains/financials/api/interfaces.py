from abc import ABC, abstractmethod
from typing import Annotated

from fastapi import Header
from fastapi.responses import JSONResponse

from north_start_ecomm_mcp.domains.financials.dtos.domainCtx import FinancialsCtx


class RevenueSummaryApi(ABC):
    @abstractmethod
    def revenue_summary(
        self,
        ctx: FinancialsCtx,
        x_employee_role: Annotated[str | None, Header(alias="X-Employee-Role")] = None,
    ) -> JSONResponse:
        """Read the role header, then call the facade with the context."""
