from pydantic import BaseModel
from typing import Optional


class ProductBase(BaseModel):
    barcode: str
    name: str
    description: Optional[str] = None
    category_id: int
    unit_type: str
    price: float
    cost: Optional[float] = None
    min_stock: int = 5  # se establece un valor por defecto si no se proporciona


class ProductCreate(ProductBase):
    pass  # Hereda todo lo necesario para crear un producto


class ProductOut(ProductBase):
    product_id: int
    is_active: bool

    class Config:
        orm_mode = True  # Necesario para trabajar con objetos ORM (SQLAlchemy)


class ProductUpdate(BaseModel):

    barcode: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    unit_type: Optional[str] = None
    price: Optional[float] = None
    cost: Optional[float] = None
    min_stock: Optional[int] = None
    is_active: Optional[bool] = None
