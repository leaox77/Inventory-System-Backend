from fastapi import Query, APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.inventory import Inventory
from app.schemas.inventory import InventoryOut, InventoryUpdate
from app.utils.security import get_current_active_user
from app.models.user import User
from app.models.branch import Branch

router = APIRouter(prefix="/inventory", tags=["inventory"])

@router.get("/branches", response_model=List[dict])
def get_branches(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    branches = db.query(Branch.branch_id, Branch.name).distinct().all()
    return [{"branch_id": branch.branch_id, "name": branch.name} for branch in branches]

@router.get("/branch/{branch_id}", response_model=List[InventoryOut])
def read_inventory_by_branch(
    branch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return db.query(Inventory).filter(Inventory.branch_id == branch_id).all()

@router.put("/{product_id}/{branch_id}", response_model=InventoryOut)
def update_inventory(
    product_id: int,
    branch_id: int,
    inventory: InventoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_inventory = db.query(Inventory).filter(
        Inventory.product_id == product_id,
        Inventory.branch_id == branch_id
    ).first()
    
    if not db_inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro de inventario no encontrado"
        )
    
    for field, value in inventory.dict(exclude_unset=True).items():
        setattr(db_inventory, field, value)
    
    db.commit()
    db.refresh(db_inventory)
    return db_inventory

from typing import Optional
from fastapi import Query

@router.get("/", response_model=List[InventoryOut])
def get_inventory(
    branch_id: Optional[int] = Query(None),
    product_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Inventory)

    if branch_id is not None:
        query = query.filter(Inventory.branch_id == branch_id)
    if product_id is not None:
        query = query.filter(Inventory.product_id == product_id)

    return query.all()
