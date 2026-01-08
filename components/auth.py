import streamlit as st
import hashlib
from data.database import db
from data.models import User, UserRole


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def init_default_users():
    """Initialise les utilisateurs par défaut"""
    with db.get_connection() as conn:
        cursor = conn.execute('SELECT COUNT(*) FROM users')
        if cursor.fetchone()[0] == 0:
            # Admin par défaut
            conn.execute('''
                INSERT INTO users VALUES (?, ?, ?, ?, ?)
            ''', (
                'admin',
                hash_password('admin123'),
                UserRole.ADMIN.value,
                'Administrateur Principal',
                'admin@tunisietrans.tn'
            ))
            # Staff par défaut
            conn.execute('''
                INSERT INTO users VALUES (?, ?, ?, ?, ?)
            ''', (
                'staff',
                hash_password('staff123'),
                UserRole.STAFF.value,
                'Employé Standard',
                'staff@tunisietrans.tn'
            ))
            conn.commit()


def authenticate_user(username: str, password: str) -> Optional[User]:
    """Authentifie un utilisateur"""
    with db.get_connection() as conn:
        cursor = conn.execute(
            'SELECT * FROM users WHERE username = ? AND password_hash = ?',
            (username, hash_password(password))
        )
        row = cursor.fetchone()
        if row:
            return User(
                username=row[0],
                password_hash=row[1],
                role=UserRole(row[2]),
                full_name=row[3],
                email=row[4]
            )
    return None


def login_page(on_login):
    """Affiche la page de connexion"""
    st.title("🔐 Connexion - TunisieTrans SARL")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Nom d'utilisateur")
            password = st.text_input("Mot de passe", type="password")

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                login_as_admin = st.form_submit_button("👑 Admin", use_container_width=True)
            with col_btn2:
                login_as_staff = st.form_submit_button("👤 Staff", use_container_width=True)

            if login_as_admin:
                user = authenticate_user(username, password)
                if user and user.role == UserRole.ADMIN:
                    on_login(user)
                    st.success(f"Connecté en tant qu'Administrateur!")
                    st.rerun()
                else:
                    st.error("Identifiants admin incorrects!")

            if login_as_staff:
                user = authenticate_user(username, password)
                if user:
                    on_login(user)
                    st.success(f"Connecté en tant qu'{user.full_name}!")
                    st.rerun()
                else:
                    st.error("Identifiants incorrects!")

        # Informations de test
        with st.expander("📋 Comptes de test"):
            st.code("Admin: admin / admin123")
            st.code("Staff: staff / staff123")