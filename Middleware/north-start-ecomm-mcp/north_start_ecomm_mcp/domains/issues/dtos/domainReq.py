from pydantic import BaseModel, Field


class IssueReq(BaseModel):
    customer: str = ""
    role: str = ""
