# schemas/purchase_order.py
from enum import Enum
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List
from pydantic import field_validator

class OrderStatus(str, Enum):
    PENDING = 'PENDING'
    APPROVED = 'APPROVED'
    DELIVERED = 'DELIVERED'
    CANCELLED = 'CANCELLED'
    PARTIALLY_DELIVERED = 'PARTIALLY_DELIVERED'

# schemas/purchase_order.py
class PurchaseOrderItemBase(BaseModel):
    product_id: int
    quantity: float
    unit_cost: float
    
    @field_validator('quantity', 'unit_cost')
    def must_be_positive(cls, value):
        if value <= 0:
            raise ValueError('Debe ser mayor que cero')
        return value

class PurchaseOrderCreate(BaseModel):
    supplier_id: int
    branch_id: int
    expected_delivery_date: Optional[datetime] = None
    notes: Optional[str] = None
    status: str = "APPROVED"
    items: List[PurchaseOrderItemBase]
    
    @field_validator('status')
    def validate_status(cls, v):
        if v.upper() not in ['PENDING', 'APPROVED', 'DELIVERED', 'CANCELLED']:
            raise ValueError('Estado inválido')
        return v.upper()
    
class PurchaseOrderItemOut(PurchaseOrderItemBase):
    item_id: int
    order_id: int
    
    class Config:
        from_attributes = True

class PurchaseOrderOut(BaseModel):
    order_id: int
    supplier_id: int
    branch_id: int
    order_date: datetime
    expected_delivery_date: Optional[datetime]
    status: str
    total_amount: float
    notes: Optional[str]
    created_by: int
    
    model_config = ConfigDict(from_attributes=True)

class OrderStatusUpdate(BaseModel):
    status: OrderStatus
    notes: Optional[str] = None