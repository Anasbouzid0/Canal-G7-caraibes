import streamlit as st
import pandas as pd
import altair as alt
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.set_page_config(page_title="Suivi détaillé par technicien", layout="wide")

# === CHARGEMENT DES DONNÉES ===
df = pd.read_excel("Canal inter.xlsx", sheet_name="SUIVI JOURNALIER CANAL")
df_stt = pd.read_excel("Canal Mai.xlsx")  # contient les montants STT par technicien

# Renommer les colonnes si nécessaire
if 'Nom technicien' in df.columns:
    df.rename(columns={"Nom technicien": "NOM"}, inplace=True)

# === TABLEAU GLOBAL PAR TECHNICIEN ===
st.subheader("\U0001F4CA Synthèse globale par technicien")
df_grouped = df.groupby("NOM").agg({
    "OT Réalisé": "sum",
    "OT OK": "sum",
    "OT NOK": "sum",
    "Taux Réussite": "mean",
    "Taux Echec": "mean",
    "Taux Cloture": "mean",
    "Taux Report": "mean"
}).reset_index()

# Ajouter les montants STT depuis le deuxième fichier
if 'NOM' in df_stt.columns and 'STT' in df_stt.columns:
    montant_stt = df_stt.groupby("NOM")["STT"].sum().reset_index()
    df_grouped = pd.merge(df_grouped, montant_stt, on="NOM", how="left")

# Affichage du tableau sombre
gb = GridOptionsBuilder.from_dataframe(df_grouped)
gb.configure_default_column(filter=True, resizable=True)
gb.configure_pagination(paginationAutoPageSize=True)
options = gb.build()

st.markdown("""
    <style>
    .ag-theme-streamlit-dark {
        background-color: #2e2e2e !important;
        color: white !important;
    }
    .ag-theme-streamlit-dark .ag-header-cell-label {
        color: white !important;
    }
    .ag-theme-streamlit-dark .ag-row, .ag-theme-streamlit-dark .ag-cell {
        background-color: #1e1e1e !important;
        color: #f0f0f0 !important;
    }
    </style>
""", unsafe_allow_html=True)

AgGrid(
    df_grouped,
    gridOptions=options,
    theme="streamlit-dark",
    fit_columns_on_grid_load=True,
    update_mode=GridUpdateMode.NO_UPDATE,
    height=400
)

# === GRAPHIQUE 1 : Montant STT par technicien ===
st.subheader("\U0001F4B8 Montant STT par technicien")
chart1 = alt.Chart(df_grouped).mark_bar().encode(
    x=alt.X('NOM:N', sort='-y', title='Technicien'),
    y=alt.Y('STT:Q', title='Montant STT (€)'),
    tooltip=['NOM', 'STT']
).properties(width=800, height=400)

st.altair_chart(chart1, use_container_width=True)

# === GRAPHIQUE 2 : Montant par jour (selon technicien) ===
st.subheader("\U0001F4C8 Variation des montants STT par jour et par technicien")

if 'Date' in df_stt.columns:
    df_stt['Date'] = pd.to_datetime(df_stt['Date'], errors='coerce')
    montant_jour_technicien = df_stt.groupby(["Date", "NOM"])["STT"].sum().reset_index()

    chart2 = alt.Chart(montant_jour_technicien).mark_line().encode(
        x=alt.X('Date:T', title='Date'),
        y=alt.Y('STT:Q', title='Montant STT (€)'),
        color='NOM:N',
        tooltip=['Date:T', 'NOM', 'STT']
    ).properties(width=800, height=400)

    st.altair_chart(chart2, use_container_width=True)
else:
    st.warning("Colonne 'Date' manquante dans le fichier Canal Mai.xlsx")
