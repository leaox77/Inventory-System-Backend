from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductOut, ProductUpdate
from app.utils.security import get_current_active_user
from app.crud.product import create_product, get_product, update_product, delete_product
from app.models.user import User
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
    unit_type: Optional[str] = None,
    branch_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    try:
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
        if unit_type:
            query = query.filter(Product.unit_type == unit_type)
        
        total = query.count()
        products = query.offset(skip).limit(limit).all()
        
        # Usar model_validate en lugar de from_orm
        products_data = [ProductOut.model_validate(product).model_dump() for product in products]
        
        return {
            "items": products_data,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        print(f"Error en read_products: {str(e)}")  # Log para depuración
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