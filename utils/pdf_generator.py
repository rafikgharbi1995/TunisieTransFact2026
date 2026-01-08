from fpdf import FPDF
from datetime import datetime
import os


class InvoicePDF(FPDF):
    def __init__(self, invoice_data, company_data):
        super().__init__()
        self.invoice_data = invoice_data
        self.company_data = company_data

    def header(self):
        # Logo
        if os.path.exists("assets/logo.png"):
            self.image("assets/logo.png", 10, 8, 33)

        # Titre
        self.set_font('Arial', 'B', 16)
        self.cell(80)
        self.cell(30, 10, 'FACTURE', 0, 0, 'C')

        # Numéro de facture
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, f"N° {self.invoice_data['id']}", 0, 1, 'R')
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def add_company_info(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, self.company_data['name'], 0, 1)

        self.set_font('Arial', '', 10)
        self.cell(0, 5, f"Matricule Fiscal: {self.company_data['matricule_fiscal']}", 0, 1)
        self.cell(0, 5, self.company_data['address'], 0, 1)
        self.cell(0, 5, f"Tél: {self.company_data['phone']} | Email: {self.company_data['email']}", 0, 1)
        self.ln(10)

    def add_client_info(self):
        self.set_font('Arial', 'B', 11)
        self.cell(0, 10, 'CLIENT:', 0, 1)

        self.set_font('Arial', '', 10)
        self.cell(0, 5, f"Nom: {self.invoice_data['client_name']}", 0, 1)
        self.cell(0, 5, f"Matricule: {self.invoice_data['client_id']}", 0, 1)
        if self.invoice_data.get('client_address'):
            self.cell(0, 5, f"Adresse: {self.invoice_data['client_address']}", 0, 1)
        self.ln(10)

    def add_invoice_details(self):
        self.set_font('Arial', '', 10)
        self.cell(50, 6, f"Date de facturation: {self.invoice_data['invoice_date']}", 0, 0)
        self.cell(0, 6, f"Date d'échéance: {self.invoice_data['due_date']}", 0, 1)
        self.ln(5)

    def add_items_table(self):
        # En-tête du tableau
        self.set_font('Arial', 'B', 10)
        self.set_fill_color(200, 220, 255)

        col_widths = [80, 20, 30, 25, 35]
        headers = ['Description', 'Qté', 'Prix unitaire', 'TVA %', 'Total HT']

        for i, header in enumerate(headers):
            self.cell(col_widths[i], 7, header, 1, 0, 'C', True)
        self.ln()

        # Articles
        self.set_font('Arial', '', 10)
        fill = False

        for item in self.invoice_data['items']:
            self.cell(col_widths[0], 6, item['description'][:50], 'LR', 0, 'L', fill)
            self.cell(col_widths[1], 6, str(item['quantity']), 'LR', 0, 'C', fill)
            self.cell(col_widths[2], 6, f"{item['unit_price']:,.2f} DT", 'LR', 0, 'R', fill)
            self.cell(col_widths[3], 6, f"{item['tva_rate']}%", 'LR', 0, 'C', fill)
            self.cell(col_widths[4], 6, f"{item['total_ht']:,.2f} DT", 'LR', 0, 'R', fill)
            self.ln()
            fill = not fill

        # Ligne de fermeture
        self.cell(sum(col_widths), 0, '', 'T')
        self.ln(10)

    def add_totals(self):
        self.set_font('Arial', 'B', 11)

        col_width = 50
        self.cell(120)
        self.cell(col_width, 8, 'Total HT:', 0, 0, 'R')
        self.cell(0, 8, f"{self.invoice_data['total_ht']:,.2f} DT", 0, 1, 'R')

        self.cell(120)
        self.cell(col_width, 8, 'TVA:', 0, 0, 'R')
        self.cell(0, 8, f"{self.invoice_data['tva_amount']:,.2f} DT", 0, 1, 'R')

        self.set_font('Arial', 'B', 12)
        self.set_text_color(0, 100, 0)
        self.cell(120)
        self.cell(col_width, 10, 'Total TTC:', 0, 0, 'R')
        self.cell(0, 10, f"{self.invoice_data['total_ttc']:,.2f} DT", 0, 1, 'R')

        self.set_text_color(0, 0, 0)
        self.ln(15)

    def add_payment_info(self):
        self.set_font('Arial', 'B', 10)
        self.cell(0, 8, 'INFORMATIONS DE PAIEMENT:', 0, 1)

        self.set_font('Arial', '', 9)
        self.cell(0, 5, f"RIB: {self.company_data['rib']}", 0, 1)
        self.cell(0, 5, f"Banque: Banque de Tunisie", 0, 1)
        self.cell(0, 5, f"Code Swift: BSTUTNTT", 0, 1)
        self.ln(10)

    def add_notes(self):
        if self.invoice_data.get('notes'):
            self.set_font('Arial', 'I', 9)
            self.multi_cell(0, 5, f"Notes: {self.invoice_data['notes']}")
            self.ln(5)


def generate_invoice_pdf(invoice_data, company_data, filename=None):
    """Génère un PDF de facture"""
    if filename is None:
        filename = f"Facture_{invoice_data['id']}_{datetime.now().strftime('%Y%m%d')}.pdf"

    pdf = InvoicePDF(invoice_data, company_data)
    pdf.add_page()

    pdf.add_company_info()
    pdf.add_client_info()
    pdf.add_invoice_details()
    pdf.add_items_table()
    pdf.add_totals()
    pdf.add_payment_info()
    pdf.add_notes()

    pdf.output(filename)
    return filename