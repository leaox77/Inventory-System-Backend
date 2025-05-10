from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app.database import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductOut, ProductUpdate
from app.utils.security import get_current_active_user
from app.crud.product import create_product, get_product, update_product, delete_product
from app.models.user import User
from app.models.inventory import Inventory  # Import Inventory model
from pydantic import ConfigDict

router = APIRouter(prefix="/products", tags=["products"])

# Actualizar el modelo ProductOut para usar from_attributes
class ProductOut(ProductOut):
    model_config = ConfigDict(from_attributes=True)  # Esto reemplaza a from_orm

@router.get("/", response_model=Dict[str, Any])
def read_products(
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    unit_type: Optional[int] = None,
    branch_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    try:
        # Consulta base de productos
        query = db.query(Product).filter(Product.is_active == True)
        
        if search:
            query = query.filter(
                or_(
                    Product.name.ilike(f"%{search}%"),
                    Product.description.ilike(f"%{search}%")
                )
            )
        
        if category_id is not None:
            query = query.filter(Product.category_id == category_id)
        if unit_type is not None:
            query = query.filter(Product.unit_type == unit_type)
        
        total = query.count()
        products = query.offset(skip).limit(limit).all()
        
        # Obtener el inventario para estos productos
        product_ids = [p.product_id for p in products]
        
        # Consulta de inventario
        inventory_query = db.query(
            Inventory.product_id,
            Inventory.branch_id,
            Inventory.quantity
        ).filter(
            Inventory.product_id.in_(product_ids)
        )
        
        if branch_id is not None:
            inventory_query = inventory_query.filter(Inventory.branch_id == branch_id)
        
        inventory_data = inventory_query.all()
        
        # Organizar el inventario por producto
        inventory_by_product = {}
        for item in inventory_data:
            if item.product_id not in inventory_by_product:
                inventory_by_product[item.product_id] = []
            inventory_by_product[item.product_id].append({
                "branch_id": item.branch_id,
                "quantity": float(item.quantity) if item.quantity else 0
            })
        
        # Construir la respuesta
        products_data = []
        for product in products:
            product_dict = ProductOut.model_validate(product).model_dump()
            
            # Calcular el stock según el filtro
            inventory_items = inventory_by_product.get(product.product_id, [])
            
            if branch_id:
                # Stock solo para la sucursal filtrada
                branch_item = next((item for item in inventory_items if item["branch_id"] == branch_id), None)
                product_dict["stock"] = branch_item["quantity"] if branch_item else 0
            else:
                # Stock total de todas las sucursales
                product_dict["stock"] = sum(item["quantity"] for item in inventory_items)
            
            product_dict["inventory_items"] = inventory_items
            products_data.append(product_dict)
        
        return {
            "items": products_data,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        print(f"Error en read_products: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener productos: {str(e)}"
        )
@router.post("/", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_new_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para realizar esta acción"
        )
    return create_product(db, product=product)

@router.get("/{product_id}", response_model=ProductOut)
def read_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    product = get_product(db, product_id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    return product

@router.put("/{product_id}", response_model=ProductOut)
def update_existing_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para realizar esta acción"
        )
    db_product = update_product(db, product_id=product_id, product=product)
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    return db_product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para realizar esta acción"
        )
    if not delete_product(db, product_id=product_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )

@router.get("/search/", response_model=ProductOut)
def read_product_by_name(
    name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    product = db.query(Product).filter(Product.name == name, Product.is_active == True).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    return product

@router.get("/{product_id}/min_stock", response_model=int)
def get_min_stock(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    product = get_product(db, product_id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    return product.min_stock

@router.get("/{product_id}/stock", response_model=int)
def get_product_stock(
    product_id: int,
    branch_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Buscar el producto
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    
    # Consulta base
    query = db.query(func.sum(Inventory.quantity)).filter(
        Inventory.product_id == product_id
    )
    
    # Filtrar por sucursal si se especifica
    if branch_id is not None:
        query = query.filter(Inventory.branch_id == branch_id)
    
    # Obtener el stock
    stock = query.scalar() or 0
    
    return stock
