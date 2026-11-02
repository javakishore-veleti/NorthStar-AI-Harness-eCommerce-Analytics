from pydantic import BaseModel, Field


class RevenueRecord(BaseModel):
    quarter: str
    amount_usd: int


class FinancialsResp(BaseModel):
    records: list[RevenueRecord] = Field(default_factory=list)
    denied: bool = False
    message: str = ""
