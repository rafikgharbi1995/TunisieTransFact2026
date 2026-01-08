import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from data.database import db
from data.models import BusinessProfile
import plotly.express as px


def show():
    st.title("🏠 Tableau de Bord TunisieTrans SARL")

    # Charger les données
    profile = db.get_profile()
    invoices = db.get_invoices()
    clients = db.get_clients()

    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_revenue = sum(inv.total_amount for inv in invoices)
        st.metric("Chiffre d'Affaires Total", f"{total_revenue:,.0f} DT", delta="12%")

    with col2:
        active_clients = len(clients)
        st.metric("Clients Actifs", active_clients, delta="+3")

    with col3:
        pending_invoices = sum(1 for inv in invoices if inv.status == "envoyée")
        st.metric("Factures en Attente", pending_invoices, delta="-2")

    with col4:
        current_month = datetime.now().month
        month_revenue = sum(
            inv.total_amount for inv in invoices
            if inv.date.month == current_month
        )
        st.metric("CA du Mois", f"{month_revenue:,.0f} DT")

    st.divider()

    # Profil entreprise et graphiques
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📋 Profil Entreprise")

        if profile:
            st.info(f"**Entreprise:** {profile.name}")
            st.info(f"**Matricule Fiscal:** {profile.matricule_fiscal}")
            st.info(f"**Adresse:** {profile.address}")
            st.info(f"**RIB:** {profile.rib}")
            st.info(f"**Secteur:** {profile.industry}")

            # Édition pour admin
            if st.session_state.user_role == "admin":
                with st.expander("✏️ Modifier le profil"):
                    edit_profile(profile)

    with col_right:
        st.subheader("📈 Évolution du CA")

        # Préparer les données pour le graphique
        if invoices:
            df_invoices = pd.DataFrame([{
                'date': inv.date,
                'montant': inv.total_amount
            } for inv in invoices])

            df_invoices['month'] = df_invoices['date'].dt.to_period('M')
            monthly_data = df_invoices.groupby('month')['montant'].sum().reset_index()
            monthly_data['month'] = monthly_data['month'].dt.to_timestamp()

            fig = px.line(monthly_data, x='month', y='montant',
                          title="Chiffre d'Affaires Mensuel",
                          markers=True)
            fig.update_layout(xaxis_title="Mois", yaxis_title="Montant (DT)")
            st.plotly_chart(fig, use_container_width=True)

    # Dernières factures
    st.subheader("🧾 Dernières Factures")
    if invoices:
        recent_invoices = sorted(invoices, key=lambda x: x.date, reverse=True)[:5]
        for inv in recent_invoices:
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"**{inv.id}** - Client: {inv.client_id}")
            with col2:
                st.write(f"{inv.total_amount:,.0f} DT")
            with col3:
                status_color = {
                    "payée": "✅",
                    "envoyée": "🟡",
                    "en retard": "🔴",
                    "brouillon": "⚪"
                }
                st.write(f"{status_color.get(inv.status, '⚪')} {inv.status}")
            st.divider()


def edit_profile(profile: BusinessProfile):
    """Formulaire d'édition du profil"""
    with st.form("edit_profile_form"):
        new_name = st.text_input("Nom de l'entreprise", value=profile.name)
        new_matricule = st.text_input("Matricule Fiscal", value=profile.matricule_fiscal)
        new_address = st.text_input("Adresse", value=profile.address)
        new_rib = st.text_input("RIB", value=profile.rib)
        new_phone = st.text_input("Téléphone", value=profile.phone or "")
        new_email = st.text_input("Email", value=profile.email or "")
        new_capital = st.number_input("Capital Social (DT)",
                                      value=float(profile.capital_social),
                                      min_value=0.0)

        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("💾 Enregistrer", use_container_width=True):
                updated_profile = BusinessProfile(
                    name=new_name,
                    matricule_fiscal=new_matricule,
                    address=new_address,
                    rib=new_rib,
                    industry=profile.industry,
                    target_audience=profile.target_audience,
                    phone=new_phone,
                    email=new_email,
                    capital_social=new_capital
                )
                db.save_profile(updated_profile)
                st.success("Profil mis à jour avec succès!")
                st.rerun()

        with col2:
            if st.form_submit_button("❌ Annuler", use_container_width=True):
                st.rerun()