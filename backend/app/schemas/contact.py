from typing import Optional

from pydantic import BaseModel, EmailStr


class ContactCreate(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    notes: Optional[str] = None


class ContactResponse(BaseModel):
    id: int
    name: str
    email: Optional[EmailStr]
    phone: Optional[str]
    company: Optional[str]
    notes: Optional[str]
    owner_id: int

    class Config:
        from_attributes = True