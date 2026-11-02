from pydantic import BaseModel, Field


class CustomerRecord(BaseModel):
    id: str
    name: str
    need: str
    contact: str


class CustomerResp(BaseModel):
    records: list[CustomerRecord] = Field(default_factory=list)
    denied: bool = False
    message: str = ""
