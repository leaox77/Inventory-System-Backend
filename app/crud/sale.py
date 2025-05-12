from sqlalchemy.orm import Session, joinedload
from ..models.sale import Sale, SaleDetail
from ..models.inventory import Inventory  # Import Inventory model
from ..models.client import Client  # Import Client model
from ..models.product import Product  # Import Product model
from ..models.payment_method import PaymentMethod  # Import PaymentMethod model
from ..schemas.sale import SaleCreate
from ..utils.sales import generate_invoice_number
from datetime import datetime  # Import datetime
from decimal import Decimal

def create_sale(db: Session, sale: SaleCreate, user_id: int):
    # Verificar cliente si se proporcionó ID
    if sale.client_id:
        client = db.query(Client).filter(Client.client_id == sale.client_id).first()
        if not client:
            raise ValueError("Cliente no encontrado")
    
    # Verificar que el método de pago existe
    payment_method = db.query(PaymentMethod).filter(
        PaymentMethod.payment_method_id == sale.payment_method_id
    ).first()
    if not payment_method:
        raise ValueError("Método de pago no encontrado")

    # Verificar stock antes de crear la venta
    for item in sale.items:
        inventory = db.query(Inventory).filter(
            Inventory.product_id == item.product_id,
            Inventory.branch_id == sale.branch_id
        ).first()
        
        if not inventory or inventory.quantity < item.quantity:
            product = db.query(Product).filter(Product.product_id == item.product_id).first()
            product_name = product.name if product else f"ID {item.product_id}"
            raise ValueError(f"Stock insuficiente para {product_name} en la sucursal seleccionada")
    
    # Calcular totales
    subtotal = sum(item.unit_price * item.quantity for item in sale.items)
    total = subtotal - (sale.discount or 0)

    # Crear la venta
    db_sale = Sale(
        invoice_number=generate_invoice_number(),
        client_id=sale.client_id,
        user_id=user_id,
        branch_id=sale.branch_id,
        subtotal=subtotal,
        discount=sale.discount or 0,
        total=total,
        payment_method_id=sale.payment_method_id,
        status="COMPLETADA",
        sale_date=datetime.utcnow()
    )
    
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    
    # Crear detalles de venta y actualizar inventario
    for item in sale.items:
        db_detail = SaleDetail(
            sale_id=db_sale.sale_id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            discount=item.discount or 0,
            total_line=item.unit_price * item.quantity - (item.discount or 0)
        )
        db.add(db_detail)
        
        # Actualizar inventario
        db_inventory = db.query(Inventory).filter(
            Inventory.product_id == item.product_id,
            Inventory.branch_id == sale.branch_id
        ).first()
        db_inventory.quantity -= Decimal(str(item.quantity))
        db.add(db_inventory)
    
    db.commit()
    return db_sale

def get_sales(db: Session, skip: int = 0, limit: int = 100, status: str = None, branch_id: int = None):
    query = db.query(Sale).options(
        joinedload(Sale.client),  # Carga eager del cliente
        joinedload(Sale.branch),  # Carga eager de la sucursal
        joinedload(Sale.payment_method),  # <-- Añade esta línea
        joinedload(Sale.details).joinedload(SaleDetail.product)  # Carga eager de detalles y productos
    )
    
    if status:
        query = query.filter(Sale.status == status)
    if branch_id:
        query = query.filter(Sale.branch_id == branch_id)
        
    return query.offset(skip).limit(limit).all()

def get_sale(db: Session, sale_id: int):
    return db.query(Sale).options(
        joinedload(Sale.client),
        joinedload(Sale.branch),
        joinedload(Sale.payment_method),
        joinedload(Sale.details).joinedload(SaleDetail.product)
    ).filter(Sale.sale_id == sale_id).first()