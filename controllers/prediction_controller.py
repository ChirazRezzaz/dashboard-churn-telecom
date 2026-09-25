"""Orchestration de la page Prédiction (Controller, au sens MVC).

Récupère la saisie utilisateur via la View, la fait valider et scorer par
le Model, puis transmet le résultat à la View pour affichage.
"""
from __future__ import annotations

from models import predictor
from views import prediction_view


def run() -> None:
    prediction_view.render_page_header()

    saisie, submitted = prediction_view.render_form()

    if not submitted or saisie is None:
        return

    alertes = predictor.valider_entree(saisie)
    proba, label = predictor.predire(saisie)

    prediction_view.render_resultat(proba, label, alertes)
