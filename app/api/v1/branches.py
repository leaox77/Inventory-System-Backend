from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.schemas.branch import BranchCreate, BranchOut, BranchUpdate
from app.crud import branch as crud_branch
from app.dependencies import get_db
from app.models.user import User
from app.dependencies import get_current_active_user

router = APIRouter(prefix="/branches", tags=["branches"])

@router.post("/", response_model=BranchOut, status_code=status.HTTP_201_CREATED)
def create_branch(
    branch: BranchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return crud_branch.create_branch(db=db, branch=branch)

@router.get("/", response_model=List[BranchOut])
def read_branches(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return crud_branch.get_branches(db, skip=skip, limit=limit)

@router.get("/{branch_id}", response_model=BranchOut)
def read_branch(
    branch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_branch = crud_branch.get_branch(db, branch_id=branch_id)
    if db_branch is None:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")
    return db_branch

@router.put("/{branch_id}", response_model=BranchOut)
def update_branch(
    branch_id: int,
    branch: BranchUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_branch = crud_branch.get_branch(db, branch_id=branch_id)
    if db_branch is None:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")
    return crud_branch.update_branch(db=db, branch_id=branch_id, branch=branch)

@router.delete("/{branch_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_branch(
    branch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_branch = crud_branch.get_branch(db, branch_id=branch_id)
    if db_branch is None:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")
    crud_branch.delete_branch(db=db, branch_id=branch_id)
    return {"ok": True}