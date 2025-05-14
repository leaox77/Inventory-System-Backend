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
    table = Table(
        data,
        colWidths=[1.5*inch, inch, 1.2*inch, 1.8*inch, inch, inch]
    )
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

    # Dejar espacio para encabezado y fecha
    x_offset = 0.8 * inch
    y_start_table = height - 2.2 * inch  # Espacio debajo del encabezado y fecha
    table_width, table_height = table.wrap(0, 0)

    # La tabla debe comenzar en y_start_table y dibujarse hacia abajo
    table.drawOn(pdf, x_offset, y_start_table - table_height)

    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()

def generate_sales_csv(sales):
    import csv
    from io import StringIO
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Encabezados
    writer.writerow([
        'Factura', 'Fecha', 'Cliente', 'NIT/CI', 'Sucursal',
        'Método de Pago', 'Subtotal', 'Descuento', 'Total', 'Estado',
        'Productos', 'Cantidad', 'Precio Unitario', 'Total Producto'
    ])
    
    for sale in sales:
        # Datos principales de la venta
        main_data = [
            sale.invoice_number,
            sale.sale_date.strftime('%Y-%m-%d %H:%M'),
            sale.client.full_name if sale.client else 'N/A',
            sale.client.ci_nit if sale.client else 'N/A',
            sale.branch.name if sale.branch else 'N/A',
            sale.payment_method.name if sale.payment_method else 'N/A',
            str(sale.subtotal),
            str(sale.discount),
            str(sale.total),
            sale.status
        ]
        
        # Detalles de productos
        for detail in sale.details:
            product_data = [
                detail.product.name if detail.product else f'Producto ID {detail.product_id}',
                str(detail.quantity),
                str(detail.unit_price),
                str(detail.total_line)
            ]
            
            # Escribir una línea combinando datos principales y de producto
            writer.writerow(main_data + product_data)
    
    return output.getvalue()