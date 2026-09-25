"""Composants d'affichage réutilisables (View, au sens MVC).

Ce module ne contient AUCUNE transformation de données : il reçoit des
DataFrames ou des valeurs déjà prêtes à afficher, et se contente de les
mettre en forme (métriques, graphiques Plotly, mise en page).
"""
from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

PALETTE = {"No Churn": "#4C78A8", "Churn": "#E45756", 0: "#4C78A8", 1: "#E45756"}


def page_header(title: str, subtitle: str) -> None:
    st.title(title)
    st.caption(subtitle)
    st.divider()


def kpi_row(kpis: dict) -> None:
    """Affiche les 4 KPIs synthétiques en haut de la page Exploration."""
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Clients (segment filtré)", f"{kpis['n_clients']:,}".replace(",", " "))
    c2.metric("Taux de churn", f"{kpis['churn_rate']:.1f} %")
    c3.metric("Ancienneté moyenne", f"{kpis['avg_tenure']:.1f} mois")
    c4.metric("Facture mensuelle moyenne", f"{kpis['avg_monthly']:.2f} $")


def bar_churn_rate(df_rates, category_col: str, title: str):
    """Diagramme en barres du taux de churn (%) par modalité."""
    fig = px.bar(
        df_rates, x=category_col, y="churn_rate",
        text=df_rates["churn_rate"].round(1).astype(str) + " %",
        title=title, labels={"churn_rate": "Taux de churn (%)", category_col: ""},
        color="churn_rate", color_continuous_scale="Reds",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(coloraxis_showscale=False, yaxis_range=[0, max(df_rates["churn_rate"].max() * 1.2, 10)])
    st.plotly_chart(fig, width="stretch")


def histogram_by_churn(df, x: str, title: str, nbins: int = 30):
    """Histogramme d'une variable numérique, coloré par statut de churn."""
    plot_df = df.copy()
    plot_df["Statut"] = plot_df["Churn"].map({0: "No Churn", 1: "Churn"})
    fig = px.histogram(
        plot_df, x=x, color="Statut", barmode="overlay", nbins=nbins,
        title=title, color_discrete_map=PALETTE, opacity=0.65,
    )
    st.plotly_chart(fig, width="stretch")


def box_by_churn(df, y: str, title: str):
    """Boîte à moustaches d'une variable numérique par statut de churn."""
    plot_df = df.copy()
    plot_df["Statut"] = plot_df["Churn"].map({0: "No Churn", 1: "Churn"})
    fig = px.box(
        plot_df, x="Statut", y=y, color="Statut", title=title,
        color_discrete_map=PALETTE,
    )
    st.plotly_chart(fig, width="stretch")


def scatter_charges(df, title: str):
    """Nuage de points MonthlyCharges vs TotalCharges, coloré par churn."""
    plot_df = df.copy()
    plot_df["Statut"] = plot_df["Churn"].map({0: "No Churn", 1: "Churn"})
    fig = px.scatter(
        plot_df, x="tenure", y="MonthlyCharges", color="Statut",
        title=title, opacity=0.5, color_discrete_map=PALETTE,
        labels={"tenure": "Ancienneté (mois)", "MonthlyCharges": "Charge mensuelle ($)"},
    )
    st.plotly_chart(fig, width="stretch")


def gauge_churn_probability(proba: float):
    """Jauge de probabilité de churn (0-100%) avec code couleur."""
    pct = proba * 100
    color = "#2ECC71" if pct < 30 else ("#F39C12" if pct < 60 else "#E45756")
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pct,
        number={"suffix": " %"},
        title={"text": "Probabilité de résiliation"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": color},
            "steps": [
                {"range": [0, 30], "color": "#EAFAF1"},
                {"range": [30, 60], "color": "#FEF5E7"},
                {"range": [60, 100], "color": "#FDEDEC"},
            ],
        },
    ))
    fig.update_layout(height=320, margin=dict(t=60, b=10, l=30, r=30))
    st.plotly_chart(fig, width="stretch")


def resultat_prediction(proba: float, label: str, alertes: list[str]) -> None:
    """Affiche le résultat de la prédiction : jauge + message + alertes."""
    col1, col2 = st.columns([1, 1])
    with col1:
        gauge_churn_probability(proba)
    with col2:
        if label == "Churn":
            st.error(f"⚠️ Client à risque — probabilité de churn : **{proba:.1%}**")
            st.markdown(
                "**Recommandation :** contacter ce client avec une offre de "
                "fidélisation avant qu'il ne résilie."
            )
        else:
            st.success(f"✅ Client fidèle — probabilité de churn : **{proba:.1%}**")
            st.markdown("**Recommandation :** aucune action urgente nécessaire.")

    if alertes:
        with st.container():
            st.warning(
                "**Points de vigilance sur la saisie :**\n\n"
                + "\n".join(f"- {a}" for a in alertes)
            )
