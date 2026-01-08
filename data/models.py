from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    STAFF = "staff"

class InvoiceStatus(str, Enum):
    DRAFT = "brouillon"
    SENT = "envoyée"
    PAID = "payée"
    OVERDUE = "en retard"

@dataclass
class User:
    username: str
    password_hash: str
    role: UserRole
    full_name: str
    email: Optional[str] = None

@dataclass
class BusinessProfile:
    name: str = "TunisieTrans SARL"
    matricule_fiscal: str = "1234567/A/M/000"
    address: str = "Zone Industrielle, Tunis, Tunisie"
    rib: str = "01 234 5678901234567 89"
    industry: str = "Transport et Logistique"
    target_audience: str = "Entreprises industrielles et commerciales"
    phone: str = "+216 71 234 567"
    email: str = "contact@tunisietrans.tn"
    capital_social: float = 100000.0

@dataclass
class Client:
    id: str
    name: str
    matricule_fiscal: str
    address: str
    phone: str
    email: str
    created_at: datetime
    credit_limit: float = 0.0
    payment_terms: int = 30
    notes: Optional[str] = None

@dataclass
class Invoice:
    id: str
    client_id: str
    date: datetime
    due_date: datetime
    total_amount: float
    tva_amount: float
    status: InvoiceStatus
    items: List[dict]
    notes: Optional[str] = None
    payment_date: Optional[datetime] = None

@dataclass
class Purchase:
    id: str
    supplier: str
    date: datetime
    total_amount: float
    tva_amount: float
    category: str
    invoice_number: str
    payment_status: str

@dataclass
class Reminder:
    id: str
    title: str
    due_date: datetime
    type: str  # 'tax', 'invoice', 'general'
    description: str
    completed: bool = False