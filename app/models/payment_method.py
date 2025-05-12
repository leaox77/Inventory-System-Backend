# models/payment_method.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime

class PaymentMethod(Base):
    __tablename__ = "payment_methods"

    payment_method_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), nullable=False, unique=True)
    description = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relación inversa (opcional)
    sales = relationship("Sale", back_populates="payment_method")