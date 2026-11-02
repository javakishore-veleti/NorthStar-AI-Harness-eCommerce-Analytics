from abc import ABC, abstractmethod
from typing import Annotated

from fastapi import Header
from fastapi.responses import JSONResponse

from north_start_ecomm_mcp.domains.customer.dtos.domainCtx import CustomerCtx


class CustomerBriefApi(ABC):
    @abstractmethod
    def customer_brief(
        self,
        ctx: CustomerCtx,
        x_employee_role: Annotated[str | None, Header(alias="X-Employee-Role")] = None,
    ) -> JSONResponse:
        """Read the role header, then call the facade with the context."""
