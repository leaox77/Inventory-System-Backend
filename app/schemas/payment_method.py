# schemas/payment_method.py
from pydantic import BaseModel
from typing import Optional

class PaymentMethodBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: Optional[bool] = True

class PaymentMethodCreate(PaymentMethodBase):
    pass

class PaymentMethodOut(PaymentMethodBase):
    payment_method_id: int
    
    class Config:
        from_attributes = True