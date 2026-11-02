from pydantic import BaseModel, Field


class CustomerReq(BaseModel):
    customer: str = ""
    role: str = ""
