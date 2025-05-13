# api/routes/supplier.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from app.schemas.supplier import SupplierCreate, SupplierOut, SupplierProductOut
from app.schemas.purchase_order import PurchaseOrderCreate, PurchaseOrderOut
from app.crud.supplier import create_supplier, get_suppliers, get_supplier, update_supplier as update_supplier_db, delete_supplier as delete_supplier_db, approve_purchase_order
from app.crud.purchase_order import create_purchase_order
from app.dependencies import get_db
from app.utils.security import get_current_active_user

router = APIRouter(prefix="/suppliers", tags=["suppliers"])

@router.post("/", response_model=SupplierOut)
def create_supplier_route(supplier: SupplierCreate, db: Session = Depends(get_db)):
    print(f"Tipo de supplier recibido: {type(supplier)}") # Para debugging
    return create_supplier(db=db, supplier_data=supplier)

@router.get("/", response_model=list[SupplierOut])
def read_suppliers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_suppliers(db, skip=skip, limit=limit)

@router.get("/{supplier_id}", response_model=SupplierOut)
def read_supplier(supplier_id: int, db: Session = Depends(get_db)):
    db_supplier = get_supplier(db, supplier_id)
    if not db_supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return db_supplier

from app.crud.supplier import get_supplier, update_supplier as update_supplier_db # Importa la función del CRUD con un alias

@router.put("/{supplier_id}", response_model=SupplierOut)
def update_supplier(supplier_id: int, supplier: SupplierCreate, db: Session = Depends(get_db)):
    db_supplier = update_supplier_db(db, supplier_id, supplier) # Llama a la función del CRUD
    if not db_supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return db_supplier

@router.delete("/{supplier_id}")
def delete_supplier(supplier_id: int, db: Session = Depends(get_db)):
    if not delete_supplier_db(db, supplier_id): # Llama a la función del CRUD
        raise HTTPException(status_code=404, detail="Supplier not found")
    return {"message": "Supplier deleted"}

@router.post("/orders/", response_model=PurchaseOrderOut)
def create_order(
    order: PurchaseOrderCreate, 
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_active_user)
):
    try:
        return create_purchase_order(db, order, user.user_id)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(500, detail=f"Error interno: {str(e)}")

@router.post("/orders/{order_id}/approve")
def approve_order(order_id: int, db: Session = Depends(get_db)):
    db_order = approve_purchase_order(db, order_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"message": "Order approved and inventory updated"}