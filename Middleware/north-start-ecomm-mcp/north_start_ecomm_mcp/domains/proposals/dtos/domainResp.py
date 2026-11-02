from pydantic import BaseModel


class ProposalResp(BaseModel):
    status: str = ""
    receipt: str = ""
    customer: str = ""
    denied: bool = False
    message: str = ""
