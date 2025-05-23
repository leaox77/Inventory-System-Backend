# schemas/unit_type.py
from pydantic import BaseModel, ConfigDict

class UnitTypeBase(BaseModel):
    name: str

class UnitTypeCreate(UnitTypeBase):
    pass

class UnitTypeOut(UnitTypeBase):
    id: int
    name: str

    class Config:
        from_attributes = True
