import streamlit as st
import pandas as pd
import altair as alt
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from io import BytesIO

st.set_page_config(page_title="Dashboard G7 Caraïbes", layout="wide")

# === CHARGEMENT DES DONNÉES ===
df = pd.read_excel("Canal Mai.xlsx")

# === FILTRES DANS LA PAGE ===
st.title("Dashboard G7 Caraïbes")

col1, col2 = st.columns(2)
with col1:
    techs = sorted(df["TECHNICIEN"].dropna().unique())
    selected_techs = st.multiselect("Filtrer par Technicien", techs, default=techs)
with col2:
    prests = sorted(df["PRESTATAIRE"].dropna().unique())
    selected_prests = st.multiselect("Filtrer par Prestataire", prests, default=prests)

df_filtered = df[df["TECHNICIEN"].isin(selected_techs) & df["PRESTATAIRE"].isin(selected_prests)]

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

# === RÉPARTITION DES TYPES DE FACTURATION ===
st.subheader("Répartition des types de facturation")
fact_counts = df_filtered["FACTURATION"].fillna("").str.upper().str.strip()
fact_counts = fact_counts[fact_counts != ""].value_counts().sort_index()
fact_row = pd.DataFrame(fact_counts).T
fact_row.index = ["Nombre"]

gb_fact = GridOptionsBuilder.from_dataframe(fact_row)
gb_fact.configure_default_column(filter=True, resizable=True, cellStyle={'textAlign': 'center'})
grid_options_fact = gb_fact.build()

AgGrid(
    fact_row,
    gridOptions=grid_options_fact,
    theme="streamlit",
    height=120,
    fit_columns_on_grid_load=True
)

# === TABLEAU PRINCIPAL AVEC RECHERCHE ===
st.subheader("Détails des interventions")

search = st.text_input("🔍 Recherche dans le tableau")
gb = GridOptionsBuilder.from_dataframe(df_filtered)
gb.configure_default_column(filter=True, sortable=True)
gb.configure_pagination()
gb.configure_side_bar()
if search:
    gb.configure_grid_options(quickFilterText=search)
grid_options = gb.build()

AgGrid(df_filtered, gridOptions=grid_options, height=400, fit_columns_on_grid_load=True, theme="streamlit")

# === EXPORT DES DONNÉES FILTRÉES ===
csv = df_filtered.to_csv(index=False).encode("utf-8")
st.download_button("Télécharger CSV filtré", data=csv, file_name="G7_filtré.csv", mime="text/csv")

excel_buffer = BytesIO()
with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
    df_filtered.to_excel(writer, index=False, sheet_name="Filtré")
st.download_button("Télécharger Excel filtré", data=excel_buffer.getvalue(), file_name="G7_filtré.xlsx", mime="application/vnd.ms-excel")
