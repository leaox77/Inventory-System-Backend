from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import (
    Role, User, Category, Product, 
    Branch, Inventory, Client
)
from app.utils.security import get_password_hash

def init_db():
    db = SessionLocal()

    # Roles
    admin_role = Role(name="Admin", permissions={"all": True})
    manager_role = Role(name="Manager", permissions={"reports": True, "inventory": True})
    cashier_role = Role(name="Cashier", permissions={"sales": True})
    
    db.add_all([admin_role, manager_role, cashier_role])
    db.commit()

    # Usuarios
    admin_user = User(
        username="admin",
        email="admin@supermarket.com",
        password_hash=get_password_hash("Admin123"),
        full_name="Administrador Principal",
        is_superuser=True,
        role_id=admin_role.id
    )
    
    db.add(admin_user)
    db.commit()

    # Categorías
    categories = [
        Category(name="Abarrotes", description="Productos básicos no perecederos"),
        Category(name="Lácteos", description="Leche, quesos y derivados", needs_refrigeration=True),
        Category(name="Carnes", description="Cortes frescos y embutidos", needs_refrigeration=True)
    ]
    
    db.add_all(categories)
    db.commit()

    # Sucursales
    branches = [
        Branch(name="Sucursal Centro", address="Av. Principal 123", phone="+5912123456"),
        Branch(name="Sucursal Norte", address="Calle Norte 456", phone="+5912123457")
    ]
    
    db.add_all(branches)
    db.commit()

    # Productos
    products = [
        Product(barcode="777123456001", name="Arroz Saborá 5kg", category_id=1, unit_type="paquete", price=25.50),
        Product(barcode="777123456002", name="Leche Pil 1L", category_id=2, unit_type="litro", price=6.20),
        Product(barcode="777123456003", name="Pollo Sofía kg", category_id=3, unit_type="kg", price=15.90)
    ]
    
    db.add_all(products)
    db.commit()

    # Inventario
    inventory = [
        Inventory(product_id=1, branch_id=1, quantity=50),
        Inventory(product_id=2, branch_id=1, quantity=100),
        Inventory(product_id=3, branch_id=1, quantity=30)
    ]
    
    db.add_all(inventory)
    db.commit()

    print("Datos de prueba creados exitosamente")

if __name__ == "__main__":
    init_db()