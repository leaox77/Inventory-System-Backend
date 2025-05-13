from sqlalchemy import Column, Numeric, Integer, ForeignKey, DateTime, func, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import Base

class Inventory(Base):
    __tablename__ = "inventory"

    inventory_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.branch_id"), nullable=False)
    quantity = Column(Numeric(10, 3), nullable=False, default=0)
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())

    product = relationship("Product", back_populates="inventory_items")
    branch = relationship("Branch", back_populates="inventory_items")

    __table_args__ = (
        UniqueConstraint('product_id', 'branch_id', name='_inventory_product_branch_uc'),
    )
