from pydantic import BaseModel, Field

from north_start_ecomm_mcp.domains.issues.dtos.domainReq import IssueReq
from north_start_ecomm_mcp.domains.issues.dtos.domainResp import IssueResp


class IssueCtx(BaseModel):
    req: IssueReq = Field(default_factory=IssueReq)
    resp: IssueResp = Field(default_factory=IssueResp)
