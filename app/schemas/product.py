from pydantic import BaseModel, ConfigDict
from typing import Optional, Union
from .unit_type import UnitTypeOut  # importa el nuevo esquema


class ProductBase(BaseModel):
    barcode: str
    name: str
    description: Optional[str] = None
    category_id: int
    unit_type: int
    price: float
    cost: Optional[float] = None
    min_stock: int = 5  # se establece un valor por defecto si no se proporciona


class ProductCreate(ProductBase):
    pass  # Hereda todo lo necesario para crear un producto


class ProductOut(ProductBase):
    product_id: int
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)  # Reemplaza orm_mode en Pydantic v2


class ProductUpdate(BaseModel):

    barcode: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    unit_type: Optional[int] = None
    price: Optional[float] = None
    cost: Optional[float] = None
    min_stock: Optional[int] = None
    is_active: Optional[bool] = None
