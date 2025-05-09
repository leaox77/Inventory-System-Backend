from sqlalchemy import Column, String, Numeric, Text, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .base import Base

class Client(Base):
    __tablename__ = "clients"

    client_id = Column(Integer, primary_key=True, autoincrement=True)  # Agregado
    ci_nit = Column(String(20), nullable=False, unique=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100))
    phone = Column(String(20))
    address = Column(Text)

    sales = relationship("Sale", back_populates="client")