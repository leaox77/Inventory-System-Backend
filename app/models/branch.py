from sqlalchemy import Column, String, Integer, Text
from sqlalchemy.orm import relationship
from .base import Base

class Branch(Base):
    __tablename__ = "branches"

    branch_id = Column(Integer, primary_key=True, autoincrement=True)  # Agregado
    name = Column(String(100), nullable=False, unique=True)
    address = Column(Text, nullable=False)
    phone = Column(String(20))
    opening_hours = Column(Text)

    inventory_items = relationship("Inventory", back_populates="branch")
    sales = relationship("Sale", back_populates="branch")