# routers/role.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.models.role import Role
from app.schemas.role import RoleOut
from app.dependencies import get_db

router = APIRouter(prefix="/roles", tags=["roles"])

@router.get("/", response_model=List[RoleOut])
def read_roles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtiene lista de roles"""
    return db.query(Role).offset(skip).limit(limit).all()