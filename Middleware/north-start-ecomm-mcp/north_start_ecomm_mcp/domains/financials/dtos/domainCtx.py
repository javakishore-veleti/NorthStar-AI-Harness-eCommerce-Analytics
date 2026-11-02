from pydantic import BaseModel, Field

from north_start_ecomm_mcp.domains.financials.dtos.domainReq import FinancialsReq
from north_start_ecomm_mcp.domains.financials.dtos.domainResp import FinancialsResp


class FinancialsCtx(BaseModel):
    req: FinancialsReq = Field(default_factory=FinancialsReq)
    resp: FinancialsResp = Field(default_factory=FinancialsResp)
