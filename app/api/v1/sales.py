from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.sale import Sale
from app.schemas.sale import SaleCreate, SaleOut
from app.crud.sale import create_sale, get_sales
from app.utils.security import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/sales", tags=["sales"])

@router.post("/", response_model=SaleOut, status_code=status.HTTP_201_CREATED)
def create_new_sale(
    sale: SaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return create_sale(db=db, sale=sale, user_id=current_user.user_id)

@router.get("/", response_model=List[SaleOut])
def read_sales(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return get_sales(db, skip=skip, limit=limit)