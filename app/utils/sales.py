# utils/sales.py
from datetime import datetime
import random
import string
from app.models import Inventory, Product  # Import the Inventory and Product models

def generate_invoice_number():
    # Formato: YYYYMMDD-XXXXX (ej. 20230515-ABC123)
    date_part = datetime.now().strftime("%Y%m%d")
    random_part = ''.join(random.choices(
        string.ascii_uppercase + string.digits, 
        k=5
    ))
    return f"{date_part}-{random_part}"

def validate_sale_items(items, branch_id, db):
    """Valida que los productos tengan suficiente stock"""
    errors = []
    for item in items:
        inventory = db.query(Inventory).filter(
            Inventory.product_id == item.product_id,
            Inventory.branch_id == branch_id
        ).first()
        
        if not inventory:
            errors.append(f"Producto ID {item.product_id} no existe en la sucursal")
        elif inventory.quantity < item.quantity:
            product = db.query(Product).get(item.product_id)
            name = product.name if product else f"ID {item.product_id}"
            errors.append(f"Stock insuficiente para {name} (Stock: {inventory.quantity}, Pedido: {item.quantity})")
    
    if errors:
        raise ValueError("\n".join(errors))