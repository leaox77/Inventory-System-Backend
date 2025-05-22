from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi.responses import StreamingResponse
from io import BytesIO
from sqlalchemy.orm import joinedload
from datetime import datetime

from app.database import get_db
from app.models.sale import Sale, SaleDetail
from app.models.product import Product
from app.models.branch import Branch
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
    query = db.query(Sale)
    
    if status:
        query = query.filter(Sale.status == status)
    if branch_id:
        query = query.filter(Sale.branch_id == branch_id)
        
    return query.offset(skip).limit(limit).all()

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
    
# Añade estas rutas a tu sales.py

@router.get("/report", response_model=dict)
def get_sales_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtiene un reporte completo de ventas para el dashboard"""
    try:
        from sqlalchemy import func, desc
        
        # Total de ventas
        total_sales = db.query(func.sum(Sale.total)).scalar() or 0
        
        # Cantidad de ventas
        sales_count = db.query(Sale).count()
        
        # Promedio de ventas
        average_sale = total_sales / sales_count if sales_count > 0 else 0
        
        # Ventas por fecha (últimos 7 días)
        sales_by_date = db.query(
            func.date(Sale.sale_date).label("date"),
            func.sum(Sale.total).label("total")
        ).group_by(
            func.date(Sale.sale_date)
        ).order_by(
            func.date(Sale.sale_date).desc()
        ).limit(7).all()
        
        # Ventas por categoría
        sales_by_category = db.query(
            Product.category_id,
            func.sum(SaleDetail.quantity).label("quantity"),
            func.sum(SaleDetail.total_line).label("total")
        ).join(
            SaleDetail, SaleDetail.product_id == Product.product_id
        ).join(
            Sale, Sale.sale_id == SaleDetail.sale_id
        ).group_by(
            Product.category_id
        ).all()
        
        # Ventas por sucursal
        sales_by_branch = db.query(
            Branch.branch_id,
            Branch.name.label("branch_name"),
            func.sum(Sale.total).label("total")
        ).join(
            Sale, Sale.branch_id == Branch.branch_id
        ).group_by(
            Branch.branch_id,
            Branch.name
        ).all()
        
        return {
            "totalSales": float(total_sales),
            "salesCount": sales_count,
            "averageSale": float(average_sale),
            "salesByDate": [{
                "date": str(date),
                "total": float(total) if total else 0
            } for date, total in sales_by_date],
            "salesByCategory": [{
                "category_id": c.category_id,
                "category": "Categoría " + str(c.category_id),
                "total": float(c.total) if c.total else 0
            } for c in sales_by_category],
            "salesByBranch": [{
                "branch_id": b.branch_id,
                "branch": b.branch_name,
                "total": float(b.total) if b.total else 0
            } for b in sales_by_branch]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary", response_model=dict)
def get_sales_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtiene un resumen de ventas"""
    try:
        from sqlalchemy import func
        
        total_sales = db.query(func.sum(Sale.total)).scalar() or 0
        sales_count = db.query(Sale).count()
        average_sale = total_sales / sales_count if sales_count > 0 else 0
        
        return {
            "totalSales": float(total_sales),
            "salesCount": sales_count,
            "averageSale": float(average_sale)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/top-products", response_model=List[dict])
def get_top_products(
    limit: int = 5,
    order: str = 'desc',
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtiene los productos más o menos vendidos"""
    try:
        from sqlalchemy import func, desc, asc
        
        order_func = desc if order == 'desc' else asc
        
        products = db.query(
            Product.product_id,
            Product.name,
            func.sum(SaleDetail.quantity).label("total_sold"),
            func.sum(SaleDetail.total_line).label("total_revenue")
        ).join(
            SaleDetail, SaleDetail.product_id == Product.product_id
        ).join(
            Sale, Sale.sale_id == SaleDetail.sale_id
        ).group_by(
            Product.product_id,
            Product.name
        ).order_by(
            order_func("total_sold")
        ).limit(limit).all()
        
        return [{
            "product_id": p.product_id,
            "name": p.name,
            "total_sold": float(p.total_sold) if p.total_sold else 0,
            "total_revenue": float(p.total_revenue) if p.total_revenue else 0
        } for p in products]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/by-branch", response_model=List[dict])
def get_sales_by_branch(
    branch_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtiene ventas por sucursal"""
    try:
        from sqlalchemy import func
        query = db.query(
            Branch.branch_id,
            Branch.name.label("branch_name"),
            func.sum(Sale.total).label("total_sales"),
            func.count(Sale.sale_id).label("sales_count")
        ).join(
            Sale, Sale.branch_id == Branch.branch_id
        ).group_by(
            Branch.branch_id,
            Branch.name
        )
        
        if branch_id:
            query = query.filter(Branch.branch_id == branch_id)
            
        results = query.all()
        
        return [{
            "branch_id": r.branch_id,
            "branch_name": r.branch_name,
            "total_sales": float(r.total_sales) if r.total_sales else 0,
            "sales_count": r.sales_count
        } for r in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))