from datetime import datetime
from typing import List, Dict


def calculate_tva(amount_ht: float, tva_rate: float = 19.0) -> float:
    """Calcule le montant de TVA"""
    return round(amount_ht * (tva_rate / 100), 3)


def calculate_total_ttc(amount_ht: float, tva_rate: float = 19.0) -> float:
    """Calcule le montant TTC"""
    return round(amount_ht * (1 + tva_rate / 100), 3)


def calculate_profit(revenue: float, expenses: float) -> float:
    """Calcule le bénéfice"""
    return revenue - expenses


def calculate_tax_declaration(invoices: List[Dict], purchases: List[Dict]) -> Dict:
    """Calcule la déclaration fiscale"""
    total_revenue = sum(inv['total_amount'] for inv in invoices)
    total_purchases = sum(pur['total_amount'] for pur in purchases)

    # TVA collectée
    tva_collected = sum(inv.get('tva_amount', 0) for inv in invoices)

    # TVA déductible
    tva_deductible = sum(pur.get('tva_amount', 0) for pur in purchases)

    # TVA à payer
    tva_payable = max(0, tva_collected - tva_deductible)

    return {
        'total_revenue': total_revenue,
        'total_purchases': total_purchases,
        'tva_collected': tva_collected,
        'tva_deductible': tva_deductible,
        'tva_payable': tva_payable,
        'net_profit': total_revenue - total_purchases
    }


def generate_invoice_number(last_number: int = 0) -> str:
    """Génère un numéro de facture séquentiel"""
    current_year = datetime.now().year
    current_month = datetime.now().strftime('%m')
    next_number = last_number + 1
    return f"FACT-{current_year}{current_month}-{next_number:04d}"


def calculate_payment_status(due_date: datetime, payment_date: datetime = None) -> str:
    """Détermine le statut de paiement"""
    if payment_date:
        return "payée"
    elif datetime.now() > due_date:
        return "en retard"
    else:
        return "en attente"