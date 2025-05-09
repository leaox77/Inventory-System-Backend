from pydantic import BaseModel
from datetime import date

class InventoryBase(BaseModel):
    product_id: int
    branch_id: int
    quantity: float
    expiry_date: date | None = None

class InventoryUpdate(InventoryBase):
    pass

class InventoryOut(InventoryBase):
    class Config:
        orm_mode = True