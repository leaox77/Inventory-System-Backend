# models/supplier.py
from sqlalchemy import Column, Integer, String, Boolean, Numeric, Text, ForeignKey, DateTime, Enum
from sqlalchemy.sql import func
from .base import Base
from sqlalchemy.orm import relationship

class Supplier(Base):
    __tablename__ = "suppliers"
    
    supplier_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    contact_name = Column(String(100), nullable=True)
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    
    products = relationship("SupplierProduct", back_populates="supplier")
    orders = relationship("PurchaseOrder", back_populates="supplier")

class SupplierProduct(Base):
    __tablename__ = "supplier_products"
    
    supplier_product_id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.supplier_id"))
    product_id = Column(Integer, ForeignKey("products.product_id"))
    cost_price = Column(Numeric(10, 2), nullable=False)
    lead_time_days = Column(Integer)
    is_available = Column(Boolean, default=True)
    
    supplier = relationship("Supplier", back_populates="products")
    product = relationship("Product")

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    
    order_id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.supplier_id"))
    branch_id = Column(Integer, ForeignKey("branches.branch_id"))
    order_date = Column(DateTime, server_default=func.now())
    expected_delivery_date = Column(DateTime)
    status = Column(Enum(
        'PENDING', 
        'APPROVED',
        'DELIVERED',
        'CANCELLED',
        'PARTIALLY_DELIVERED',
        name='order_status'
    ), default='PENDING')
    total_amount = Column(Numeric(12, 2))
    notes = Column(Text)
    created_by = Column(Integer, ForeignKey("users.user_id"))
    
    supplier = relationship("Supplier", back_populates="orders")
    branch = relationship("Branch")
    items = relationship("PurchaseOrderItem", back_populates="order")
    creator = relationship("User")

class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"
    
    item_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("purchase_orders.order_id"))
    product_id = Column(Integer, ForeignKey("products.product_id"))
    quantity = Column(Numeric(10, 2), nullable=False)
    unit_cost = Column(Numeric(10, 2), nullable=False)
    
    # Relaciones
    order = relationship("PurchaseOrder", back_populates="items")
    product = relationship("Product")
