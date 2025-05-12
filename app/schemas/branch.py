from pydantic import BaseModel, ConfigDict
from typing import Optional


class BranchBase(BaseModel):
    name: str
    address: str
    phone: Optional[str] = None
    opening_hours: Optional[str] = None


class BranchCreate(BranchBase):
    pass


class BranchOut(BranchBase):
    branch_id: int
    name: str
   
    class Config:
        from_attributes = True


class BranchUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    opening_hours: Optional[str] = None
