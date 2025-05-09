from sqlalchemy.orm import Session
from ..models.inventory import Inventory

def update_inventory_on_sale(db: Session, product_id: int, branch_id: int, quantity: float):
    inventory = db.query(Inventory).filter(
        Inventory.product_id == product_id,
        Inventory.branch_id == branch_id
    ).first()
    
    if inventory:
        inventory.quantity -= quantity
        db.commit()
        db.refresh(inventory)
        return inventory
    return None