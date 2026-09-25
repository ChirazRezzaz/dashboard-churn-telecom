"""Formulaire et affichage de la page Prédiction (View, au sens MVC).

Le formulaire ne demande que des caractéristiques "naturelles" (celles
qu'un conseiller client connaît réellement) : les variables engineerées
(tenure_group, num_services, senior_isole, charge_par_service) sont
recalculées côté Model (models/predictor.py), jamais saisies ici.
"""
from __future__ import annotations

import streamlit as st

from views import components

YES_NO = ["Yes", "No"]
GENDERS = ["Female", "Male"]
INTERNET_SERVICES = ["DSL", "Fiber optic", "No"]
CONTRACTS = ["Month-to-month", "One year", "Two year"]
PAYMENT_METHODS = [
    "Electronic check", "Mailed check",
    "Bank transfer (automatic)", "Credit card (automatic)",
]


def render_form() -> tuple[dict | None, bool]:
    """Affiche le formulaire de saisie. Renvoie (saisie_brute, submitted)."""
    st.subheader("Profil client")

    # En dehors du st.form : ces deux champs conditionnent l'affichage
    # d'autres champs (rerun immédiat nécessaire, impossible dans un form).
    col_a, col_b = st.columns(2)
    with col_a:
        phone_service = st.selectbox("Service téléphonique", YES_NO, index=0, key="phone_service")
    with col_b:
        internet_service = st.selectbox("Service internet", INTERNET_SERVICES, index=0, key="internet_service")

    with st.form("formulaire_prediction"):
        col1, col2, col3 = st.columns(3)
        with col1:
            gender = st.selectbox("Genre", GENDERS)
            senior_citizen = st.checkbox("Client senior (65 ans ou +)")
            partner = st.selectbox("A un(e) partenaire", YES_NO, index=1)
            dependents = st.selectbox("A des personnes à charge", YES_NO, index=1)
        with col2:
            tenure = st.slider("Ancienneté (mois)", 0, 72, 12)
            contract = st.selectbox("Type de contrat", CONTRACTS)
            paperless_billing = st.selectbox("Facturation dématérialisée", YES_NO, index=0)
            payment_method = st.selectbox("Méthode de paiement", PAYMENT_METHODS)
        with col3:
            monthly_charges = st.slider("Charge mensuelle ($)", 18.0, 120.0, 70.0, step=0.5)
            total_charges_defaut = round(tenure * monthly_charges, 2)
            total_charges = st.number_input(
                "Charges totales facturées à date ($)",
                min_value=0.0, value=total_charges_defaut, step=10.0,
                help="Pré-rempli à partir de l'ancienneté × la charge mensuelle — ajustable.",
            )

        st.divider()
        st.subheader("Services souscrits")

        if phone_service == "No":
            multiple_lines = "No phone service"
            st.caption("Lignes multiples : non applicable (pas de service téléphonique).")
        else:
            multiple_lines = st.selectbox("Lignes téléphoniques multiples", YES_NO, index=1)

        if internet_service == "No":
            online_security = online_backup = device_protection = "No internet service"
            tech_support = streaming_tv = streaming_movies = "No internet service"
            st.caption("Services liés à internet : non applicables (pas d'accès internet).")
        else:
            s1, s2, s3 = st.columns(3)
            with s1:
                online_security = st.selectbox("Sécurité en ligne", YES_NO, index=1)
                online_backup = st.selectbox("Sauvegarde en ligne", YES_NO, index=1)
            with s2:
                device_protection = st.selectbox("Protection des appareils", YES_NO, index=1)
                tech_support = st.selectbox("Support technique", YES_NO, index=1)
            with s3:
                streaming_tv = st.selectbox("Streaming TV", YES_NO, index=1)
                streaming_movies = st.selectbox("Streaming films", YES_NO, index=1)

        submitted = st.form_submit_button("Prédire le risque de churn", width="stretch")

    if not submitted:
        return None, False

    saisie = {
        "gender": gender,
        "SeniorCitizen": int(senior_citizen),
        "Partner": partner,
        "Dependents": dependents,
        "tenure": tenure,
        "PhoneService": phone_service,
        "MultipleLines": multiple_lines,
        "InternetService": internet_service,
        "OnlineSecurity": online_security,
        "OnlineBackup": online_backup,
        "DeviceProtection": device_protection,
        "TechSupport": tech_support,
        "StreamingTV": streaming_tv,
        "StreamingMovies": streaming_movies,
        "Contract": contract,
        "PaperlessBilling": paperless_billing,
        "PaymentMethod": payment_method,
        "MonthlyCharges": monthly_charges,
        "TotalCharges": total_charges,
    }
    return saisie, True


def render_resultat(proba: float, label: str, alertes: list[str]) -> None:
    st.divider()
    st.subheader("Résultat de la prédiction")
    components.resultat_prediction(proba, label, alertes)


def render_page_header() -> None:
    components.page_header(
        "Prédiction — Risque de churn",
        "Simulez la probabilité de résiliation d'un client à partir de son profil.",
    )
