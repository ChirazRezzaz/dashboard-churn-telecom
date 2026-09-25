# Churn Télécom — Dashboard interactif

Application **Streamlit** permettant au service client d'un opérateur télécom d'explorer les facteurs de résiliation (churn) et de **simuler en direct**, pendant un appel, la probabilité qu'un client donné soit sur le point de résilier — sans solliciter l'équipe data.

Ce dashboard utilise le dataset (IBM Telco Customer Churn) et un pipeline de modélisation (Gradient Boosting, ROC-AUC ≈ 0.84 sur le jeu de test), intégrés dans une application MVC.

## Fonctionnalités

### Page Exploration
- Filtres dans la sidebar : type de contrat, service internet, méthode de paiement, ancienneté
- 4 KPIs synthétiques (`st.metric`) : nombre de clients, taux de churn, ancienneté moyenne, facture mensuelle moyenne
- 6 visualisations interactives Plotly : taux de churn par contrat / service internet / méthode de paiement, distribution de l'ancienneté, charge mensuelle par statut, ancienneté vs charge mensuelle
- Table de données filtrées consultable en un clic

### Page Prédiction
- Formulaire (`st.form`) organisé par sections (profil client, contrat & facturation, services souscrits)
- Champs conditionnels : les services liés au téléphone/internet ne s'affichent que si ces services sont souscrits, pour éviter toute saisie incohérente
- Jauge de probabilité de churn + recommandation d'action
- Détection et avertissement des saisies incohérentes ou aberrantes (ex. charges totales incompatibles avec l'ancienneté)

## Architecture (MVC)

```
dashboard-churn-telecom/
├── app.py                          # Point d'entrée, navigation entre les pages
├── models/
│   ├── data_loader.py              # Chargement des données (@st.cache_data)
│   ├── transforms.py                # Nettoyage, feature engineering, agrégations
│   └── predictor.py                 # Chargement du pipeline (@st.cache_resource) et prédiction
├── views/
│   ├── components.py                # KPIs, graphiques Plotly, jauge — composants réutilisables
│   ├── exploration_view.py          # Mise en page de la page Exploration
│   └── prediction_view.py           # Formulaire et affichage du résultat de la page Prédiction
├── controllers/
│   ├── exploration_controller.py    # Orchestration : filtres → Model → View
│   └── prediction_controller.py     # Orchestration : formulaire → Model → View
├── data/
│   └── telco_churn.csv              # Dataset IBM Telco Customer Churn
├── model.joblib                     # Pipeline sklearn entraîné (prétraitement + Gradient Boosting)
└── requirements.txt
```

**Séparation des responsabilités :**
- **Model** (`models/`) : seul endroit qui touche au disque et transforme des données. Aucune ligne Streamlit d'affichage.
- **View** (`views/`) : affichage pur (widgets, métriques, graphiques). Ne lit ni ne transforme jamais un DataFrame — elle reçoit des données déjà prêtes.
- **Controller** (`controllers/`) : orchestre la lecture des entrées utilisateur, l'appel au Model, et la transmission des résultats à la View.

## Choix de conception — variables engineerées

Le pipeline attend des variables créées (`tenure_group`, `num_services`, `senior_isole`, `charge_par_service`) qui ne sont **pas** demandées directement dans le formulaire : elles sont **recalculées automatiquement** à partir des saisies brutes (`models/predictor.construire_ligne_entree`), en réutilisant exactement la même logique que celle utilisée à l'entraînement (`models/transforms.engineer_features`). Ce choix évite de demander à un conseiller client des informations qu'il n'a pas naturellement (ex. « quelle est votre tranche d'ancienneté ? ») et garantit la cohérence entre les données d'entraînement et les données servies en production.

## Installation et lancement

```bash
cd dashboard-churn-telecom
python -m venv .venv
source .venv/bin/activate      # Windows : .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

L'application s'ouvre automatiquement sur `http://localhost:8501`.

> Le modèle (`model.joblib`) et les données (`data/telco_churn.csv`) sont déjà inclus dans le dépôt — aucune étape supplémentaire n'est nécessaire pour lancer l'application. Pour ré-entraîner le modèle après une modification du pipeline, relancez le script d'entraînement (voir `models/transforms.py` pour la logique de feature engineering reproduite à l'identique entre le notebook et l'application).

## Modèle

- **Algorithme :** `GradientBoostingClassifier` (n_estimators=100, learning_rate=0.1), au sein d'un `Pipeline` sklearn incluant l'imputation, le scaling (variables numériques) et le one-hot encoding (variables catégorielles).
- **Performance (évaluation holdout 20%) :** ROC-AUC ≈ 0.843, F1 (classe churn) ≈ 0.59.
- **Modèle sauvegardé :** ré-entraîné sur 100 % des données disponibles avant sauvegarde (pratique standard de mise en production), l'évaluation ci-dessus provenant d'un split dédié fait avant ce ré-entraînement final.

## Stack technique

Python - Streamlit - Plotly Express - Scikit-learn - Pandas - Joblib
