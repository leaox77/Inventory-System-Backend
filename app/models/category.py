from sqlalchemy import Column, String, Numeric, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .base import Base

class Category(Base):
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, autoincrement=True)  # Agregado
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(500))
    needs_refrigeration = Column(Boolean, default=False)

    products = relationship("Product", back_populates="category")