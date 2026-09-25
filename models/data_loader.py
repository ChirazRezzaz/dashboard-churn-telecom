"""Chargement des données (Model, au sens MVC).

Seules les fonctions de ce module touchent au disque. Elles sont mises en
cache avec `@st.cache_data` pour éviter de relire/retraiter le CSV à chaque
interaction utilisateur (filtre, navigation entre pages...).
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from models.transforms import prepare_dataset

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "telco_churn.csv"


@st.cache_data(show_spinner="Chargement des données...")
def load_raw_data() -> pd.DataFrame:
    """Charge le CSV brut IBM Telco Customer Churn."""
    return pd.read_csv(DATA_PATH)


@st.cache_data(show_spinner="Préparation des données...")
def load_processed_data() -> pd.DataFrame:
    """Charge et nettoie/enrichit le dataset (cible encodée, features créées)."""
    raw = load_raw_data()
    return prepare_dataset(raw)


@st.cache_data
def get_filter_options(df: pd.DataFrame) -> dict:
    """Valeurs uniques utilisées pour peupler les filtres de la sidebar."""
    return {
        "contracts": sorted(df["Contract"].unique().tolist()),
        "internet_services": sorted(df["InternetService"].unique().tolist()),
        "payment_methods": sorted(df["PaymentMethod"].unique().tolist()),
        "tenure_min": int(df["tenure"].min()),
        "tenure_max": int(df["tenure"].max()),
    }
