import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
import os

# ================= CONFIGURATION =================
st.set_page_config(
    page_title="TunisieTrans - Gestion Complète",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= ÉTAT DE L'APPLICATION =================
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = 'staff'
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'dashboard'

# Initialisation des données
if 'invoices' not in st.session_state:
    st.session_state.invoices = []
if 'purchases' not in st.session_state:
    st.session_state.purchases = []
if 'clients' not in st.session_state:
    st.session_state.clients = []
if 'profile' not in st.session_state:
    st.session_state.profile = {
        'name': 'TunisieTrans SARL',
        'matricule_fiscal': '1234567/A/M/000',
        'address': 'Zone Industrielle, Tunis, Tunisie',
        'rib': '01 234 5678901234567 89',
        'industry': 'Transport et Logistique',
        'phone': '+216 71 234 567',
        'email': 'contact@tunisietrans.tn',
        'capital': 100000.0
    }


# ================= FONCTIONS UTILITAIRES =================
def generate_id(prefix):
    """Génère un ID unique"""
    import uuid
    return f"{prefix}-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"


def calculate_tva(amount, rate=19):
    """Calcule la TVA"""
    return round(amount * rate / 100, 3)


def save_data():
    """Sauvegarde les données en JSON"""
    data = {
        'invoices': st.session_state.invoices,
        'purchases': st.session_state.purchases,
        'clients': st.session_state.clients,
        'profile': st.session_state.profile
    }
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=2)


def load_data():
    """Charge les données depuis JSON"""
    try:
        with open('data.json', 'r') as f:
            data = json.load(f)
            st.session_state.invoices = data.get('invoices', [])
            st.session_state.purchases = data.get('purchases', [])
            st.session_state.clients = data.get('clients', [])
            st.session_state.profile = data.get('profile', st.session_state.profile)
    except:
        pass


# ================= PAGES =================
def login_page():
    """Page de connexion"""
    st.title("🔐 Connexion - TunisieTrans SARL")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Nom d'utilisateur")
            password = st.text_input("Mot de passe", type="password")

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                login_admin = st.form_submit_button("👑 Admin", use_container_width=True)
            with col_btn2:
                login_staff = st.form_submit_button("👤 Staff", use_container_width=True)

            if login_admin:
                if username == "admin" and password == "admin123":
                    st.session_state.authenticated = True
                    st.session_state.user_role = "admin"
                    st.session_state.username = username
                    load_data()
                    st.success("Connecté en tant qu'administrateur!")
                    st.rerun()
                else:
                    st.error("Identifiants admin incorrects!")

            if login_staff:
                if username == "staff" and password == "staff123":
                    st.session_state.authenticated = True
                    st.session_state.user_role = "staff"
                    st.session_state.username = username
                    load_data()
                    st.success("Connecté en tant qu'employé!")
                    st.rerun()
                else:
                    st.error("Identifiants incorrects!")

        with st.expander("📋 Comptes de test"):
            st.code("Admin: admin / admin123")
            st.code("Staff: staff / staff123")


def sidebar():
    """Barre latérale de navigation"""
    with st.sidebar:
        st.title("🚚 TunisieTrans")
        st.divider()

        # Menu principal
        menu_items = [
            ("🏠 Dashboard", "dashboard"),
            ("🧾 Factures Ventes", "invoices"),
            ("🛒 Achats & Dépenses", "purchases"),
            ("👥 Clients", "clients"),
            ("📊 Analytics", "analytics"),
            ("🤖 Assistant Fiscal", "tax-ai"),
            ("⏰ Rappels", "reminders"),
            ("📋 Déclaration", "declaration")
        ]

        for icon, view in menu_items:
            if st.button(icon, use_container_width=True, key=f"btn_{view}"):
                st.session_state.current_view = view
                st.rerun()

        if st.session_state.user_role == "admin":
            st.divider()
            st.subheader("⚙️ Administration")
            if st.button("👑 Gestion Utilisateurs", use_container_width=True):
                st.session_state.current_view = "users"
                st.rerun()

        st.divider()
        st.write(f"👤 {st.session_state.username}")
        st.write(f"📋 {st.session_state.user_role}")

        if st.button("🚪 Déconnexion", use_container_width=True, type="primary"):
            save_data()
            st.session_state.authenticated = False
            st.rerun()


# ================= FONCTIONNALITÉS PRINCIPALES =================
def show_dashboard():
    """Tableau de bord"""
    st.title("🏠 Tableau de Bord")

    # Métriques
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_ventes = sum(inv.get('total_ttc', 0) for inv in st.session_state.invoices)
        st.metric("Chiffre d'Affaires", f"{total_ventes:,.0f} DT", "+12%")

    with col2:
        total_clients = len(st.session_state.clients)
        st.metric("Clients Actifs", total_clients, "+3")

    with col3:
        factures_impayees = sum(1 for inv in st.session_state.invoices if inv.get('status') == 'impayée')
        st.metric("Factures Impayées", factures_impayees, "-2")

    with col4:
        total_achats = sum(pur.get('montant_ttc', 0) for pur in st.session_state.purchases)
        st.metric("Dépenses Total", f"{total_achats:,.0f} DT", "-5%")

    # Profil entreprise
    st.divider()
    st.subheader("📋 Profil Entreprise")

    col_left, col_right = st.columns(2)

    with col_left:
        st.info(f"**Entreprise:** {st.session_state.profile['name']}")
        st.info(f"**Matricule Fiscal:** {st.session_state.profile['matricule_fiscal']}")
        st.info(f"**Adresse:** {st.session_state.profile['address']}")

    with col_right:
        st.info(f"**RIB:** {st.session_state.profile['rib']}")
        st.info(f"**Téléphone:** {st.session_state.profile['phone']}")
        st.info(f"**Email:** {st.session_state.profile['email']}")

        if st.session_state.user_role == "admin":
            with st.expander("✏️ Modifier le profil"):
                edit_profile()

    # Dernières factures
    st.divider()
    st.subheader("🧾 Dernières Factures")

    if st.session_state.invoices:
        recent_invoices = st.session_state.invoices[-5:] if len(
            st.session_state.invoices) > 5 else st.session_state.invoices
        for inv in reversed(recent_invoices):
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                with col1:
                    st.write(f"**{inv.get('numero', 'N/A')}** - {inv.get('client', 'Client')}")
                with col2:
                    st.write(f"{inv.get('total_ttc', 0):,.0f} DT")
                with col3:
                    status = inv.get('status', 'brouillon')
                    status_icons = {'payée': '✅', 'impayée': '🔴', 'brouillon': '⚪'}
                    st.write(f"{status_icons.get(status, '⚪')} {status}")
                with col4:
                    if st.button("📋", key=f"view_{inv.get('id')}"):
                        st.session_state.selected_invoice = inv
                        st.session_state.current_view = "invoice_detail"
    else:
        st.info("Aucune facture créée")


def edit_profile():
    """Édition du profil entreprise"""
    with st.form("edit_profile_form"):
        new_name = st.text_input("Nom", value=st.session_state.profile['name'])
        new_matricule = st.text_input("Matricule Fiscal", value=st.session_state.profile['matricule_fiscal'])
        new_address = st.text_input("Adresse", value=st.session_state.profile['address'])
        new_rib = st.text_input("RIB", value=st.session_state.profile['rib'])
        new_phone = st.text_input("Téléphone", value=st.session_state.profile['phone'])
        new_email = st.text_input("Email", value=st.session_state.profile['email'])

        if st.form_submit_button("💾 Enregistrer"):
            st.session_state.profile.update({
                'name': new_name,
                'matricule_fiscal': new_matricule,
                'address': new_address,
                'rib': new_rib,
                'phone': new_phone,
                'email': new_email
            })
            save_data()
            st.success("Profil mis à jour!")
            st.rerun()


def show_invoices():
    """Gestion des factures de vente"""
    st.title("🧾 Factures de Vente")

    tab1, tab2, tab3 = st.tabs(["📋 Toutes les Factures", "➕ Nouvelle Facture", "📊 Statistiques"])

    with tab1:
        # Liste des factures
        if st.session_state.invoices:
            df = pd.DataFrame(st.session_state.invoices)
            st.dataframe(df[['numero', 'client', 'date', 'total_ttc', 'status']], use_container_width=True)

            # Téléchargement
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Exporter en CSV",
                data=csv,
                file_name="factures.csv",
                mime="text/csv"
            )
        else:
            st.info("Aucune facture disponible")

    with tab2:
        # Formulaire nouvelle facture
        with st.form("new_invoice_form"):
            st.subheader("Nouvelle Facture de Vente")

            col1, col2 = st.columns(2)
            with col1:
                client_name = st.text_input("Nom du Client*", placeholder="Société X")
                client_matricule = st.text_input("Matricule Fiscal Client", placeholder="123456/A/M/000")
                client_address = st.text_area("Adresse du Client")
            with col2:
                invoice_date = st.date_input("Date de facturation", datetime.now())
                due_date = st.date_input("Date d'échéance", datetime.now() + timedelta(days=30))
                payment_method = st.selectbox("Mode de paiement", ["Virement", "Chèque", "Espèces"])

            st.divider()
            st.subheader("🛍️ Articles")

            # Articles
            if 'invoice_items' not in st.session_state:
                st.session_state.invoice_items = []

            # Ajouter un article
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
                with col1:
                    item_desc = st.text_input("Description", key="item_desc_new", placeholder="Transport marchandises")
                with col2:
                    item_qty = st.number_input("Qté", min_value=1, value=1, key="item_qty_new")
                with col3:
                    item_price = st.number_input("Prix unitaire (DT)", min_value=0.0, value=100.0, key="item_price_new")
                with col4:
                    item_tva = st.number_input("TVA %", min_value=0.0, value=19.0, key="item_tva_new")
                with col5:
                    st.write("")  # Espace
                    st.write("")  # Espace
                    add_item = st.button("➕ Ajouter", key="add_item_btn")

            if add_item and item_desc:
                total_ht = item_qty * item_price
                tva_amount = calculate_tva(total_ht, item_tva)
                total_ttc = total_ht + tva_amount

                st.session_state.invoice_items.append({
                    'description': item_desc,
                    'quantity': item_qty,
                    'unit_price': item_price,
                    'tva_rate': item_tva,
                    'total_ht': total_ht,
                    'tva_amount': tva_amount,
                    'total_ttc': total_ttc
                })
                st.success(f"Article ajouté: {item_desc}")
                st.rerun()

            # Afficher les articles ajoutés
            if st.session_state.invoice_items:
                st.subheader("Articles ajoutés")
                items_df = pd.DataFrame(st.session_state.invoice_items)
                st.dataframe(items_df, use_container_width=True)

                # Totaux
                total_ht = sum(item['total_ht'] for item in st.session_state.invoice_items)
                total_tva = sum(item['tva_amount'] for item in st.session_state.invoice_items)
                total_ttc = sum(item['total_ttc'] for item in st.session_state.invoice_items)

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total HT", f"{total_ht:,.2f} DT")
                with col2:
                    st.metric("Total TVA", f"{total_tva:,.2f} DT")
                with col3:
                    st.metric("Total TTC", f"{total_ttc:,.2f} DT")

            # Notes et validation
            st.divider()
            notes = st.text_area("Notes additionnelles")

            if st.form_submit_button("✅ Créer la facture", use_container_width=True):
                if not client_name:
                    st.error("Veuillez saisir le nom du client")
                elif not st.session_state.invoice_items:
                    st.error("Veuillez ajouter au moins un article")
                else:
                    # Créer la facture
                    invoice_number = f"FACT-{datetime.now().strftime('%Y%m')}-{len(st.session_state.invoices) + 1:03d}"

                    new_invoice = {
                        'id': generate_id('INV'),
                        'numero': invoice_number,
                        'client': client_name,
                        'client_matricule': client_matricule,
                        'client_address': client_address,
                        'date': invoice_date.strftime('%d/%m/%Y'),
                        'due_date': due_date.strftime('%d/%m/%Y'),
                        'payment_method': payment_method,
                        'items': st.session_state.invoice_items.copy(),
                        'total_ht': total_ht,
                        'tva_amount': total_tva,
                        'total_ttc': total_ttc,
                        'status': 'brouillon',
                        'notes': notes,
                        'created_at': datetime.now().strftime('%d/%m/%Y %H:%M')
                    }

                    st.session_state.invoices.append(new_invoice)
                    st.session_state.invoice_items = []  # Réinitialiser
                    save_data()

                    st.success(f"Facture {invoice_number} créée avec succès!")
                    st.balloons()

    with tab3:
        # Statistiques
        if st.session_state.invoices:
            total_factures = len(st.session_state.invoices)
            total_ca = sum(inv.get('total_ttc', 0) for inv in st.session_state.invoices)
            moy_facture = total_ca / total_factures if total_factures > 0 else 0

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Nombre de factures", total_factures)
            with col2:
                st.metric("Chiffre d'affaires total", f"{total_ca:,.0f} DT")
            with col3:
                st.metric("Moyenne par facture", f"{moy_facture:,.0f} DT")
        else:
            st.info("Aucune statistique disponible")


def show_purchases():
    """Gestion des achats et dépenses"""
    st.title("🛒 Achats & Dépenses")

    tab1, tab2 = st.tabs(["📋 Liste des Achats", "➕ Nouvel Achat"])

    with tab1:
        if st.session_state.purchases:
            df = pd.DataFrame(st.session_state.purchases)
            st.dataframe(df[['fournisseur', 'date', 'montant_ttc', 'categorie', 'status']], use_container_width=True)
        else:
            st.info("Aucun achat enregistré")

    with tab2:
        with st.form("new_purchase_form"):
            st.subheader("Nouvel Achat / Dépense")

            col1, col2 = st.columns(2)
            with col1:
                fournisseur = st.text_input("Fournisseur*", placeholder="Société Y")
                num_facture = st.text_input("N° Facture Fournisseur")
                date_achat = st.date_input("Date", datetime.now())
            with col2:
                categorie = st.selectbox("Catégorie", [
                    "Carburant", "Maintenance", "Péages",
                    "Salaires", "Loyer", "Fournitures", "Autre"
                ])
                montant_ht = st.number_input("Montant HT (DT)*", min_value=0.0, value=1000.0)
                tva_rate = st.number_input("TVA %", min_value=0.0, value=19.0)

            description = st.text_area("Description", placeholder="Détails de l'achat...")

            if st.form_submit_button("✅ Enregistrer l'achat"):
                if not fournisseur:
                    st.error("Veuillez saisir le fournisseur")
                else:
                    tva_montant = calculate_tva(montant_ht, tva_rate)
                    montant_ttc = montant_ht + tva_montant

                    new_purchase = {
                        'id': generate_id('PUR'),
                        'fournisseur': fournisseur,
                        'num_facture': num_facture,
                        'date': date_achat.strftime('%d/%m/%Y'),
                        'categorie': categorie,
                        'montant_ht': montant_ht,
                        'tva_rate': tva_rate,
                        'tva_montant': tva_montant,
                        'montant_ttc': montant_ttc,
                        'description': description,
                        'status': 'non payé'
                    }

                    st.session_state.purchases.append(new_purchase)
                    save_data()
                    st.success(f"Achat enregistré: {fournisseur} - {montant_ttc:,.2f} DT")


def show_clients():
    """Gestion des clients"""
    st.title("👥 Gestion des Clients")

    tab1, tab2 = st.tabs(["📋 Liste des Clients", "➕ Nouveau Client"])

    with tab1:
        if st.session_state.clients:
            df = pd.DataFrame(st.session_state.clients)
            st.dataframe(df[['nom', 'matricule_fiscal', 'telephone', 'email', 'ville']], use_container_width=True)
        else:
            st.info("Aucun client enregistré")

    with tab2:
        with st.form("new_client_form"):
            st.subheader("Nouveau Client")

            col1, col2 = st.columns(2)
            with col1:
                nom = st.text_input("Nom/Raison Sociale*", placeholder="Entreprise Client")
                matricule = st.text_input("Matricule Fiscal", placeholder="123456/A/M/000")
                activite = st.text_input("Activité", placeholder="Commerce, Industrie, etc.")
            with col2:
                telephone = st.text_input("Téléphone", placeholder="+216 XX XXX XXX")
                email = st.text_input("Email", placeholder="contact@client.tn")
                ville = st.text_input("Ville", placeholder="Tunis")

            adresse = st.text_area("Adresse complète")
            notes = st.text_area("Notes", placeholder="Informations supplémentaires...")

            if st.form_submit_button("✅ Enregistrer le client"):
                if not nom:
                    st.error("Veuillez saisir le nom du client")
                else:
                    new_client = {
                        'id': generate_id('CLI'),
                        'nom': nom,
                        'matricule_fiscal': matricule,
                        'activite': activite,
                        'telephone': telephone,
                        'email': email,
                        'ville': ville,
                        'adresse': adresse,
                        'notes': notes,
                        'date_creation': datetime.now().strftime('%d/%m/%Y')
                    }

                    st.session_state.clients.append(new_client)
                    save_data()
                    st.success(f"Client {nom} ajouté avec succès!")


def show_analytics():
    """Analyses et statistiques"""
    st.title("📊 Analytics")

    if st.session_state.invoices:
        # Graphique des ventes par mois
        df = pd.DataFrame(st.session_state.invoices)

        # Convertir les dates
        try:
            df['date_dt'] = pd.to_datetime(df['date'], format='%d/%m/%Y')
            df['month'] = df['date_dt'].dt.to_period('M')

            monthly_sales = df.groupby('month')['total_ttc'].sum().reset_index()
            monthly_sales['month'] = monthly_sales['month'].dt.to_timestamp()

            st.subheader("Évolution des ventes")
            st.line_chart(monthly_sales.set_index('month')['total_ttc'])

            # Top clients
            st.subheader("Top 5 Clients")
            client_sales = df.groupby('client')['total_ttc'].sum().nlargest(5)
            st.bar_chart(client_sales)

        except:
            st.info("Données insuffisantes pour les analyses")
    else:
        st.info("Aucune donnée disponible pour les analyses")


def show_tax_assistant():
    """Assistant fiscal"""
    st.title("🤖 Assistant Fiscal")

    st.info("Cette fonctionnalité nécessite une clé API OpenAI")

    question = st.text_area("Posez votre question fiscale...",
                            placeholder="Ex: Comment déclarer la TVA en Tunisie?")

    if st.button("Analyser"):
        st.warning("Fonctionnalité IA à implémenter")
        st.write("""
        **Pour utiliser l'assistant fiscal :**
        1. Obtenez une clé API sur platform.openai.com
        2. Ajoutez-la dans les paramètres
        3. Posez vos questions fiscales
        """)


def show_reminders():
    """Rappels et échéances"""
    st.title("⏰ Rappels et Échéances")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📅 Échéances à venir")

        # Vérifier les factures impayées
        today = datetime.now()
        for invoice in st.session_state.invoices:
            if invoice.get('status') == 'impayée':
                try:
                    due_date = datetime.strptime(invoice['due_date'], '%d/%m/%Y')
                    if due_date < today:
                        st.error(f"⚠️ Facture {invoice['numero']} en retard!")
                    elif (due_date - today).days <= 7:
                        st.warning(f"⏳ Facture {invoice['numero']} due dans {(due_date - today).days} jours")
                except:
                    pass

    with col2:
        st.subheader("➕ Nouveau rappel")
        with st.form("new_reminder"):
            titre = st.text_input("Titre")
            date_rappel = st.date_input("Date du rappel", datetime.now() + timedelta(days=7))
            description = st.text_area("Description")

            if st.form_submit_button("Ajouter le rappel"):
                st.success("Rappel ajouté")


def show_declaration():
    """Déclaration fiscale"""
    st.title("📋 Déclaration Fiscale")

    # Calculs TVA
    total_tva_collected = sum(inv.get('tva_amount', 0) for inv in st.session_state.invoices)
    total_tva_deductible = sum(pur.get('tva_montant', 0) for pur in st.session_state.purchases)
    tva_a_payer = max(0, total_tva_collected - total_tva_deductible)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🧾 TVA Collectée (Ventes)")
        st.metric("Total TVA Facturée", f"{total_tva_collected:,.2f} DT")

        st.subheader("🛒 TVA Déductible (Achats)")
        st.metric("Total TVA Achats", f"{total_tva_deductible:,.2f} DT")

    with col2:
        st.subheader("💰 Résultat TVA")
        st.metric("TVA à Payer", f"{tva_a_payer:,.2f} DT",
                  delta=f"{(total_tva_collected - total_tva_deductible):,.2f} DT")

        if tva_a_payer > 0:
            st.info(f"⚠️ TVA à déclarer et payer: {tva_a_payer:,.2f} DT")
        else:
            st.success("✅ Crédit de TVA")

    # Bouton générer déclaration
    if st.button("📄 Générer Déclaration PDF", use_container_width=True):
        st.info("Fonctionnalité PDF à implémenter")
        st.write("""
        **Déclaration générée:**
        - Période: Mois courant
        - TVA Collectée: {total_tva_collected:,.2f} DT
        - TVA Déductible: {total_tva_deductible:,.2f} DT
        - TVA Nette: {tva_a_payer:,.2f} DT
        """.format(
            total_tva_collected=total_tva_collected,
            total_tva_deductible=total_tva_deductible,
            tva_a_payer=tva_a_payer
        ))


def show_users():
    """Gestion des utilisateurs (admin seulement)"""
    st.title("👑 Gestion des Utilisateurs")

    users = [
        {"username": "admin", "role": "admin", "full_name": "Administrateur Principal"},
        {"username": "staff", "role": "staff", "full_name": "Employé Standard"}
    ]

    st.dataframe(pd.DataFrame(users), use_container_width=True)

    st.subheader("Ajouter un utilisateur")
    with st.form("add_user_form"):
        new_username = st.text_input("Nom d'utilisateur")
        new_password = st.text_input("Mot de passe", type="password")
        new_role = st.selectbox("Rôle", ["admin", "staff"])
        new_fullname = st.text_input("Nom complet")

        if st.form_submit_button("Ajouter l'utilisateur"):
            st.success(f"Utilisateur {new_username} ajouté")


# ================= ROUTEUR PRINCIPAL =================
def render_view():
    """Affiche la vue actuelle"""
    view = st.session_state.current_view

    if view == "dashboard":
        show_dashboard()
    elif view == "invoices":
        show_invoices()
    elif view == "purchases":
        show_purchases()
    elif view == "clients":
        show_clients()
    elif view == "analytics":
        show_analytics()
    elif view == "tax-ai":
        show_tax_assistant()
    elif view == "reminders":
        show_reminders()
    elif view == "declaration":
        show_declaration()
    elif view == "users":
        show_users()
    else:
        show_dashboard()


# ================= APPLICATION PRINCIPALE =================
def main():
    """Point d'entrée principal"""

    # Charger les données au démarrage
    if st.session_state.authenticated:
        load_data()

    if not st.session_state.authenticated:
        login_page()
    else:
        sidebar()
        render_view()


if __name__ == "__main__":
    main()