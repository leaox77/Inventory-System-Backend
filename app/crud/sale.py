from sqlalchemy.orm import Session
from ..models.sale import Sale, SaleDetail
from ..schemas.sale import SaleCreate
from ..utils.sales import generate_invoice_number

def create_sale(db: Session, sale: SaleCreate, user_id: int):
    db_sale = Sale(
        invoice_number=generate_invoice_number(),
        client_id=sale.client_id,
        user_id=user_id,
        branch_id=sale.branch_id,
        subtotal=sum(item.unit_price * item.quantity for item in sale.items),
        discount=sale.discount,
        total=sum(item.unit_price * item.quantity for item in sale.items) - sale.discount,
        payment_method=sale.payment_method,
    )
    
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    
    for item in sale.items:
        db_detail = SaleDetail(
            sale_id=db_sale.sale_id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            discount=item.discount,
            total_line=item.unit_price * item.quantity - item.discount
        )
        db.add(db_detail)
    
    db.commit()
    return db_sale

def get_sales(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Sale).offset(skip).limit(limit).all()