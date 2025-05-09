from datetime import datetime

def generate_invoice_number(branch_id: int = 1):
    current_year = datetime.now().strftime('%Y')
    sequence = datetime.now().strftime('%m%d%H%M%S')
    return f"{branch_id:03d}-{current_year}-{sequence}"