from sqlalchemy import Column, String, Numeric, Integer, ForeignKey, Boolean, func
from sqlalchemy.orm import relationship, Session
from typing import Optional
from .base import Base
from .inventory import Inventory  # Import the Inventory model
from .unit_type import UnitType  # importa el nuevo modelo

class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, autoincrement=True)  # Agregado
    barcode = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    category_id = Column(Integer, ForeignKey("categories.category_id"))
    unit_type = Column(Integer, ForeignKey("unit_types.id"))  # Cambiado a integer y FK
    price = Column(Numeric(10, 2), nullable=False)
    cost = Column(Numeric(10, 2))
    min_stock = Column(Integer, default=5)
    is_active = Column(Boolean, default=True)
    

    category = relationship("Category", back_populates="products")
    inventory_items = relationship("Inventory", back_populates="product")
    sale_details = relationship("SaleDetail", back_populates="product")
    unit_type_rel = relationship("UnitType", back_populates="products")  # nuevo

    def get_stock(self, db: Session, branch_id: Optional[int] = None):
        if branch_id:
            # Si se proporciona una sucursal, filtra por sucursal
            stock = db.query(func.sum(Inventory.quantity)).filter(
                Inventory.product_id == self.product_id,
                Inventory.branch_id == branch_id
            ).scalar()
        else:
            # Si no se proporciona una sucursal, calcula el stock total
            stock = db.query(func.sum(Inventory.quantity)).filter(
                Inventory.product_id == self.product_id
            ).scalar()

        return stock or 0  # Retorna 0 si no hay stock