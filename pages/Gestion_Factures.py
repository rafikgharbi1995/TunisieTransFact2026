import streamlit as st
import pandas as pd
from datetime import datetime
import uuid
from data.database import db
from data.models import Invoice, InvoiceStatus
from components.invoice_form import render_invoice_form


def show():
    st.title("🧾 Gestion des Factures")

    # Tabs pour différentes vues
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Toutes les Factures",
        "➕ Nouvelle Facture",
        "📊 Statistiques",
        "🔍 Recherche"
    ])

    with tab1:
        show_all_invoices()

    with tab2:
        create_invoice()

    with tab3:
        show_invoice_stats()

    with tab4:
        search_invoices()


def show_all_invoices():
    """Affiche toutes les factures"""
    invoices = db.get_invoices()

    if not invoices:
        st.info("Aucune facture trouvée.")
        return

    # Filtres
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.multiselect(
            "Filtrer par statut",
            options=["tous"] + [status.value for status in InvoiceStatus],
            default=["tous"]
        )
    with col2:
        month_filter = st.selectbox(
            "Filtrer par mois",
            options=["tous"] + list(range(1, 13))
        )
    with col3:
        search_term = st.text_input("Rechercher par ID ou client")

    # Appliquer les filtres
    filtered_invoices = invoices
    if "tous" not in status_filter:
        filtered_invoices = [inv for inv in filtered_invoices if inv.status in status_filter]

    if search_term:
        filtered_invoices = [
            inv for inv in filtered_invoices
            if search_term.lower() in inv.id.lower() or search_term.lower() in inv.client_id.lower()
        ]

    # Afficher le tableau
    df = pd.DataFrame([{
        "ID": inv.id,
        "Client": inv.client_id,
        "Date": inv.date.strftime("%d/%m/%Y"),
        "Échéance": inv.due_date.strftime("%d/%m/%Y"),
        "Montant HT": f"{inv.total_amount - inv.tva_amount:,.2f} DT",
        "TVA": f"{inv.tva_amount:,.2f} DT",
        "Total TTC": f"{inv.total_amount:,.2f} DT",
        "Statut": inv.status,
        "Action": "📝"
    } for inv in filtered_invoices])

    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Téléchargement Excel
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Exporter en CSV",
            data=csv,
            file_name=f"factures_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.warning("Aucune facture ne correspond aux filtres.")


def create_invoice():
    """Créer une nouvelle facture"""
    st.subheader("Créer une nouvelle facture")

    # Formulaire de facture
    invoice_data = render_invoice_form()

    if invoice_data and st.button("✅ Créer la facture", use_container_width=True):
        # Générer un ID unique
        invoice_id = f"FACT-{datetime.now().strftime('%Y%m')}-{str(uuid.uuid4())[:8].upper()}"

        # Créer l'objet Invoice
        new_invoice = Invoice(
            id=invoice_id,
            client_id=invoice_data['client_id'],
            date=datetime.now(),
            due_date=invoice_data['due_date'],
            total_amount=invoice_data['total_ttc'],
            tva_amount=invoice_data['tva_amount'],
            status=InvoiceStatus.DRAFT,
            items=invoice_data['items']
        )

        # Sauvegarder
        db.add_invoice(new_invoice)
        st.success(f"Facture {invoice_id} créée avec succès!")

        # Options post-création
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📄 Générer PDF", use_container_width=True):
                # TODO: Implémenter la génération PDF
                st.info("Fonction PDF à implémenter")
        with col2:
            if st.button("📧 Envoyer au client", use_container_width=True):
                st.info("Fonction envoi email à implémenter")
        with col3:
            if st.button("➕ Nouvelle facture", use_container_width=True):
                st.rerun()


def show_invoice_stats():
    """Affiche les statistiques des factures"""
    invoices = db.get_invoices()

    if not invoices:
        st.info("Aucune donnée disponible.")
        return

    # Calculs statistiques
    total_amount = sum(inv.total_amount for inv in invoices)
    average_invoice = total_amount / len(invoices) if invoices else 0
    paid_invoices = sum(1 for inv in invoices if inv.status == "payée")
    overdue_invoices = sum(1 for inv in invoices if inv.status == "en retard")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Facturé", f"{total_amount:,.0f} DT")
    with col2:
        st.metric("Moyenne par facture", f"{average_invoice:,.0f} DT")
    with col3:
        st.metric("Factures payées", paid_invoices)
    with col4:
        st.metric("Factures en retard", overdue_invoices)

    # Graphique par statut
    status_counts = pd.Series([inv.status for inv in invoices]).value_counts()
    fig = px.pie(values=status_counts.values, names=status_counts.index,
                 title="Répartition par statut")
    st.plotly_chart(fig, use_container_width=True)


def search_invoices():
    """Recherche avancée de factures"""
    st.subheader("🔍 Recherche Avancée")

    with st.form("search_form"):
        col1, col2 = st.columns(2)
        with col1:
            client_id = st.text_input("ID Client")
            min_amount = st.number_input("Montant minimum (DT)", min_value=0.0)
        with col2:
            start_date = st.date_input("Date de début")
            end_date = st.date_input("Date de fin")

        if st.form_submit_button("🔍 Rechercher", use_container_width=True):
            # TODO: Implémenter la recherche avancée
            st.info("Fonction de recherche avancée à implémenter")