from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.unit_type import UnitType
from app.schemas.unit_type import UnitTypeCreate, UnitTypeOut
from app.utils.security import get_current_active_user, admin_required
from app.models.user import User

router = APIRouter(prefix="/unit-types", tags=["unit types"])

@router.get("/", response_model=List[UnitTypeOut])
def read_unit_types(
    name: Optional[str] = Query(None, description="Filtrar por nombre exacto o parcial"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(UnitType)
    if name:
        query = query.filter(UnitType.name.ilike(f"%{name}%"))  # filtrado parcial
    return query.offset(skip).limit(limit).all()

@router.post("/", response_model=UnitTypeOut, status_code=status.HTTP_201_CREATED)
def create_unit_type(
    unit_type: UnitTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    db_unit_type = UnitType(**unit_type.dict())
    db.add(db_unit_type)
    db.commit()
    db.refresh(db_unit_type)
    return db_unit_type
