from pydantic import BaseModel


class FinancialsReq(BaseModel):
    quarter: str = ""
    role: str = ""
