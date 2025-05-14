from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi.responses import StreamingResponse
from io import BytesIO
from sqlalchemy.orm import joinedload
from datetime import datetime

from app.database import get_db
from app.models.sale import Sale, SaleDetail
from app.schemas.sale import SaleCreate, SaleOut
from app.crud.sale import create_sale, get_sales, get_sale
from app.utils.security import get_current_active_user
from app.models.user import User
from app.utils.pdf_generator import generate_invoice_pdf, generate_sales_csv

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

@router.get("/{sale_id}/invoice")
def generate_invoice(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Obtener la venta con todas las relaciones necesarias
    sale = db.query(Sale).options(
        joinedload(Sale.client),
        joinedload(Sale.branch),
        joinedload(Sale.user),
        joinedload(Sale.payment_method),
        joinedload(Sale.details).joinedload(SaleDetail.product)
    ).filter(Sale.sale_id == sale_id).first()
    
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venta no encontrada"
        )
    
    # Generar el PDF
    pdf_content = generate_invoice_pdf(sale)
    
    # Configurar la respuesta
    headers = {
        'Content-Disposition': f'attachment; filename="factura_{sale.invoice_number}.pdf"'
    }
    return StreamingResponse(
        BytesIO(pdf_content),
        media_type='application/pdf',
        headers=headers
    )

from app.utils.pdf_generator import generate_sales_report_pdf
from fastapi import Response

@router.get("/export/{format}")
def export_sales(
    format: str,
    db: Session = Depends(get_db),
    status: Optional[str] = None,
    branch_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    try:
        # Obtener las ventas filtradas con todos los detalles necesarios
        query = db.query(Sale).options(
            joinedload(Sale.client),
            joinedload(Sale.branch),
            joinedload(Sale.payment_method),
            joinedload(Sale.details).joinedload(SaleDetail.product)
        )
        
        if status:
            query = query.filter(Sale.status == status)
        if branch_id:
            query = query.filter(Sale.branch_id == branch_id)
        if start_date:
            query = query.filter(Sale.sale_date >= start_date)
        if end_date:
            query = query.filter(Sale.sale_date <= end_date)
        
        sales = query.order_by(Sale.sale_date.desc()).all()
        
        if format == 'pdf':
            pdf_content = generate_sales_report_pdf(sales)
            headers = {
                'Content-Disposition': f'attachment; filename="reporte_ventas_{datetime.now().strftime("%Y%m%d")}.pdf"'
            }
            return StreamingResponse(
                BytesIO(pdf_content),
                media_type='application/pdf',
                headers=headers
            )
        elif format == 'csv':
            # Implementar generación de CSV
            csv_content = generate_sales_csv(sales)
            headers = {
                'Content-Disposition': f'attachment; filename="reporte_ventas_{datetime.now().strftime("%Y%m%d")}.csv"'
            }
            return StreamingResponse(
                BytesIO(csv_content.encode('utf-8')),
                media_type='text/csv',
                headers=headers
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Formato no soportado. Use 'pdf' o 'csv'"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar el reporte: {str(e)}"
        )