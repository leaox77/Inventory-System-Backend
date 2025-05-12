from pydantic import BaseModel, EmailStr
from typing import Optional

class ClientBase(BaseModel):
    ci_nit: str
    full_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class ClientCreate(ClientBase):
    pass

class ClientOut(ClientBase):
    client_id: int
    
    class Config:
        from_attributes = True