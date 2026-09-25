"""Orchestration de la page Exploration (Controller, au sens MVC).

Lit les données et les filtres, appelle le Model pour filtrer/agréger,
puis délègue tout l'affichage à la View. Ne construit aucune figure et
ne lit aucun fichier directement.
"""
from __future__ import annotations

from models import data_loader, transforms
from views import exploration_view


def run() -> None:
    df = data_loader.load_processed_data()
    options = data_loader.get_filter_options(df)

    filtres = exploration_view.render_sidebar_filters(options)

    df_filtered = transforms.filter_data(
        df,
        contracts=filtres["contracts"],
        internet_services=filtres["internet_services"],
        payment_methods=filtres["payment_methods"],
        tenure_range=filtres["tenure_range"],
    )

    kpis = transforms.compute_kpis(df_filtered)
    rate_by_contract = transforms.churn_rate_by(df_filtered, "Contract")
    rate_by_internet = transforms.churn_rate_by(df_filtered, "InternetService")
    rate_by_payment = transforms.churn_rate_by(df_filtered, "PaymentMethod")

    exploration_view.render(
        df_filtered, kpis, rate_by_contract, rate_by_internet, rate_by_payment
    )
