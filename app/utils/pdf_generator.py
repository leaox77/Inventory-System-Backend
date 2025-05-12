# utils/pdf_generator.py
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from io import BytesIO
from datetime import datetime

def generate_invoice_pdf(sale):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Encabezado
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(1 * inch, height - 1 * inch, "FACTURA")

    # Datos de la venta
    pdf.setFont("Helvetica", 12)
    y = height - 1.5 * inch
    pdf.drawString(1 * inch, y, f"Factura Nº: {sale.invoice_number}")
    y -= 20
    pdf.drawString(1 * inch, y, f"Fecha: {sale.sale_date.strftime('%d/%m/%Y %H:%M')}")
    y -= 20
    pdf.drawString(1 * inch, y, f"Sucursal: {sale.branch.name if sale.branch else 'N/A'}")
    y -= 20
    pdf.drawString(1 * inch, y, f"Cliente: {sale.client.full_name if sale.client else 'N/A'}")
    y -= 20
    if sale.client:
        pdf.drawString(1 * inch, y, f"NIT/CI: {sale.client.ci_nit}")
        y -= 20
    pdf.drawString(1 * inch, y, f"Vendedor: {sale.user.username if sale.user else 'N/A'}")
    y -= 30

    # Tabla de productos
    data = [["Producto", "Cantidad", "P. Unit.", "Desc.", "Total"]]
    
    for detail in sale.details:
        data.append([
            detail.product.name if detail.product else f"Producto ID {detail.product_id}",
            str(detail.quantity),
            f"${detail.unit_price:.2f}",
            f"${detail.discount:.2f}",
            f"${detail.total_line:.2f}"
        ])
    
    # Crear tabla
    table = Table(data, colWidths=[3*inch, inch, inch, inch, inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    # Dibujar tabla
    table.wrapOn(pdf, width, height)
    table.drawOn(pdf, 1 * inch, y - len(data) * 20)
    y -= len(data) * 20 + 30

    # Totales
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawRightString(4.5 * inch, y, "Subtotal:")
    pdf.drawRightString(5.5 * inch, y, f"${sale.subtotal:.2f}")
    y -= 20
    pdf.drawRightString(4.5 * inch, y, "Descuento:")
    pdf.drawRightString(5.5 * inch, y, f"${sale.discount:.2f}")
    y -= 20
    pdf.drawRightString(4.5 * inch, y, "TOTAL:")
    pdf.drawRightString(5.5 * inch, y, f"${sale.total:.2f}")

    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()

def generate_sales_report_pdf(sales):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Encabezado
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(1 * inch, height - 1 * inch, "REPORTE DE VENTAS")

    # Fecha de generación
    pdf.setFont("Helvetica", 12)
    pdf.drawString(1 * inch, height - 1.3 * inch, f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    # Tabla de ventas
    data = [["Factura", "Fecha", "Cliente", "Sucursal", "Total", "Estado"]]
    
    for sale in sales:
        data.append([
            sale.invoice_number,
            sale.sale_date.strftime('%d/%m/%Y'),
            sale.client.full_name if sale.client else "N/A",
            sale.branch.name if sale.branch else "N/A",
            f"${sale.total:.2f}",
            sale.status
        ])
    
    # Crear tabla
    table = Table(data, colWidths=[1.5*inch, inch, 2*inch, inch, inch, inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8)
    ]))
    
    # Dibujar tabla
    table.wrapOn(pdf, width, height)
    table.drawOn(pdf, 0.5 * inch, height - 2 * inch - len(data) * 15)

    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()