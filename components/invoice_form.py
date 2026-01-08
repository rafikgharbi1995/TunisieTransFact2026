import streamlit as st
from datetime import datetime, timedelta
import pandas as pd


def render_invoice_form():
    """Rendu du formulaire de création de facture"""

    # Section client
    st.subheader("👥 Informations Client")
    col1, col2 = st.columns(2)
    with col1:
        client_id = st.text_input("Matricule Fiscal Client*")
        client_name = st.text_input("Nom du Client*")
    with col2:
        client_address = st.text_area("Adresse")
        client_phone = st.text_input("Téléphone")

    # Section dates
    st.subheader("📅 Dates")
    col1, col2 = st.columns(2)
    with col1:
        invoice_date = st.date_input("Date de facturation", datetime.now())
    with col2:
        due_date = st.date_input(
            "Date d'échéance",
            datetime.now() + timedelta(days=30)
        )

    # Section articles
    st.subheader("🛍️ Articles")

    # Tableau d'articles
    if 'invoice_items' not in st.session_state:
        st.session_state.invoice_items = []

    with st.container():
        col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 2, 2, 2, 1])
        with col1:
            st.write("**Description**")
        with col2:
            st.write("**Quantité**")
        with col3:
            st.write("**Prix unitaire (DT)**")
        with col4:
            st.write("**TVA (%)**")
        with col5:
            st.write("**Total HT (DT)**")
        with col6:
            st.write("**Action**")

    # Ajouter un article
    with st.form("add_item_form"):
        col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 2, 2, 2, 1])
        with col1:
            item_desc = st.text_input("Description", key="item_desc")
        with col2:
            item_qty = st.number_input("Qté", min_value=1, value=1, key="item_qty")
        with col3:
            item_price = st.number_input("Prix", min_value=0.0, value=0.0, key="item_price")
        with col4:
            item_tva = st.number_input("TVA %", min_value=0.0, value=19.0, key="item_tva")
        with col5:
            item_total_ht = item_qty * item_price
            st.write(f"**{item_total_ht:,.2f} DT**")
        with col6:
            add_item = st.form_submit_button("➕", use_container_width=True)

        if add_item and item_desc:
            st.session_state.invoice_items.append({
                'description': item_desc,
                'quantity': item_qty,
                'unit_price': item_price,
                'tva_rate': item_tva,
                'total_ht': item_total_ht,
                'tva_amount': item_total_ht * (item_tva / 100),
                'total_ttc': item_total_ht * (1 + item_tva / 100)
            })
            st.rerun()

    # Afficher les articles ajoutés
    if st.session_state.invoice_items:
        df_items = pd.DataFrame(st.session_state.invoice_items)
        st.dataframe(df_items, use_container_width=True, hide_index=True)

        # Calculs totaux
        total_ht = df_items['total_ht'].sum()
        total_tva = df_items['tva_amount'].sum()
        total_ttc = df_items['total_ttc'].sum()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total HT", f"{total_ht:,.2f} DT")
        with col2:
            st.metric("Total TVA", f"{total_tva:,.2f} DT")
        with col3:
            st.metric("Total TTC", f"{total_ttc:,.2f} DT")

        # Notes
        st.subheader("📝 Notes")
        notes = st.text_area("Notes additionnelles")

        # Validation
        if not client_id or not client_name:
            st.error("Veuillez remplir les champs obligatoires (*)")
            return None

        if len(st.session_state.invoice_items) == 0:
            st.error("Veuillez ajouter au moins un article")
            return None

        return {
            'client_id': client_id,
            'client_name': client_name,
            'client_address': client_address,
            'client_phone': client_phone,
            'invoice_date': invoice_date,
            'due_date': due_date,
            'items': st.session_state.invoice_items,
            'total_ht': total_ht,
            'tva_amount': total_tva,
            'total_ttc': total_ttc,
            'notes': notes
        }

    return None