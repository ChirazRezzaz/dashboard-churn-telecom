import streamlit as st

from controllers import exploration_controller, prediction_controller

st.set_page_config(
    page_title="Dashboard Churn Télécom",
    page_icon="📉",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.title("Churn Télécom")
st.sidebar.caption("Outil interne — équipe service client")

page = st.sidebar.radio(
    "Navigation",
    ["Exploration", "Prédiction"],
    label_visibility="collapsed",
)

st.sidebar.divider()
st.sidebar.markdown(
    "**À propos**\n\n"
    "Ce dashboard explore les facteurs de résiliation (churn) des clients "
    "d'un opérateur télécom et permet de simuler, pour un client donné, "
    "sa probabilité de résiliation à partir d'un modèle de Gradient Boosting "
    "(ROC-AUC ≈ 0.84 sur le jeu de test)."
)

if page == "Exploration":
    exploration_controller.run()
else:
    prediction_controller.run()
