# pages/1_Ecarts_Mai_Avril.py
import streamlit as st
import pandas as pd
import altair as alt
from st_aggrid import AgGrid, GridOptionsBuilder
from io import BytesIO

st.set_page_config(page_title="Suivi des Écarts de Performance", layout="wide")

st.title("📈 Tableau de Bord - Suivi des Écarts de Performance (Mai vs Avril)")

# === Chargement des données ===
file_path = "Ecart.xlsx"
try:
    df_mai = pd.read_excel(file_path, sheet_name="SUIVI HEBDOMADAIRE MAI")
    df_avril = pd.read_excel(file_path, sheet_name="SUIVI HEBDOMADAIRE Avril")
except Exception as e:
    st.error(f"Erreur lors du chargement : {e}")
    st.stop()

# Nettoyage des colonnes
cols_to_compare = [
    "Planifiés", "Ok", "Nok", "Reportés",
    "Taux Réussite", "Taux Echec", "Taux Report", "Taux Cloture",
    "Montant prévu", "Montant réel", "Montant echec"
]

for df in [df_mai, df_avril]:
    df.columns = df.columns.str.strip()

# Extraction et alignement
mai = df_mai[["Semaine"] + cols_to_compare].set_index("Semaine")
avril = df_avril[["Semaine"] + cols_to_compare].set_index("Semaine")
avril = avril.loc[mai.index]

# Calcul des écarts MAI vs AVRIL
ecarts_avr = ((mai - avril) / avril.replace(0, pd.NA)) * 100
ecarts_avr = ecarts_avr.clip(lower=-100, upper=100).round(2)
ecarts_avr.loc["MOYENNE"] = ecarts_avr.mean()

st.header("📋 Synthèse des Écarts - Mois de Mai comparé à Avril")
gb1 = GridOptionsBuilder.from_dataframe(ecarts_avr.reset_index())
gb1.configure_default_column(resizable=True, filter=True, sortable=True)
gb1.configure_pagination()
AgGrid(ecarts_avr.reset_index(), gridOptions=gb1.build(), height=300)

# === Graphiques dynamiques avec barres d'évolution ===

def afficher_graphique(df, indicateurs, titre):
    df_no_avg = df.drop(index="MOYENNE")
    long_df = df_no_avg[indicateurs].reset_index().melt(id_vars="Semaine", var_name="Indicateur", value_name="Écart (%)")
    moyenne = df.loc["MOYENNE", indicateurs].reset_index()
    moyenne.columns = ["Indicateur", "Écart (%)"]

    barre = alt.Chart(moyenne).mark_bar().encode(
        x=alt.X("Indicateur:N", title="Indicateur"),
        y=alt.Y("Écart (%):Q", scale=alt.Scale(domain=[-100, 100])),
        color=alt.condition("datum['Écart (%)'] > 0", alt.value("green"), alt.value("red")),
        tooltip=["Indicateur", "Écart (%)"]
    ).properties(width=900, height=120, title="Synthèse moyenne des écarts (%)")

    ligne = alt.Chart(long_df).mark_line(point=True).encode(
        x="Semaine:N",
        y=alt.Y("Écart (%):Q", scale=alt.Scale(domain=[-100, 100])),
        color="Indicateur",
        tooltip=["Semaine", "Indicateur", "Écart (%)"]
    ).properties(width=900, height=400, title=titre)

    st.altair_chart(barre & ligne, use_container_width=True)

st.subheader("📌 Indicateurs Opérationnels : OK / NOK / Reportés")
action_cols = ["Ok", "Nok", "Reportés"]
afficher_graphique(ecarts_avr, action_cols, "Tendance hebdomadaire des indicateurs opérationnels")

st.subheader("📌 Indicateurs Financiers : Montants")
montant_cols = ["Montant prévu", "Montant réel", "Montant echec"]
afficher_graphique(ecarts_avr, montant_cols, "Tendance hebdomadaire des montants")

st.subheader("📌 Indicateurs de Performance : Taux")
taux_cols = ["Taux Réussite", "Taux Echec", "Taux Report", "Taux Cloture"]
afficher_graphique(ecarts_avr, taux_cols, "Tendance hebdomadaire des taux de performance")

# === Export ===
buffer = BytesIO()
with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
    ecarts_avr.to_excel(writer, sheet_name="Écarts Mai-Avril")
st.download_button("📥 Télécharger les données d’écarts (Excel)", buffer.getvalue(), file_name="ecarts_mai_avril.xlsx")

st.success("✔️ Rapport de comparaison mensuelle généré avec succès")
