import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Suivi D3 - G7 Caraïbes", page_icon="📈", layout="wide")

st.title("📊 Suivi Opérationnel D3 - G7 Caraïbes")

# === Chargement des données ===
df = pd.read_excel("Canal inter.xlsx")
df = df.rename(columns={"Nom technicien": "NOM"}) if "Nom technicien" in df.columns else df

# Nettoyage des colonnes utiles
colonnes_utiles = [
    "NOM", "Date", "État", "OT planifiés", "OT Réalisé", 
    "OT OK", "OT NOK", "OT Reportes", "Taux Réussite", 
    "Taux Echec", "Taux Cloture", "Taux Report"
]
df = df[colonnes_utiles].dropna(subset=["NOM", "Date"])

# Convertir Date si nécessaire
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = df.dropna(subset=["Date"])

# === Filtres ===
st.sidebar.header("🔎 Filtres")
tech_list = sorted(df["NOM"].unique())
selected_tech = st.sidebar.selectbox("Technicien", tech_list)
df_tech = df[df["NOM"] == selected_tech]

# === Indicateurs ===
total_interv = len(df_tech)
ot_real = df_tech["OT Réalisé"].sum()
ot_ok = df_tech["OT OK"].sum()
ot_nok = df_tech["OT NOK"].sum()
nb_fact_types = df_tech["État"].nunique()

# Moyennes taux
taux_ok = df_tech["Taux Réussite"].mean()
taux_echec = df_tech["Taux Echec"].mean()
taux_cloture = df_tech["Taux Cloture"].mean()
taux_report = df_tech["Taux Report"].mean()

# === Affichage des KPIs ===
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Nombre d'interventions", total_interv)
kpi2.metric("OT Réalisés", int(ot_real))
kpi3.metric("OT OK / NOK", f"{int(not_ok)} / {int(not_nok)}")
kpi4.metric("Types d'État rencontrés", nb_fact_types)

col5, col6, col7, col8 = st.columns(4)
col5.metric("Taux de Réussite", f"{taux_ok:.2f}%")
col6.metric("Taux d'Échec", f"{taux_echec:.2f}%")
col7.metric("Taux de Clôture", f"{taux_cloture:.2f}%")
col8.metric("Taux de Report", f"{taux_report:.2f}%")

# === Graphe de variation du nombre d'interventions par jour ===
daily_df = df_tech.groupby("Date")["OT Réalisé"].sum().reset_index()
line_chart = alt.Chart(daily_df).mark_line(point=True).encode(
    x="Date:T",
    y=alt.Y("OT Réalisé:Q", title="OT Réalisé"),
    tooltip=["Date", "OT Réalisé"]
).properties(
    title=f"📈 Évolution des OT Réalisés pour {selected_tech}",
    width=900,
    height=350
)

st.altair_chart(line_chart, use_container_width=True)

# === Tableau journalier ===
st.subheader("🗓️ Détail journalier des interventions")
st.dataframe(df_tech.sort_values("Date", ascending=False).reset_index(drop=True))
