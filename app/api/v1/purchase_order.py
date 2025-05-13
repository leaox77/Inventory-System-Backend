# api/routes/purchase_order.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.purchase_order import OrderStatusUpdate, PurchaseOrderOut, PurchaseOrderCreate
from app.crud.purchase_order import update_order_status, create_purchase_order
from app.dependencies import get_db
from app.utils.security import get_current_active_user

router = APIRouter(prefix="/orders", tags=["orders"])

@router.patch("/{order_id}/status", response_model=PurchaseOrderOut)
def change_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    try:
        updated_order = update_order_status(db, order_id, status_update)
        if not updated_order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        return updated_order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/", response_model=PurchaseOrderOut, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: PurchaseOrderCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    try:
        new_order = create_purchase_order(db, order_data) # Usamos la nueva función create_purchase_order
        return new_order
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )