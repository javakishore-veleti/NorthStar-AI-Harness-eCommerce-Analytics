from typing import Annotated

from fastapi import Header
from fastapi.responses import JSONResponse

from north_start_ecomm_mcp.app.http_role import role_from_header
from north_start_ecomm_mcp.common.singleton import Singleton
from north_start_ecomm_mcp.domains.proposals.api.interfaces import SendProposalApi
from north_start_ecomm_mcp.domains.proposals.dtos.domainCtx import ProposalCtx
from north_start_ecomm_mcp.domains.proposals.facades.objects_factory import ProposalFacadeFactory


class SendProposalApiImpl(SendProposalApi, metaclass=Singleton):
    def send_proposal(
        self,
        ctx: ProposalCtx,
        x_employee_role: Annotated[str | None, Header(alias="X-Employee-Role")] = None,
    ) -> JSONResponse:
        ctx.req.role = role_from_header(x_employee_role)
        result = ProposalFacadeFactory.get_proposal_facade().send(ctx)
        status_code = 403 if result.resp.denied else 200
        return JSONResponse(status_code=status_code, content=result.model_dump())
