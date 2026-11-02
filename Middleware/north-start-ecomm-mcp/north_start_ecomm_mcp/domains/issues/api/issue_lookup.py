from typing import Annotated

from fastapi import APIRouter, Header
from fastapi.responses import JSONResponse

from north_start_ecomm_mcp.app.http_role import role_from_header
from north_start_ecomm_mcp.domains.issues.dtos.domainCtx import IssueCtx
from north_start_ecomm_mcp.domains.issues.facades.objects_factory import (
    IssueFacadeFactory,
)

router = APIRouter()


@router.post("/api/issues/lookup")
def issue_lookup(
    ctx: IssueCtx,
    x_employee_role: Annotated[str | None, Header(alias="X-Employee-Role")] = None,
) -> JSONResponse:
    ctx.req.role = role_from_header(x_employee_role)
    result = IssueFacadeFactory.get_issue_facade().lookup(ctx)
    status_code = 403 if result.resp.denied else 200
    return JSONResponse(status_code=status_code, content=result.model_dump())
