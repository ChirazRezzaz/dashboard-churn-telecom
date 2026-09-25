"""Chargement du pipeline sklearn et prédiction (Model, au sens MVC).

Le pipeline sauvegardé (`model.joblib`) contient le prétraitement complet
(imputation, scaling, one-hot encoding) ET le classifieur — l'application
n'a donc jamais besoin de dupliquer cette logique, seulement de lui fournir
un DataFrame avec les bonnes colonnes brutes.
"""
from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

from models.transforms import FEATURE_COLUMNS, engineer_features

MODEL_PATH = Path(__file__).resolve().parent.parent / "model.joblib"


@st.cache_resource(show_spinner="Chargement du modèle...")
def charger_modele():
    """Charge le pipeline sklearn entraîné (mis en cache : une seule lecture disque)."""
    return joblib.load(MODEL_PATH)


def construire_ligne_entree(saisie_brute: dict) -> pd.DataFrame:
    """Transforme les saisies brutes du formulaire en une ligne de features
    identique à celles utilisées à l'entraînement (recalcul des variables
    engineerées : tenure_group, num_services, senior_isole, charge_par_service).

    Choix de conception : le formulaire ne demande que des caractéristiques
    "naturelles" pour un conseiller client (ancienneté, services souscrits...),
    jamais les variables dérivées elles-mêmes — elles sont recalculées ici,
    exactement comme au Projet 2, pour garantir la cohérence train/serving.
    """
    df = pd.DataFrame([saisie_brute])
    df = engineer_features(df)
    return df[FEATURE_COLUMNS]


def valider_entree(saisie_brute: dict) -> list[str]:
    """Contrôles de cohérence métier sur la saisie utilisateur.

    Renvoie une liste d'avertissements (chaîne vide = aucune alerte). La
    prédiction reste possible même en présence d'avertissements — le pipeline
    sklearn est robuste à des combinaisons improbables — mais l'utilisateur
    est prévenu que le résultat doit être interprété avec prudence.
    """
    alertes: list[str] = []
    tenure = saisie_brute.get("tenure", 0)
    monthly = saisie_brute.get("MonthlyCharges", 0)
    total = saisie_brute.get("TotalCharges", 0)

    if tenure == 0 and total > 0:
        alertes.append(
            "Un client avec 0 mois d'ancienneté ne devrait pas avoir de charges "
            "totales déjà facturées — vérifiez la cohérence de la saisie."
        )
    if tenure > 0 and total < monthly * 0.5:
        alertes.append(
            "Le total facturé semble anormalement bas par rapport à l'ancienneté "
            "et à la charge mensuelle — vérifiez la saisie."
        )
    if total > monthly * (tenure + 1) * 1.5:
        alertes.append(
            "Le total facturé semble anormalement élevé par rapport à l'ancienneté "
            "et à la charge mensuelle — vérifiez la saisie."
        )
    if saisie_brute.get("PhoneService") == "No" and saisie_brute.get("MultipleLines") not in (
        "No phone service", None
    ):
        alertes.append(
            "Incohérence : un client sans service téléphonique ne peut pas avoir "
            "plusieurs lignes."
        )
    if saisie_brute.get("InternetService") == "No":
        services_internet = ["OnlineSecurity", "OnlineBackup", "DeviceProtection",
                              "TechSupport", "StreamingTV", "StreamingMovies"]
        incoherents = [
            s for s in services_internet
            if saisie_brute.get(s) not in ("No internet service", None)
        ]
        if incoherents:
            alertes.append(
                "Incohérence : un client sans accès internet ne peut pas avoir de "
                "services associés (sécurité, streaming...)."
            )
    return alertes


def predire(saisie_brute: dict) -> tuple[float, str]:
    """Retourne (probabilité de churn, label prédit) pour une saisie donnée."""
    modele = charger_modele()
    df_entree = construire_ligne_entree(saisie_brute)
    proba = float(modele.predict_proba(df_entree)[0, 1])
    label = "Churn" if proba >= 0.5 else "Fidèle"
    return proba, label
