import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
import pandas as pd
import altair as alt
from io import BytesIO
from PIL import Image

st.set_page_config(page_title="Dashboard G7 Caraïbes", layout="wide")

# === CHARGEMENT DES DONNÉES ===
df = pd.read_excel("Canal Mai.xlsx")

# === FILTRES ===
st.sidebar.header("Filtres")
techs = sorted(df["TECHNICIEN"].dropna().unique())
prests = sorted(df["PRESTATAIRE"].dropna().unique())
f_techs = st.sidebar.multiselect("Technicien", techs, default=techs)
f_prests = st.sidebar.multiselect("Prestataire", prests, default=prests)
df_filtered = df[df["TECHNICIEN"].isin(f_techs) & df["PRESTATAIRE"].isin(f_prests)]

# === KPI ===
col1, col2, col3 = st.columns(3)
col1.metric("Montant GSET (€)", f"{df_filtered['GSET'].sum():,.2f}")
col2.metric("Montant STT (€)", f"{df_filtered['STT'].sum():,.2f}")
col3.metric("Nombre de Ref PXO", f"{df_filtered['Ref PXO'].count()}")

# === GRAPHIQUES ===
grouped = df_filtered.groupby("TECHNICIEN").agg(
    STT=("STT", "sum"),
    RefCount=("Ref PXO", "count")
).reset_index()

chart1 = alt.Chart(grouped).mark_bar(color="#318C6A").encode(
    x=alt.X("TECHNICIEN", sort=None),
    y=alt.Y("STT"),
    tooltip=["TECHNICIEN", "STT"]
).properties(title="Montant STT par Technicien", width=400, height=300)

chart2 = alt.Chart(grouped).mark_bar(color="#F9E266").encode(
    x=alt.X("TECHNICIEN", sort=None),
    y=alt.Y("RefCount"),
    tooltip=["TECHNICIEN", "RefCount"]
).properties(title="Références PXO par Technicien", width=400, height=300)

ch1, ch2 = st.columns(2)
ch1.altair_chart(chart1, use_container_width=True)
ch2.altair_chart(chart2, use_container_width=True)

# === TABLEAU HORIZONTAL : Types de facturation ===
st.subheader(" Répartition des types de facturation")
fact_counts = df_filtered["FACTURATION"].value_counts().sort_index()
fact_row = pd.DataFrame(fact_counts).T
fact_row.index = ["Nombre"]

# AgGrid horizontal
gb_fact = GridOptionsBuilder.from_dataframe(fact_row)
gb_fact.configure_default_column(filter=True, resizable=True, cellStyle={'textAlign': 'center'})
grid_options_fact = gb_fact.build()

AgGrid(
    fact_row,
    gridOptions=grid_options_fact,
    theme="blue",
    height=120,
    fit_columns_on_grid_load=True
)

# === TABLEAU PRINCIPAL ===
st.subheader("Détails des interventions")
gb = GridOptionsBuilder.from_dataframe(df_filtered)
gb.configure_default_column(filter=True, sortable=True)
gb.configure_pagination()
gb.configure_side_bar()
grid_options = gb.build()

search = st.text_input("🔍 Recherche dans le tableau")
if search:
    grid_options["quickFilterText"] = search

AgGrid(df_filtered, gridOptions=grid_options, height=350)

# === EXPORT CSV ===
csv = df_filtered.to_csv(index=False).encode('utf-8')
st.download_button("📥 Télécharger CSV", csv, file_name="G7_data.csv", mime="text/csv")

# === EXPORT EXCEL ===
buffer = BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    df_filtered.to_excel(writer, index=False, sheet_name="Feuille1")
st.download_button("📥 Télécharger Excel", buffer.getvalue(), file_name="G7_data.xlsx", mime="application/vnd.ms-excel")
