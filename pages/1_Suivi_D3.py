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
etat_counts = df_filtered['ETAT'].value_counts()
ot_real = etat_counts.get("Réalisé", 0)
ot_report = etat_counts.get("Reporté", 0)
ot_ok = etat_counts.get("OK", 0)
ot_nok = etat_counts.get("NOK", 0)

fact_codes = df_filtered['FACTURATION'].nunique()
fact_types = df_filtered['FACTURATION'].value_counts()

# === INDICATEURS ===
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Nombre d'interventions", total_interv)
kpi2.metric("OT Réalisés", int(ot_real))
kpi3.metric("OT OK / NOK", f"{ot_ok} / {ot_nok}")
kpi4.metric("Types d'État rencontrés", len(etat_counts))

# === GRAPHIQUE : Montant par jour ===
if 'DATE' in df_filtered.columns and 'STT' in df_filtered.columns:
    df_filtered['DATE'] = pd.to_datetime(df_filtered['DATE'], errors='coerce')
    montant_par_jour = df_filtered.groupby('DATE')['STT'].sum().reset_index()

    st.subheader("\U0001F4C8 Montant STT par jour")
    chart = alt.Chart(montant_par_jour).mark_line(point=True).encode(
        x=alt.X('DATE:T', title='Date'),
        y=alt.Y('STT:Q', title='Montant STT (€)'),
        tooltip=['DATE:T', 'STT:Q']
    ).properties(width=800, height=400)

    st.altair_chart(chart, use_container_width=True)

# === TABLEAU DÉTAILLÉ ===
st.subheader("\U0001F4CA Détails des interventions pour " + technicien_choisi)

colonnes_affichees = ["DATE", "NOM", "FACTURATION", "ETAT", "STT"]
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
    taux_reussite = round((ot_ok / total_interv) * 100, 2)
    taux_echec = round((ot_nok / total_interv) * 100, 2)
    taux_report = round((ot_report / total_interv) * 100, 2)
    taux_cloture = round((ot_real / total_interv) * 100, 2)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("% Réussite (OK)", f"{taux_reussite}%")
    col2.metric("% Échec (NOK)", f"{taux_echec}%")
    col3.metric("% Reportés", f"{taux_report}%")
    col4.metric("% Clôturés (Réalisé)", f"{taux_cloture}%")
else:
    st.warning("Aucune intervention enregistrée pour ce technicien.")
