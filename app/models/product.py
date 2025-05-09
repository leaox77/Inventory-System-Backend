from sqlalchemy import Column, String, Numeric, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .base import Base

class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, autoincrement=True)  # Agregado
    barcode = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    category_id = Column(Integer, ForeignKey("categories.category_id"))
    unit_type = Column(String(10), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    cost = Column(Numeric(10, 2))
    min_stock = Column(Integer, default=5)
    is_active = Column(Boolean, default=True)

    category = relationship("Category", back_populates="products")
    inventory_items = relationship("Inventory", back_populates="product")
    sale_details = relationship("SaleDetail", back_populates="product")