from pydantic import BaseModel

class RoleBase(BaseModel):
    name: str
    permissions: dict | None = None  # Cambiado a dict para mayor flexibilidad

class RoleCreate(RoleBase):
    pass

class RoleOut(RoleBase):
    role_id: int

    class Config:
        from_attributes = True  # Reemplaza a orm_mode en Pydantic v2