# crud/purchase_order.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.sql import text  # Import the text function
from fastapi import HTTPException, status  # Import HTTPException
from app.models.supplier import PurchaseOrder
from app.models.product import Product  # Import the Product model
from app.models.supplier import PurchaseOrderItem  # Import the PurchaseOrderItem model
from app.models.inventory import Inventory  # Import the Inventory model
from datetime import datetime
from decimal import Decimal  # Import Decimal
from app.schemas.purchase_order import PurchaseOrderCreate, PurchaseOrderOut  # Import the missing schemas

def update_order_status(db: Session, order_id: int, status_data):
    db_order = db.query(PurchaseOrder).filter(PurchaseOrder.order_id == order_id).first()
    if not db_order:
        return None

    # Validar transiciones de estado
    if db_order.status == 'CANCELLED' and status_data.status != 'CANCELLED':
        raise ValueError("No se puede modificar una orden cancelada")

    if db_order.status == 'DELIVERED' and status_data.status != 'DELIVERED':
        raise ValueError("No se puede modificar una orden ya entregada")

    # Lógica especial para aprobación
    if status_data.status == 'APPROVED' and db_order.status == 'PENDING':
        try:
            # Actualizar el inventario al aprobar la orden
            for item in db_order.items:  # Acceder a los items a través de la relación
                inventory_item = (
                    db.query(Inventory)
                    .filter(
                        Inventory.product_id == item.product_id,
                        Inventory.branch_id == db_order.branch_id,
                    )
                    .first()
                )
                if inventory_item:
                    inventory_item.quantity += item.quantity  # Aumentar la cantidad
                else:
                    # Si no existe un registro de inventario para ese producto y sucursal, créalo
                    new_inventory_item = Inventory(
                        product_id=item.product_id,
                        branch_id=db_order.branch_id,
                        quantity=item.quantity
                    )
                    db.add(new_inventory_item)

            db_order.status = status_data.status
            db.session.commit()

        except SQLAlchemyError as e:
            db.rollback()
            raise ValueError(f"Error al actualizar el inventario: {str(e)}")

    db_order.status = status_data.status
    if status_data.notes:
        db_order.notes = status_data.notes

    db.commit()
    db.refresh(db_order)
    return db_order

def create_purchase_order(db: Session, order_data, user_id: int):
    try:
        # 1. Validar productos
        product_ids = [item.product_id for item in order_data.items]
        existing_products = db.query(Product.product_id).filter(
            Product.product_id.in_(product_ids)
        ).all()
        
        if len(existing_products) != len(product_ids):
            missing_ids = set(product_ids) - {p.product_id for p in existing_products}
            raise HTTPException(400, detail=f"Productos no encontrados: {missing_ids}")

        # 2. Crear la orden
        total_amount = sum(
            Decimal(str(item.quantity)) * Decimal(str(item.unit_cost))
            for item in order_data.items
        )
        
        db_order = PurchaseOrder(
            supplier_id=order_data.supplier_id,
            branch_id=order_data.branch_id,
            expected_delivery_date=order_data.expected_delivery_date,
            status=order_data.status,
            total_amount=float(total_amount),
            notes=order_data.notes,
            created_by=user_id
        )
        db.add(db_order)
        db.flush()

        # 3. Procesar items y actualizar inventario
        for item in order_data.items:
            # Guardar item de orden
            db.add(PurchaseOrderItem(
                order_id=db_order.order_id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_cost=item.unit_cost
            ))

            # Opción 1: Usar merge (alternativa si no puedes modificar la BD)
            inventory = db.query(Inventory).filter(
                Inventory.product_id == item.product_id,
                Inventory.branch_id == order_data.branch_id
            ).first()
            
            if inventory:
                inventory.quantity += Decimal(str(item.quantity))
            else:
                db.add(Inventory(
                    product_id=item.product_id,
                    branch_id=order_data.branch_id,
                    quantity=item.quantity
                ))

            # Opción 2: Si puedes modificar la BD, añade la migración SQL:
            """
            ALTER TABLE inventory 
            ADD CONSTRAINT _inventory_product_branch_uc 
            UNIQUE (product_id, branch_id);
            """

        db.commit()
        return db_order

    except Exception as e:
        db.rollback()
        raise HTTPException(500, detail=f"Error al crear orden: {str(e)}")