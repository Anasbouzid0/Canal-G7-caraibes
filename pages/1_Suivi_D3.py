import streamlit as st
import pandas as pd
import altair as alt
from st_aggrid import AgGrid, GridOptionsBuilder

st.set_page_config(page_title="Suivi détaillé par technicien", layout="wide")

# === CHARGEMENT DES DONNÉES ===
df = pd.read_excel("Canal inter.xlsx", sheet_name="SUIVI JOURNALIER CANAL")

# Renommer les colonnes si nécessaire
if 'Nom technicien' in df.columns:
    df.rename(columns={"Nom technicien": "NOM"}, inplace=True)

# === FILTRE TECHNICIEN ===
techniciens = df["NOM"].dropna().unique().tolist()
technicien_choisi = st.selectbox("Choisir un technicien", sorted(techniciens))
df_filtered = df[df["NOM"] == technicien_choisi]

# === CALCULS ===
total_interv = len(df_filtered)
etat_counts = df_filtered['État'].value_counts()
ot_real = df_filtered['OT Réalisé'].sum()
ot_report = df_filtered['OT Reportes'].sum()
ot_ok = df_filtered['OT OK'].sum()
ot_nok = df_filtered['OT NOK'].sum()

# === INDICATEURS ===
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Nombre d'interventions", total_interv)
kpi2.metric("OT Réalisés", int(not_real))
kpi3.metric("OT OK / NOK", f"{int(not_ok)} / {int(not_nok)}")
kpi4.metric("Types d'État rencontrés", len(etat_counts))

# === GRAPHIQUE : Montant par jour ===
if 'Date' in df_filtered.columns and 'OT Réalisé' in df_filtered.columns:
    df_filtered['Date'] = pd.to_datetime(df_filtered['Date'], errors='coerce')
    montant_par_jour = df_filtered.groupby('Date')['OT Réalisé'].sum().reset_index()

    st.subheader("\U0001F4C8 OT Réalisés par jour")
    chart = alt.Chart(montant_par_jour).mark_line(point=True).encode(
        x=alt.X('Date:T', title='Date'),
        y=alt.Y('OT Réalisé:Q', title='OT Réalisé'),
        tooltip=['Date:T', 'OT Réalisé:Q']
    ).properties(width=800, height=400)

    st.altair_chart(chart, use_container_width=True)

# === TABLEAU DÉTAILLÉ ===
st.subheader("\U0001F4CA Détails des interventions pour " + technicien_choisi)

colonnes_affichees = ["Date", "NOM", "État", "OT planifiés", "OT Réalisé", "OT OK", "OT NOK", "OT Reportes"]
df_affiche = df_filtered[colonnes_affichees]

# AgGrid
gb = GridOptionsBuilder.from_dataframe(df_affiche)
gb.configure_default_column(filter=True, resizable=True)
gb.configure_pagination()
options = gb.build()

AgGrid(df_affiche, gridOptions=options, theme="alpine", fit_columns_on_grid_load=True)

# === TAUX DE RÉUSSITE ET ÉCHEC ===
st.subheader("\U0001F4C9 Taux de Réussite et d'Échec")

if total_interv > 0:
    taux_reussite = df_filtered['Taux Réussite'].mean()
    taux_echec = df_filtered['Taux Echec'].mean()
    taux_report = df_filtered['Taux Report'].mean()
    taux_cloture = df_filtered['Taux Cloture'].mean()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("% Réussite (OK)", f"{taux_reussite:.2f}%")
    col2.metric("% Échec (NOK)", f"{taux_echec:.2f}%")
    col3.metric("% Reportés", f"{taux_report:.2f}%")
    col4.metric("% Clôturés", f"{taux_cloture:.2f}%")
else:
    st.warning("Aucune intervention enregistrée pour ce technicien.")
