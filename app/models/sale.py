from sqlalchemy import Column, Numeric, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime

class Sale(Base):
    __tablename__ = "sales"

    sale_id = Column(Integer, primary_key=True, autoincrement=True)  # Agregado
    invoice_number = Column(String(20), unique=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.client_id"))
    user_id = Column(Integer, ForeignKey("users.user_id"))
    branch_id = Column(Integer, ForeignKey("branches.branch_id"))
    sale_date = Column(DateTime, default=datetime.utcnow)
    subtotal = Column(Numeric(12, 2), nullable=False)
    discount = Column(Numeric(12, 2), default=0)
    total = Column(Numeric(12, 2), nullable=False)
    payment_method = Column(String(20), nullable=False)
    status = Column(String(20), default="COMPLETADA")

    client = relationship("Client", back_populates="sales", lazy="joined")
    user = relationship("User", back_populates="sales")
    branch = relationship("Branch", back_populates="sales", lazy="joined")
    details = relationship("SaleDetail", back_populates="sale")

class SaleDetail(Base):
    __tablename__ = "sale_details"

    detail_id = Column(Integer, primary_key=True, autoincrement=True)  # Agregado
    sale_id = Column(Integer, ForeignKey("sales.sale_id"))
    product_id = Column(Integer, ForeignKey("products.product_id"))
    quantity = Column(Numeric(10, 3), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    discount = Column(Numeric(10, 2), default=0)
    total_line = Column(Numeric(12, 2), nullable=False)

    sale = relationship("Sale", back_populates="details")
    product = relationship("Product", back_populates="sale_details")