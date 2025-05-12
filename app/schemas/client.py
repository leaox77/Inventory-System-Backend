# schemas/client.py
from pydantic import BaseModel

class ClientBase(BaseModel):
    ci_nit: str
    full_name: str
    email: str | None = None
    phone: str | None = None
    address: str | None = None

class ClientCreate(ClientBase):
    pass

class ClientOut(ClientBase):
    client_id: int
    
    class Config:
        from_attributes = True  # Reemplaza a orm_mode en Pydantic v2