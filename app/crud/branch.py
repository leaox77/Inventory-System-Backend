from sqlalchemy.orm import Session
from ..models.branch import Branch
from ..schemas.branch import BranchCreate, BranchUpdate

def get_branches(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Branch).offset(skip).limit(limit).all()

def get_branch(db: Session, branch_id: int):
    return db.query(Branch).filter(Branch.branch_id == branch_id).first()

def create_branch(db: Session, branch: BranchCreate):
    db_branch = Branch(
        name=branch.name,
        address=branch.address,
        phone=branch.phone,
        opening_hours=branch.opening_hours
    )
    db.add(db_branch)
    db.commit()
    db.refresh(db_branch)
    return db_branch

def update_branch(db: Session, branch_id: int, branch: BranchUpdate):
    db_branch = db.query(Branch).filter(Branch.branch_id == branch_id).first()
    if not db_branch:
        return None
    
    update_data = branch.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_branch, key, value)
    
    db.commit()
    db.refresh(db_branch)
    return db_branch

def delete_branch(db: Session, branch_id: int):
    db_branch = db.query(Branch).filter(Branch.branch_id == branch_id).first()
    if db_branch:
        db.delete(db_branch)
        db.commit()
    return db_branch