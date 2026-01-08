import streamlit as st
from data.models import UserRole


def render_sidebar(user_role: UserRole, on_logout, set_current_view):
    """Affiche la barre latérale de navigation"""
    with st.sidebar:
        # Logo et titre
        st.image("assets/logo.png", width=200) if st.get_option("theme.primaryColor") else st.title("🚚 TunisieTrans")
        st.divider()

        # Navigation
        st.subheader("📋 Menu Principal")

        menu_items = [
            ("🏠 Dashboard", "dashboard"),
            ("🧾 Factures", "invoices"),
            ("🛒 Achats", "purchases"),
            ("👥 Clients", "clients"),
            ("📊 Analytics", "analytics"),
            ("🤖 Assistant Fiscal", "tax-ai"),
            ("⏰ Rappels", "reminders"),
            ("📋 Déclaration", "declaration")
        ]

        for icon_text, view in menu_items:
            if st.button(icon_text, use_container_width=True, key=f"btn_{view}"):
                set_current_view(view)
                st.rerun()

        # Section admin seulement
        if user_role == UserRole.ADMIN:
            st.divider()
            st.subheader("⚙️ Administration")
            if st.button("👑 Gestion Utilisateurs", use_container_width=True):
                set_current_view("admin-users")
                st.rerun()
            if st.button("⚙️ Paramètres", use_container_width=True):
                set_current_view("settings")
                st.rerun()

        st.divider()

        # Informations utilisateur
        st.caption(f"👤 Connecté : {st.session_state.get('user_full_name', 'Utilisateur')}")
        st.caption(f"📋 Rôle : {user_role.value}")

        # Bouton déconnexion
        if st.button("🚪 Déconnexion", use_container_width=True, type="primary"):
            on_logout()
            st.rerun()

        # Footer
        st.divider()
        st.caption("© 2024 TunisieTrans SARL")
        st.caption("Version 1.0.0")