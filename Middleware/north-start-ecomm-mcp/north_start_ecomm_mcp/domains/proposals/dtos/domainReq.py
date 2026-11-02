from pydantic import BaseModel


class ProposalReq(BaseModel):
    customer: str = ""
    body: str = ""
    role: str = ""
