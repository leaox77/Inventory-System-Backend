from sqlalchemy.orm import Session
from ..models.product import Product
from ..models.inventory import Inventory  # Import Inventory model
from ..schemas.product import ProductCreate, ProductUpdate

def get_product(db: Session, product_id: int):
    return db.query(Product).filter(Product.product_id == product_id).first()

def get_products(db: Session, skip: int = 0, limit: int = 200):
    return db.query(Product).filter(Product.is_active == True).offset(skip).limit(limit).all()

def create_product(db: Session, product: ProductCreate):
    # Convertir el schema Pydantic a un diccionario, excluyendo inventory_assignments
    product_data = product.model_dump(exclude={"inventory_assignments"})
    
    # Crear el producto
    db_product = Product(**product_data)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    # Crear registros de inventario si se proporcionaron asignaciones
    if product.inventory_assignments:
        for assignment in product.inventory_assignments:
            inventory = Inventory(
                product_id=db_product.product_id,
                branch_id=assignment.branch_id,
                quantity=assignment.quantity
            )
            db.add(inventory)
        db.commit()
    
    return db_product

def update_product(db: Session, product_id: int, product: ProductUpdate):
    db_product = get_product(db, product_id)
    if not db_product:
        return None
    
    # Actualizar campos del producto
    update_data = product.model_dump(exclude_unset=True, exclude={"inventory_assignments"})
    for field, value in update_data.items():
        setattr(db_product, field, value)

    db.commit()
    db.refresh(db_product)
    return db_product

def update_product_inventory(db: Session, product_id: int, inventory_assignments: list):
    # Eliminar asignaciones existentes
    db.query(Inventory).filter(Inventory.product_id == product_id).delete()
    
    # Agregar nuevas asignaciones
    if inventory_assignments:
        for assignment in inventory_assignments:
            inventory = Inventory(
                product_id=product_id,
                branch_id=assignment.branch_id,
                quantity=assignment.quantity
            )
            db.add(inventory)
    
    db.commit()

def delete_product(db: Session, product_id: int):
    db_product = get_product(db, product_id)
    if not db_product:
        return None
    
    # Eliminar registros de inventario primero
    db.query(Inventory).filter(Inventory.product_id == product_id).delete()
    
    db_product.is_active = False
    db.commit()
    return db_product