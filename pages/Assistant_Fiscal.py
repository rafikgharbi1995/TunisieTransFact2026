import streamlit as st
import openai
from datetime import datetime
import os


def show():
    st.title("🤖 Assistant Fiscal Intelligent")

    # Configuration OpenAI
    if "openai_api_key" not in st.session_state:
        st.session_state.openai_api_key = os.getenv("OPENAI_API_KEY", "")

    # Sidebar pour la configuration
    with st.sidebar:
        st.subheader("⚙️ Configuration IA")
        api_key = st.text_input(
            "Clé API OpenAI",
            value=st.session_state.openai_api_key,
            type="password"
        )
        if api_key:
            st.session_state.openai_api_key = api_key
            openai.api_key = api_key

        st.divider()
        st.subheader("💡 Exemples de questions")

        example_questions = [
            "Comment calculer la TVA en Tunisie?",
            "Quelles sont les échéances fiscales ce mois?",
            "Comment déclarer la TVA mensuelle?",
            "Quels documents pour une déclaration annuelle?",
            "Comment optimiser mes impôts légitimement?"
        ]

        for question in example_questions:
            if st.button(question, use_container_width=True):
                st.session_state.chat_input = question

    # Interface principale
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant",
             "content": "Bonjour! Je suis votre assistant fiscal. Comment puis-je vous aider aujourd'hui?"}
        ]

    # Afficher l'historique des messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input utilisateur
    if prompt := st.chat_input("Posez votre question fiscale..."):
        # Vérifier la clé API
        if not st.session_state.openai_api_key:
            st.error("Veuillez configurer votre clé API OpenAI dans la sidebar.")
            return

        # Ajouter le message utilisateur
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Générer la réponse
        with st.chat_message("assistant"):
            with st.spinner("Analyse en cours..."):
                try:
                    response = generate_fiscal_response(prompt)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"Erreur: {str(e)}")

    # Section d'outils fiscaux
    st.divider()
    st.subheader("🧮 Outils de Calcul Fiscal")

    col1, col2 = st.columns(2)

    with col1:
        with st.expander("📊 Calculatrice TVA"):
            calculate_tva()

    with col2:
        with st.expander("📅 Calendrier Fiscal"):
            show_fiscal_calendar()


def generate_fiscal_response(prompt: str) -> str:
    """Génère une réponse avec OpenAI"""

    system_prompt = """Tu es un expert fiscal tunisien spécialisé dans la législation fiscale tunisienne.
    Fournis des réponses précises, à jour et conformes à la réglementation tunisienne.
    Inclus les références légales quand c'est pertinent.
    Sois concis mais complet.

    Informations contextuelles:
    - Entreprise: SARL de transport/logistique
    - Régime: Réel normal pour la TVA
    - Secteur: Transport et Logistique
    - Localisation: Tunisie

    Réponds en français."""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erreur lors de la génération de la réponse: {str(e)}"


def calculate_tva():
    """Calculatrice TVA"""
    col1, col2 = st.columns(2)

    with col1:
        amount = st.number_input("Montant HT (DT)", min_value=0.0, value=1000.0)
        tva_rate = st.selectbox("Taux TVA (%)", [7, 13, 19], index=2)

    with col2:
        tva_amount = amount * (tva_rate / 100)
        total_ttc = amount + tva_amount

        st.metric("Montant TVA", f"{tva_amount:,.2f} DT")
        st.metric("Total TTC", f"{total_ttc:,.2f} DT")


def show_fiscal_calendar():
    """Affiche le calendrier fiscal"""
    current_month = datetime.now().month
    current_year = datetime.now().year

    fiscal_deadlines = {
        "TVA Mensuelle": f"20/{current_month:02d}/{current_year}",
        "Déclaration Annuelle": f"25/03/{current_year + 1}",
        "Impôt sur les Sociétés": f"25/04/{current_year + 1}",
        "CNSS Patronale": f"15/{current_month:02d}/{current_year}"
    }

    for tax, deadline in fiscal_deadlines.items():
        st.info(f"**{tax}:** {deadline}")