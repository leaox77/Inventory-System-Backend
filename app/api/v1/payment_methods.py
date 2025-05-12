from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.payment_method import PaymentMethod
from app.schemas.payment_method import PaymentMethodCreate, PaymentMethodOut


router = APIRouter(prefix="/payment-methods", tags=["payment-methods"])

@router.post("/", response_model=PaymentMethodOut, status_code=status.HTTP_201_CREATED)
def create_payment_method(
    payment_method: PaymentMethodCreate,
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo método de pago.
    """
    db_payment_method = PaymentMethod(**payment_method.dict())
    db.add(db_payment_method)
    db.commit()
    db.refresh(db_payment_method)
    return db_payment_method

@router.get("/", response_model=List[PaymentMethodOut])
def read_payment_methods(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Obtiene una lista de métodos de pago.
    """
    payment_methods = db.query(PaymentMethod).offset(skip).limit(limit).all()
    return payment_methods
