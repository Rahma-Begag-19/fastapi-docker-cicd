from typing import Optional

from pydantic import BaseModel


class DealCreate(BaseModel):
    title: str
    value: Optional[float] = None
    status: str = "open"
    contact_id: int


class DealResponse(BaseModel):
    id: int
    title: str
    value: Optional[float]
    status: str
    contact_id: int
    owner_id: int

    class Config:
        from_attributes = True