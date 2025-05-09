from sqlalchemy import Column, Numeric, Integer, ForeignKey, Date
from sqlalchemy.orm import relationship
from .base import Base
from datetime import date

class Inventory(Base):
    __tablename__ = "inventory"

    product_id = Column(Integer, ForeignKey("products.product_id"), primary_key=True)
    branch_id = Column(Integer, ForeignKey("branches.branch_id"), primary_key=True)
    quantity = Column(Numeric(10, 3), nullable=False, default=0)
    expiry_date = Column(Date)
    last_updated = Column(Date, default=date.today)

    product = relationship("Product", back_populates="inventory_items")
    branch = relationship("Branch", back_populates="inventory_items")