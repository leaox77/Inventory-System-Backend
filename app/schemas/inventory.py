from pydantic import BaseModel
from datetime import datetime

class InventoryBase(BaseModel):
    product_id: int
    branch_id: int
    quantity: float

class InventoryUpdate(BaseModel):
    quantity: float

class InventoryOut(InventoryBase):
    inventory_id: int
    last_updated: datetime

    class Config:
        orm_mode = True
