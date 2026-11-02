from pydantic import BaseModel, Field


class IssueRecord(BaseModel):
    id: str
    customer: str
    symptom: str
    owner: str


class IssueResp(BaseModel):
    records: list[IssueRecord] = Field(default_factory=list)
    denied: bool = False
    message: str = ""
