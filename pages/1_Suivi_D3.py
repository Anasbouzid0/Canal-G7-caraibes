import streamlit as st
import pandas as pd
import altair as alt
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.set_page_config(page_title="Suivi détaillé par technicien", layout="wide")

# === CHARGEMENT DES DONNÉES ===
df = pd.read_excel("Canal inter.xlsx", sheet_name="SUIVI JOURNALIER CANAL")

# Renommer les colonnes si nécessaire
if 'Nom technicien' in df.columns:
    df.rename(columns={"Nom technicien": "NOM"}, inplace=True)

# === KPIs dynamiques avec total global par défaut ===

# Titre principal
st.subheader(" Suivi des interventions")

# Préparer la liste des techniciens avec option "Tous"
techniciens = df["NOM"].dropna().unique().tolist()
techniciens.insert(0, "Tous")  # Ajouter l'option "Tous"

# === Suivi dynamique des interventions ===
st.subheader("📊 Suivi des interventions")

# Liste des techniciens avec option "Tous"
techniciens = df["NOM"].dropna().unique().tolist()
techniciens.insert(0, "Tous")

# Sélection du technicien
technicien_choisi = st.selectbox("Choisir un technicien", sorted(techniciens))

# Filtrage dynamique
df_filtered = df.copy() if technicien_choisi == "Tous" else df[df["NOM"] == technicien_choisi]

# Calculs
total_planifies = df_filtered['OT planifiés'].sum()
ot_real = df_filtered['OT Réalisé'].sum()
ot_ok = df_filtered['OT OK'].sum()
ot_nok = df_filtered['OT NOK'].sum()
ot_report = df_filtered['OT Reportes'].sum()

# Affichage dynamique — UNE seule barre
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("OT Planifiés", int(total_planifies))
kpi2.metric("OT Réalisés", int(ot_real))
kpi3.metric("OT OK / NOK", f"{int(ot_ok)} / {int(ot_nok)}")
kpi4.metric("OT Reportés", int(ot_report))


# === CALCULS MOYENNES DES TAUX ===
taux_cols = ['Taux Réussite', 'Taux Echec', 'Taux Report', 'Taux Cloture']
for col in taux_cols:
    df_filtered[col] = pd.to_numeric(df_filtered[col], errors='coerce')

moy_taux_reussite = df_filtered['Taux Réussite'].mean()
moy_taux_echec = df_filtered['Taux Echec'].mean()
moy_taux_report = df_filtered['Taux Report'].mean()
moy_taux_cloture = df_filtered['Taux Cloture'].mean()

# === INDICATEURS ===
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("OT Planifiés", int(total_planifies))
kpi2.metric("OT Réalisés", int(ot_real))
kpi3.metric("OT OK / NOK", f"{int(ot_ok)} / {int(ot_nok)}")
kpi4.metric("OT Reportés", int(ot_report))

# === GRAPHIQUE : OT Réalisés par jour avec jour du mois ===
if 'Date' in df_filtered.columns and 'OT Réalisé' in df_filtered.columns:
    df_filtered['Date'] = pd.to_datetime(df_filtered['Date'], errors='coerce')
    montant_par_jour = df_filtered.groupby('Date')['OT Réalisé'].sum().reset_index()
    montant_par_jour['Jour'] = montant_par_jour['Date'].dt.strftime('%d')  # extraire jour (02, 03, ..., 31)

    st.subheader("OT Réalisés par jour")
    chart = alt.Chart(montant_par_jour).mark_line(point=True).encode(
        x=alt.X('Jour:O', title='Mai', sort=montant_par_jour['Jour'].tolist()),
        y=alt.Y('OT Réalisé:Q', title='OT Réalisé'),
        tooltip=['Jour', 'OT Réalisé']
    ).properties(width=800, height=400)

    st.altair_chart(chart, use_container_width=True)

# === TABLEAU DÉTAILLÉ ===
st.subheader(" Détails des interventions pour " + technicien_choisi)

colonnes_affichees = ["Date", "NOM", "État", "OT planifiés", "OT Réalisé", "OT OK", "OT NOK", "OT Reportes"]
df_affiche = df_filtered[colonnes_affichees]

# AgGrid personnalisé avec thème streamlit-dark
gb = GridOptionsBuilder.from_dataframe(df_affiche)
gb.configure_default_column(filter=True, resizable=True)
gb.configure_pagination(paginationAutoPageSize=True)
gb.configure_grid_options(domLayout='normal')
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
    df_affiche,
    gridOptions=options,
    theme="streamlit-dark",
    fit_columns_on_grid_load=True,
    update_mode=GridUpdateMode.NO_UPDATE,
    height=400
)

# === TAUX DE RÉUSSITE ET ÉCHEC ===
st.subheader(" Moyennes des taux")

col1, col2, col3, col4 = st.columns(4)
col1.metric("% Réussite (OK)", f"{moy_taux_reussite:.2f}%")
col2.metric("% Échec (NOK)", f"{moy_taux_echec:.2f}%")
col3.metric("% Reportés", f"{moy_taux_report:.2f}%")
col4.metric("% Clôturés", f"{moy_taux_cloture:.2f}%")
