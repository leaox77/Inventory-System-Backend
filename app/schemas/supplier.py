# schemas/supplier.py
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional
from .product import ProductOut

class SupplierBase(BaseModel):
    name: str
    contact_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    is_active: bool = True

class SupplierCreate(SupplierBase):
    pass

class SupplierOut(SupplierBase):
    supplier_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class SupplierProductBase(BaseModel):
    supplier_id: int
    product_id: int
    cost_price: float
    lead_time_days: Optional[int] = None
    is_available: bool = True

class SupplierProductOut(SupplierProductBase):
    supplier_product_id: int
    product: ProductOut
    
    model_config = ConfigDict(from_attributes=True)
