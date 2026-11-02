from pydantic import BaseModel, Field

from north_start_ecomm_mcp.domains.proposals.dtos.domainReq import ProposalReq
from north_start_ecomm_mcp.domains.proposals.dtos.domainResp import ProposalResp


class ProposalCtx(BaseModel):
    req: ProposalReq = Field(default_factory=ProposalReq)
    resp: ProposalResp = Field(default_factory=ProposalResp)
