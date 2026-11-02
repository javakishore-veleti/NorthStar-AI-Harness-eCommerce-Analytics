from typing import Annotated

from fastapi import APIRouter, Header
from fastapi.responses import JSONResponse

from north_start_ecomm_mcp.app.http_role import role_from_header
from north_start_ecomm_mcp.domains.customer.dtos.domainCtx import CustomerCtx
from north_start_ecomm_mcp.domains.customer.facades.objects_factory import (
    CustomerFacadeFactory,
)

router = APIRouter()


@router.post("/api/customer/brief")
def customer_brief(
    ctx: CustomerCtx,
    x_employee_role: Annotated[str | None, Header(alias="X-Employee-Role")] = None,
) -> JSONResponse:
    ctx.req.role = role_from_header(x_employee_role)
    result = CustomerFacadeFactory.get_customer_facade().lookup(ctx)
    status_code = 403 if result.resp.denied else 200
    return JSONResponse(status_code=status_code, content=result.model_dump())
