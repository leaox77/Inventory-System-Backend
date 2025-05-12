from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.sale import Sale
from app.schemas.sale import SaleCreate, SaleOut
from app.crud.sale import create_sale, get_sales, get_sale
from app.utils.security import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/sales", tags=["sales"])

@router.post("/", response_model=SaleOut, status_code=status.HTTP_201_CREATED)
def create_new_sale(
    sale: SaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        return create_sale(db=db, sale=sale, user_id=current_user.user_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear la venta: {str(e)}"
        )

@router.get("/", response_model=List[SaleOut])
def read_sales(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    branch_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return get_sales(db, skip=skip, limit=limit)

@router.get("/by-branch", response_model=List[SaleOut])
def get_sales_by_branch(
    branch_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtiene ventas filtradas por sucursal
    """
    return get_sales(db, branch_id=branch_id, skip=skip, limit=limit)

@router.get("/{sale_id}", response_model=SaleOut)
def read_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    sale = get_sale(db, sale_id=sale_id)
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venta no encontrada"
        )
    return sale

# Añade estas rutas al router de sales (/sales)

@router.get("/report/by-date", response_model=List[dict])
def get_sales_by_date(
    date_range: str = "week",  # week, month, year
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtiene ventas agrupadas por fecha"""
    from sqlalchemy import func, Date, cast
    from datetime import datetime, timedelta
    
    # Calcular fecha de inicio según el rango
    today = datetime.now().date()
    if date_range == "week":
        start_date = today - timedelta(days=7)
    elif date_range == "month":
        start_date = today - timedelta(days=30)
    elif date_range == "year":
        start_date = today - timedelta(days=365)
    else:
        start_date = today - timedelta(days=7)
    
    # Consulta para agrupar ventas por fecha
    sales_by_date = db.query(
        cast(Sale.sale_date, Date).label("date"),
        func.sum(Sale.total).label("total")
    ).filter(
        Sale.sale_date >= start_date
    ).group_by(
        cast(Sale.sale_date, Date)
    ).order_by(
        cast(Sale.sale_date, Date)
    ).all()
    
    return [{"date": str(date), "total": float(total)} for date, total in sales_by_date]

