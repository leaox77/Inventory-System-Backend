from pydantic import BaseModel
from datetime import datetime
from .product import ProductOut
from .client import ClientOut
from .payment_method import PaymentMethodOut  # Import PaymentMethodOut from the appropriate module
from typing import List, Optional
from decimal import Decimal
from .branch import BranchOut  # Import BranchOut from the appropriate module

class SaleDetailBase(BaseModel):
    product_id: int
    quantity: Decimal
    unit_price: Decimal
    discount: Optional[Decimal] = Decimal('0.0') # Descuento por producto, opcional

class SaleDetailCreate(SaleDetailBase):
    pass

class SaleDetailOut(SaleDetailBase):
    product: ProductOut
    total_line: float  # Cálculo del total por línea, teniendo en cuenta el descuento

    class Config:
        from_attributes = True

class SaleBase(BaseModel):
    client_id: Optional[int] = None  # Permite que sea opcional
    branch_id: int
    payment_method_id: int

class SaleCreate(SaleBase):
    items: List[SaleDetailCreate]  # Lista de detalles de venta, cada uno de tipo SaleDetailCreate
    discount: Optional[float] = 0.0  # El descuento total, también opcional

class SaleOut(SaleBase):
    sale_id: int
    user_id: int
    invoice_number: str
    sale_date: datetime
    subtotal: float
    discount: float  # El descuento total aplicado a la venta
    total: float
    status: str
    payment_method: PaymentMethodOut
    details: List[SaleDetailOut]  # Lista con los detalles de la venta, cada uno de tipo SaleDetailOut
    client: ClientOut
    branch: BranchOut
    class Config:
        from_attributes = True
