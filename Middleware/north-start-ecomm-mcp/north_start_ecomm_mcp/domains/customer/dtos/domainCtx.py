from pydantic import BaseModel, Field

from north_start_ecomm_mcp.domains.customer.dtos.domainReq import CustomerReq
from north_start_ecomm_mcp.domains.customer.dtos.domainResp import CustomerResp


class CustomerCtx(BaseModel):
    req: CustomerReq = Field(default_factory=CustomerReq)
    resp: CustomerResp = Field(default_factory=CustomerResp)
