"""Nettoyage, feature engineering et agrégations pour le churn télécom.

Toute la logique de transformation de données vit ici (Model, au sens MVC) :
ni les Views ni les Controllers ne doivent manipuler un DataFrame directement.
"""
from __future__ import annotations

import pandas as pd

SERVICE_COLS = [
    "OnlineSecurity", "OnlineBackup", "DeviceProtection",
    "TechSupport", "StreamingTV", "StreamingMovies",
]

TENURE_BINS = [-1, 12, 24, 60, 1000]
TENURE_LABELS = ["0-12 mois", "1-2 ans", "2-5 ans", "5+ ans"]

# Colonnes attendues par le pipeline sklearn entraîné (models/predictor.py)
FEATURE_COLUMNS = [
    "gender", "SeniorCitizen", "Partner", "Dependents", "tenure",
    "PhoneService", "MultipleLines", "InternetService", "OnlineSecurity",
    "OnlineBackup", "DeviceProtection", "TechSupport", "StreamingTV",
    "StreamingMovies", "Contract", "PaperlessBilling", "PaymentMethod",
    "MonthlyCharges", "TotalCharges",
    "tenure_group", "num_services", "senior_isole", "charge_par_service",
]


def clean_total_charges(df: pd.DataFrame) -> pd.DataFrame:
    """Convertit TotalCharges en numérique et impute les valeurs manquantes
    (clients à tenure nulle, pas encore facturés) par 0."""
    df = df.copy()
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    df["TotalCharges"] = df["TotalCharges"].fillna(0)
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Ajoute les variables créées au Projet 2 : tenure_group, num_services,
    senior_isole, charge_par_service. Reproductible ligne à ligne (utilisé
    aussi bien sur tout le dataset que sur une saisie utilisateur unique)."""
    df = df.copy()

    df["tenure_group"] = pd.cut(
        df["tenure"], bins=TENURE_BINS, labels=TENURE_LABELS
    ).astype(str)

    df["num_services"] = df[SERVICE_COLS].apply(
        lambda row: (row == "Yes").sum(), axis=1
    )

    df["senior_isole"] = (
        (df["SeniorCitizen"] == 1)
        & (df["Partner"] == "No")
        & (df["Dependents"] == "No")
    ).astype(int)

    df["charge_par_service"] = df["MonthlyCharges"] / (df["num_services"] + 1)

    return df


def prepare_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Pipeline de nettoyage complet appliqué au chargement des données brutes."""
    df = clean_total_charges(df)
    df = engineer_features(df)
    df["Churn"] = (df["Churn"] == "Yes").astype(int)
    return df


def filter_data(
    df: pd.DataFrame,
    contracts: list[str] | None = None,
    internet_services: list[str] | None = None,
    payment_methods: list[str] | None = None,
    tenure_range: tuple[int, int] | None = None,
) -> pd.DataFrame:
    """Applique les filtres sélectionnés dans la sidebar Exploration."""
    out = df
    if contracts:
        out = out[out["Contract"].isin(contracts)]
    if internet_services:
        out = out[out["InternetService"].isin(internet_services)]
    if payment_methods:
        out = out[out["PaymentMethod"].isin(payment_methods)]
    if tenure_range:
        lo, hi = tenure_range
        out = out[(out["tenure"] >= lo) & (out["tenure"] <= hi)]
    return out


def compute_kpis(df: pd.DataFrame) -> dict:
    """KPIs synthétiques affichés en haut de la page Exploration."""
    n = len(df)
    if n == 0:
        return {"n_clients": 0, "churn_rate": 0.0, "avg_tenure": 0.0, "avg_monthly": 0.0}
    return {
        "n_clients": n,
        "churn_rate": df["Churn"].mean() * 100,
        "avg_tenure": df["tenure"].mean(),
        "avg_monthly": df["MonthlyCharges"].mean(),
    }


def churn_rate_by(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Taux de churn (%) et effectif par modalité d'une colonne catégorielle."""
    if len(df) == 0:
        return pd.DataFrame(columns=[column, "churn_rate", "n_clients"])
    grouped = df.groupby(column, observed=True).agg(
        churn_rate=("Churn", "mean"),
        n_clients=("Churn", "size"),
    ).reset_index()
    grouped["churn_rate"] = grouped["churn_rate"] * 100
    return grouped.sort_values("churn_rate", ascending=False)
