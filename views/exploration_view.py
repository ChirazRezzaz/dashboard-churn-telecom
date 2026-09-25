"""Mise en page de la page Exploration (View, au sens MVC).

Reçoit des données déjà filtrées/agrégées par le Controller et le Model ;
n'effectue aucune lecture de fichier ni transformation de données.
"""
from __future__ import annotations

import streamlit as st

from views import components


def render_sidebar_filters(options: dict) -> dict:
    """Affiche les filtres de la sidebar et renvoie les valeurs sélectionnées."""
    st.sidebar.header("Filtres")

    contracts = st.sidebar.multiselect(
        "Type de contrat", options["contracts"], default=options["contracts"]
    )
    internet_services = st.sidebar.multiselect(
        "Service internet", options["internet_services"], default=options["internet_services"]
    )
    payment_methods = st.sidebar.multiselect(
        "Méthode de paiement", options["payment_methods"], default=options["payment_methods"]
    )
    tenure_range = st.sidebar.slider(
        "Ancienneté (mois)",
        min_value=options["tenure_min"], max_value=options["tenure_max"],
        value=(options["tenure_min"], options["tenure_max"]),
    )

    return {
        "contracts": contracts,
        "internet_services": internet_services,
        "payment_methods": payment_methods,
        "tenure_range": tenure_range,
    }


def render(df_filtered, kpis: dict, rate_by_contract, rate_by_internet, rate_by_payment) -> None:
    components.page_header(
        "Exploration — Churn Télécom",
        "Naviguez dans le portefeuille client et identifiez les segments à risque.",
    )

    components.kpi_row(kpis)
    st.divider()

    if df_filtered.empty:
        st.info("Aucun client ne correspond aux filtres sélectionnés.")
        return

    col1, col2 = st.columns(2)
    with col1:
        components.bar_churn_rate(
            rate_by_contract, "Contract", "Taux de churn par type de contrat"
        )
    with col2:
        components.bar_churn_rate(
            rate_by_internet, "InternetService", "Taux de churn par service internet"
        )

    col3, col4 = st.columns(2)
    with col3:
        components.histogram_by_churn(
            df_filtered, "tenure", "Distribution de l'ancienneté selon le churn"
        )
    with col4:
        components.box_by_churn(
            df_filtered, "MonthlyCharges", "Charge mensuelle selon le churn"
        )

    col5, col6 = st.columns(2)
    with col5:
        components.bar_churn_rate(
            rate_by_payment, "PaymentMethod", "Taux de churn par méthode de paiement"
        )
    with col6:
        components.scatter_charges(
            df_filtered, "Ancienneté vs charge mensuelle (par statut de churn)"
        )

    with st.expander("Voir les données filtrées"):
        st.dataframe(
            df_filtered.drop(columns=["Churn"]).assign(
                Churn=df_filtered["Churn"].map({0: "No", 1: "Yes"})
            ),
            width="stretch",
        )
