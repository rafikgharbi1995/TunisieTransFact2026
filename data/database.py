import sqlite3
import json
from datetime import datetime
from typing import List, Optional
import pandas as pd
from .models import *


class Database:
    def __init__(self, db_path="data/tunisietrans.db"):
        self.db_path = db_path
        self.init_database()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_database(self):
        with self.get_connection() as conn:
            # Table des utilisateurs
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    email TEXT
                )
            ''')

            # Table du profil entreprise
            conn.execute('''
                CREATE TABLE IF NOT EXISTS business_profile (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    matricule_fiscal TEXT NOT NULL,
                    address TEXT NOT NULL,
                    rib TEXT NOT NULL,
                    industry TEXT NOT NULL,
                    target_audience TEXT NOT NULL,
                    phone TEXT,
                    email TEXT,
                    capital_social REAL
                )
            ''')

            # Table des clients
            conn.execute('''
                CREATE TABLE IF NOT EXISTS clients (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    matricule_fiscal TEXT NOT NULL,
                    address TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    email TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    credit_limit REAL DEFAULT 0.0,
                    payment_terms INTEGER DEFAULT 30,
                    notes TEXT
                )
            ''')

            # Table des factures
            conn.execute('''
                CREATE TABLE IF NOT EXISTS invoices (
                    id TEXT PRIMARY KEY,
                    client_id TEXT NOT NULL,
                    date TIMESTAMP NOT NULL,
                    due_date TIMESTAMP NOT NULL,
                    total_amount REAL NOT NULL,
                    tva_amount REAL NOT NULL,
                    status TEXT NOT NULL,
                    items TEXT NOT NULL,  # JSON array
                    notes TEXT,
                    payment_date TIMESTAMP,
                    FOREIGN KEY (client_id) REFERENCES clients (id)
                )
            ''')

            # Table des achats
            conn.execute('''
                CREATE TABLE IF NOT EXISTS purchases (
                    id TEXT PRIMARY KEY,
                    supplier TEXT NOT NULL,
                    date TIMESTAMP NOT NULL,
                    total_amount REAL NOT NULL,
                    tva_amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    invoice_number TEXT NOT NULL,
                    payment_status TEXT NOT NULL
                )
            ''')

            # Table des rappels
            conn.execute('''
                CREATE TABLE IF NOT EXISTS reminders (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    due_date TIMESTAMP NOT NULL,
                    type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    completed BOOLEAN DEFAULT 0
                )
            ''')

            conn.commit()

    # CRUD Operations pour les clients
    def add_client(self, client: Client):
        with self.get_connection() as conn:
            conn.execute('''
                INSERT INTO clients VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                client.id, client.name, client.matricule_fiscal, client.address,
                client.phone, client.email, client.created_at, client.credit_limit,
                client.payment_terms, client.notes
            ))
            conn.commit()

    def get_clients(self) -> List[Client]:
        with self.get_connection() as conn:
            cursor = conn.execute('SELECT * FROM clients')
            return [Client(*row) for row in cursor.fetchall()]

    # CRUD Operations pour les factures
    def add_invoice(self, invoice: Invoice):
        with self.get_connection() as conn:
            conn.execute('''
                INSERT INTO invoices VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                invoice.id, invoice.client_id, invoice.date, invoice.due_date,
                invoice.total_amount, invoice.tva_amount, invoice.status,
                json.dumps(invoice.items), invoice.notes, invoice.payment_date
            ))
            conn.commit()

    def get_invoices(self) -> List[Invoice]:
        with self.get_connection() as conn:
            cursor = conn.execute('SELECT * FROM invoices')
            invoices = []
            for row in cursor.fetchall():
                items = json.loads(row[7])
                invoices.append(Invoice(
                    id=row[0], client_id=row[1], date=row[2], due_date=row[3],
                    total_amount=row[4], tva_amount=row[5], status=row[6],
                    items=items, notes=row[8], payment_date=row[9]
                ))
            return invoices

    # Opérations pour le profil entreprise
    def save_profile(self, profile: BusinessProfile):
        with self.get_connection() as conn:
            # Vider la table et insérer le nouveau profil
            conn.execute('DELETE FROM business_profile')
            conn.execute('''
                INSERT INTO business_profile 
                (name, matricule_fiscal, address, rib, industry, 
                 target_audience, phone, email, capital_social)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                profile.name, profile.matricule_fiscal, profile.address,
                profile.rib, profile.industry, profile.target_audience,
                profile.phone, profile.email, profile.capital_social
            ))
            conn.commit()

    def get_profile(self) -> Optional[BusinessProfile]:
        with self.get_connection() as conn:
            cursor = conn.execute('SELECT * FROM business_profile LIMIT 1')
            row = cursor.fetchone()
            if row:
                return BusinessProfile(
                    name=row[1], matricule_fiscal=row[2], address=row[3],
                    rib=row[4], industry=row[5], target_audience=row[6],
                    phone=row[7], email=row[8], capital_social=row[9]
                )
            return None

    # Statistiques
    def get_monthly_stats(self, month: int, year: int):
        with self.get_connection() as conn:
            # Revenus du mois
            cursor = conn.execute('''
                SELECT SUM(total_amount) FROM invoices 
                WHERE strftime('%m', date) = ? AND strftime('%Y', date) = ?
            ''', (f"{month:02d}", str(year)))
            revenue = cursor.fetchone()[0] or 0

            # Dépenses du mois
            cursor = conn.execute('''
                SELECT SUM(total_amount) FROM purchases 
                WHERE strftime('%m', date) = ? AND strftime('%Y', date) = ?
            ''', (f"{month:02d}", str(year)))
            expenses = cursor.fetchone()[0] or 0

            return {
                'revenue': revenue,
                'expenses': expenses,
                'profit': revenue - expenses
            }


# Instance globale de la base de données
db = Database()