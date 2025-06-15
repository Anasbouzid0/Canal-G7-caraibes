import streamlit as st
import pandas as pd
import altair as alt
from io import BytesIO

st.set_page_config(page_title="CANAL G7 Caraïbes", layout="centered")
st.markdown("<h1 style='text-align: center; color: #0C2340;'> CANAL G7 Caraïbes – Tableau de Bord Interactif</h1>", unsafe_allow_html=True)
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

# === GRAPHIQUES TECHNICIENS ===
grouped = df_filtered.groupby("TECHNICIEN").agg(
    STT=("STT", "sum"),
    RefCount=("Ref PXO", "count")
).reset_index()

chart1 = alt.Chart(grouped).mark_bar(color="#318C6A").encode(
    x=alt.X("TECHNICIEN", sort=None),
    y=alt.Y("STT"),
    tooltip=["TECHNICIEN", "STT"]
).properties(title="Montant STT par Technicien", height=300)

chart2 = alt.Chart(grouped).mark_bar(color="#F9E266").encode(
    x=alt.X("TECHNICIEN", sort=None),
    y=alt.Y("RefCount"),
    tooltip=["TECHNICIEN", "RefCount"]
).properties(title="Références PXO par Technicien", height=300)

ch1, ch2 = st.columns(2)
ch1.altair_chart(chart1, use_container_width=True)
ch2.altair_chart(chart2, use_container_width=True)

# === TABLEAU DES CODES FACTURATION + TRAVAUX SUPPLÉMENTAIRES ===
st.subheader("Répartition globale Facturation / Travaux Supplémentaires")
df_filtered["FACTURATION"] = df_filtered["FACTURATION"].fillna("")
df_filtered["TRAVAUX SUPPLEMENTAIRES"] = df_filtered["TRAVAUX SUPPLEMENTAIRES"].fillna("")

fact_codes = df_filtered["FACTURATION"].astype(str).str.upper().str.split(r"[,\s]+")
travaux_codes = df_filtered["TRAVAUX SUPPLEMENTAIRES"].astype(str).str.upper().str.split(r"[,\s]+")

fact_exploded = fact_codes.explode()
ts_exploded = travaux_codes.explode()

all_codes = pd.concat([fact_exploded, ts_exploded]).astype(str).str.strip()
all_codes = all_codes[all_codes != ""]

code_counts = all_codes.value_counts().sort_index()
code_counts_df = pd.DataFrame(code_counts).T
code_counts_df.index = ["Nombre"]

# === AFFICHAGE DU TABLEAU (COMPATIBLE MOBILE) ===
with st.expander("Afficher la répartition des codes"):
    st.dataframe(code_counts_df.T.reset_index().rename(columns={"index": "Code"}), use_container_width=True)

# === GRAPHIQUE DES CODES ===
st.subheader("Répartition des codes – Nombre d’occurrences")
code_counts_long = code_counts.reset_index()
code_counts_long.columns = ["Code", "Nombre"]

chart_counts = alt.Chart(code_counts_long).mark_bar(size=30).encode(
    x=alt.X("Code:N", sort='-y', title="Code"),
    y=alt.Y("Nombre:Q", title="Nombre d'occurrences"),
    tooltip=["Code", "Nombre"]
).properties(height=400)

st.altair_chart(chart_counts, use_container_width=True)

# === TABLEAU PRINCIPAL ===
st.subheader("Détails des interventions")
with st.expander("Afficher le tableau détaillé"):
    st.dataframe(df_filtered, use_container_width=True)

# === EXPORT CSV ===
csv = df_filtered.to_csv(index=False).encode('utf-8')
st.download_button("Télécharger CSV", csv, file_name="G7_data.csv", mime="text/csv")

# === EXPORT EXCEL ===
buffer = BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    df_filtered.to_excel(writer, index=False, sheet_name="Feuille1")
st.download_button("Télécharger Excel", buffer.getvalue(), file_name="G7_data.xlsx", mime="application/vnd.ms-excel")
