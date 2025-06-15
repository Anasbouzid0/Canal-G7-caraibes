# pages/1_Ecarts_Mai_Avril.py
import streamlit as st
import pandas as pd
import altair as alt
from st_aggrid import AgGrid, GridOptionsBuilder

st.set_page_config(page_title="Écarts Mai / Avril", layout="wide")

st.title("📊 Analyse des Écarts Hebdomadaires : Mai vs Avril")

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
df_mai.columns = df_mai.columns.str.strip()
df_avril.columns = df_avril.columns.str.strip()

# Extraction et alignement
mai = df_mai[["Semaine"] + cols_to_compare].set_index("Semaine")
avril = df_avril[["Semaine"] + cols_to_compare].set_index("Semaine")
avril = avril.loc[mai.index]  # Réalignement

# Calcul des écarts en pourcentage avec traitement des 0 et limite [-100%, +100%]
ecarts = ((mai - avril) / avril.replace(0, pd.NA)) * 100
ecarts = ecarts.clip(lower=-100, upper=100).round(2)
ecarts.loc["MOYENNE"] = ecarts.mean()

# === Affichage tableau interactif ===
st.subheader("🧾 Tableau des écarts en pourcentage")
gb = GridOptionsBuilder.from_dataframe(ecarts.reset_index())
gb.configure_default_column(resizable=True, filter=True, sortable=True)
gb.configure_pagination()
grid_options = gb.build()
AgGrid(ecarts.reset_index(), gridOptions=grid_options, height=450, fit_columns_on_grid_load=True)

# === Graphique 1 : OK / NOK / Reportés ===
st.subheader("✅ Évolution des écarts : OK / NOK / Reportés")
indicateurs_actions = ["Ok", "Nok", "Reportés"]
long_action = ecarts.drop(index="MOYENNE")[indicateurs_actions].reset_index().melt(id_vars="Semaine", var_name="Indicateur", value_name="Écart (%)")
chart_action = alt.Chart(long_action).mark_line(point=True).encode(
    x="Semaine:N",
    y=alt.Y("Écart (%):Q", scale=alt.Scale(domain=[-100, 100])),
    color="Indicateur",
    tooltip=["Semaine", "Indicateur", "Écart (%)"]
).properties(width=900, height=400)
st.altair_chart(chart_action, use_container_width=True)

# === Graphique 2 : Montants ===
st.subheader("💶 Évolution des écarts : Montants")
indicateurs_montant = ["Montant prévu", "Montant réel", "Montant echec"]
long_montant = ecarts.drop(index="MOYENNE")[indicateurs_montant].reset_index().melt(id_vars="Semaine", var_name="Indicateur", value_name="Écart (%)")
chart_montant = alt.Chart(long_montant).mark_line(point=True).encode(
    x="Semaine:N",
    y=alt.Y("Écart (%):Q", scale=alt.Scale(domain=[-100, 100])),
    color="Indicateur",
    tooltip=["Semaine", "Indicateur", "Écart (%)"]
).properties(width=900, height=400)
st.altair_chart(chart_montant, use_container_width=True)

# === Graphique 3 : Taux ===
st.subheader("📊 Évolution des écarts : Taux")
indicateurs_taux = ["Taux Réussite", "Taux Echec", "Taux Report", "Taux Cloture"]
long_taux = ecarts.drop(index="MOYENNE")[indicateurs_taux].reset_index().melt(id_vars="Semaine", var_name="Indicateur", value_name="Écart (%)")
chart_taux = alt.Chart(long_taux).mark_line(point=True).encode(
    x="Semaine:N",
    y=alt.Y("Écart (%):Q", scale=alt.Scale(domain=[-100, 100])),
    color="Indicateur",
    tooltip=["Semaine", "Indicateur", "Écart (%)"]
).properties(width=900, height=400)
st.altair_chart(chart_taux, use_container_width=True)

# === Export CSV ===
st.download_button(
    "📥 Télécharger les écarts (CSV)",
    ecarts.reset_index().to_csv(index=False).encode("utf-8"),
    file_name="ecarts_mai_avril.csv",
    mime="text/csv"
)

# === Export Excel ===
from io import BytesIO
buffer = BytesIO()
with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
    ecarts.to_excel(writer, index=True, sheet_name="Écarts")
st.download_button(
    "📥 Télécharger les écarts (Excel)",
    buffer.getvalue(),
    file_name="ecarts_mai_avril.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# === Fin de page ===
st.success("Analyse complète générée avec succès ✅")
