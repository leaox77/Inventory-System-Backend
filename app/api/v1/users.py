from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserOut, UserCreate, UserUpdate
from app.crud.user import get_user, create_user, get_user_by_email
from app.utils.security import get_current_active_user, admin_required

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=List[UserOut])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    return db.query(User).offset(skip).limit(limit).all()

@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_new_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    
    return create_user(db=db, user=user)

@router.get("/me", response_model=UserOut)
def read_user_me(current_user: User = Depends(get_current_active_user)):
    return current_user