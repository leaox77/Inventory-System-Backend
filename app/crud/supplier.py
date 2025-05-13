# crud/supplier.py
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from sqlalchemy import func
from datetime import datetime, timedelta
from app.models.supplier import Supplier, SupplierProduct, PurchaseOrder, PurchaseOrderItem
from app.schemas.supplier import SupplierCreate
from app.models.inventory import Inventory
from app.models.product import Product  # Import the Product model

def create_supplier(db: Session, supplier_data: SupplierCreate):
    try:
        db_supplier = Supplier(**supplier_data.model_dump())
        db.add(db_supplier)
        db.commit()
        db.refresh(db_supplier)
        return db_supplier
    except Exception as e:
        print(f"Error en create_supplier (CRUD): {e}")
        raise

def get_suppliers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Supplier).offset(skip).limit(limit).all()

def get_supplier(db: Session, supplier_id: int):
    return db.query(Supplier).filter(Supplier.supplier_id == supplier_id).first()

def update_supplier(db: Session, supplier_id: int, supplier_data):
    db_supplier = get_supplier(db, supplier_id)
    if not db_supplier:
        return None
    for key, value in supplier_data.dict().items():
        setattr(db_supplier, key, value)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier

def delete_supplier(db: Session, supplier_id: int):
    db_supplier = get_supplier(db, supplier_id)
    if not db_supplier:
        return False
    db.delete(db_supplier)
    db.commit()
    return True

def approve_purchase_order(db: Session, order_id: int):
    db_order = db.query(PurchaseOrder).filter(PurchaseOrder.order_id == order_id).first()
    if not db_order:
        return None
    
    # Actualizar inventario
    for item in db_order.items:
        inventory = db.query(Inventory).filter(
            Inventory.product_id == item.product_id,
            Inventory.branch_id == db_order.branch_id
        ).first()
        
        if inventory:
            inventory.quantity += item.quantity
        else:
            inventory = Inventory(
                product_id=item.product_id,
                branch_id=db_order.branch_id,
                quantity=item.quantity
            )
            db.add(inventory)
    
    db_order.status = "APPROVED"
    db.commit()
    return db_order