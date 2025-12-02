import streamlit as st
import pandas as pd
import plotly.express as px
import io

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Mon Simulateur Budgétaire",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- STYLE CSS (Pour l'intégration Systeme.io) ---
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .block-container {padding-top: 1rem; padding-bottom: 2rem;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- DONNÉES INITIALES ---
DEFAULT_EXPENSES = [
    {"Catégorie": "Foyer", "Poste": "Loyer résidence principale", "Mensuel": 0.0},
    {"Catégorie": "Foyer", "Poste": "Assurance Habitation", "Mensuel": 0.0},
    {"Catégorie": "Foyer", "Poste": "Electricité / Eau", "Mensuel": 0.0},
    {"Catégorie": "Foyer", "Poste": "Internet & Mobile", "Mensuel": 0.0},
    {"Catégorie": "Vie Courante", "Poste": "Dépenses alimentaires", "Mensuel": 0.0},
    {"Catégorie": "Vie Courante", "Poste": "Vêtements & Shopping", "Mensuel": 0.0},
    {"Catégorie": "Vie Courante", "Poste": "Entretien (ménage, jardin)", "Mensuel": 0.0},
    {"Catégorie": "Enfants", "Poste": "Scolarité / Garde", "Mensuel": 0.0},
    {"Catégorie": "Loisirs", "Poste": "Sport / Musique", "Mensuel": 0.0},
    {"Catégorie": "Loisirs", "Poste": "Resto / Sorties", "Mensuel": 0.0},
    {"Catégorie": "Loisirs", "Poste": "Voyages (lissé mensuel)", "Mensuel": 0.0},
    {"Catégorie": "Loisirs", "Poste": "Plaisirs / Jeux / Tabac", "Mensuel": 0.0},
    {"Catégorie": "Transport", "Poste": "Carburant / Péage", "Mensuel": 0.0},
    {"Catégorie": "Transport", "Poste": "Assurance / Entretien Auto", "Mensuel": 0.0},
    {"Catégorie": "Transport", "Poste": "Transports en commun", "Mensuel": 0.0},
    {"Catégorie": "Banque", "Poste": "Crédit Immo / Loyer", "Mensuel": 0.0},
    {"Catégorie": "Banque", "Poste": "Crédits Conso / Auto", "Mensuel": 0.0},
    {"Catégorie": "Impôts", "Poste": "Impôt sur le revenu (mensuel)", "Mensuel": 0.0},
]

DEFAULT_INCOME = [
    {"Type": "Travail", "Source": "Salaires (Net)", "Mensuel": 0.0},
    {"Type": "Travail", "Source": "Primes / Bonus", "Mensuel": 0.0},
    {"Type": "Travail", "Source": "Bénéfices (Indépendants)", "Mensuel": 0.0},
    {"Type": "Patrimoine", "Source": "Loyers perçus", "Mensuel": 0.0},
    {"Type": "Aides", "Source": "CAF / APL", "Mensuel": 0.0},
    {"Type": "Aides", "Source": "Chômage / Retraite", "Mensuel": 0.0},
    {"Type": "Autre", "Source": "Autre revenus", "Mensuel": 0.0},
]

# --- FONCTIONS ---
def load_data():
    if 'df_expenses' not in st.session_state:
        st.session_state.df_expenses = pd.DataFrame(DEFAULT_EXPENSES)
    if 'df_income' not in st.session_state:
        st.session_state.df_income = pd.DataFrame(DEFAULT_INCOME)

def calculate_weights(df):
    """Ajoute une colonne de pourcentage au dataframe."""
    total = df["Mensuel"].sum()
    if total > 0:
        # On calcule le ratio (ex: 0.30 pour 30%)
        df["Poids"] = df["Mensuel"] / total
    else:
        df["Poids"] = 0.0
    return df

def convert_df_to_csv(df_inc, df_exp, balance_m, balance_a):
    output = io.StringIO()
    output.write("--- RAPPORT BUDGETAIRE ---\n\n")
    output.write(f"Reste a vivre Mensuel;{balance_m}\n")
    output.write(f"Reste a vivre Annuel;{balance_a}\n\n")
    output.write("--- REVENUS ---\n")
    df_inc.to_csv(output, index=False, sep=";")
    output.write("\n--- DEPENSES ---\n")
    df_exp.to_csv(output, index=False, sep=";")
    return output.getvalue().encode('utf-8')

# --- MAIN ---
def main():
    load_data()

    st.title("📊 Calculatrice Budgétaire & Analyse")
    st.caption("Remplissez vos montants pour voir apparaître l'analyse de votre situation.")

    # 1. Préparer les données avec les pourcentages à jour
    # On recalcule les poids AVANT d'afficher le tableau
    st.session_state.df_expenses = calculate_weights(st.session_state.df_expenses)

    col1, col2 = st.columns([1.3, 1], gap="large")

    with col1:
        st.subheader("💸 Vos Dépenses")
        st.info("💡 Identifiez les barres rouges les plus longues : ce sont vos postes prioritaires.")
        
        # Le tableau magique avec la colonne Poids
        edited_expenses = st.data_editor(
            st.session_state.df_expenses,
            column_config={
                "Mensuel": st.column_config.NumberColumn(
                    "Montant (€)",
                    min_value=0,
                    step=10,
                    format="%.0f €",
                    width="small"
                ),
                "Poids": st.column_config.ProgressColumn(
                    "Poids dans le budget",
                    help="Ce que cette dépense représente par rapport au total des dépenses",
                    format="%.1f %%", # Affiche en pourcentage
                    min_value=0,
                    max_value=1,     # 1 = 100%
                    width="medium"
                ),
                "Catégorie": st.column_config.TextColumn("Catégorie", disabled=True, width="small"),
                "Poste": st.column_config.TextColumn("Poste", disabled=True),
            },
            hide_index=True,
            use_container_width=True,
            num_rows="fixed",
            key="editor_expenses"
        )
        
        # Mise à jour du state avec les nouvelles valeurs entrées par l'utilisateur
        # IMPORTANT : On ne garde que les colonnes originales pour éviter de dupliquer la colonne Poids au prochain tour
        st.session_state.df_expenses = edited_expenses[["Catégorie", "Poste", "Mensuel"]]
        
        total_exp = edited_expenses["Mensuel"].sum()

    with col2:
        st.subheader("💰 Vos Revenus")
        
        edited_income = st.data_editor(
            st.session_state.df_income,
            column_config={
                "Mensuel": st.column_config.NumberColumn(
                    "Montant (€)",
                    min_value=0,
                    step=10,
                    format="%.0f €"
                ),
                "Type": st.column_config.TextColumn("Type", disabled=True),
                "Source": st.column_config.TextColumn("Source", disabled=True),
            },
            hide_index=True,
            use_container_width=True,
            num_rows="fixed",
            key="editor_income"
        )
        st.session_state.df_income = edited_income
        total_inc = edited_income["Mensuel"].sum()

        # --- CARTES DE SYNTHÈSE ---
        st.markdown("---")
        st.write("### 🏁 Résultat Immédiat")
        
        cashflow = total_inc - total_exp
        
        # Affichage dynamique des métriques
        m1, m2 = st.columns(2)
        m1.metric("Total Dépenses", f"{total_exp:,.0f} €")
        m2.metric("Total Revenus", f"{total_inc:,.0f} €")
        
        st.metric("Reste à vivre (Mensuel)", f"{cashflow:,.2f} €", 
                 delta="⚠️ DANGER" if cashflow < 0 else "✅ SAIN",
                 delta_color="inverse" if cashflow < 0 else "normal")

    # --- SECTION COACHING ---
    st.markdown("---")
    st.header("🧠 L'Analyse du Coach")

    if total_exp > 0:
        # Trouver la plus grosse dépense
        max_expense = edited_expenses.loc[edited_expenses["Mensuel"].idxmax()]
        max_cat = max_expense["Catégorie"]
        max_poste = max_expense["Poste"]
        max_val = max_expense["Mensuel"]
        max_pct = (max_val / total_exp) * 100

        col_coach1, col_coach2 = st.columns([2, 1])
        
        with col_coach1:
            if cashflow < 0:
                st.error(f"🚨 **Vous dépensez plus que vous ne gagnez (-{abs(cashflow):.0f} €)**")
                st.markdown(f"""
                Votre poste le plus lourd est **{max_poste}** ({max_pct:.1f}% du total).
                
                **Conseils d'urgence :**
                1. Regardez la colonne **'Poids dans le budget'** ci-dessus. Tout ce qui dépasse 10-15% (hors loyer) est une cible.
                2. Si vos dépenses contraintes (Loyer + Crédits) dépassent 35% de vos revenus, vous êtes en zone de risque.
                3. Coupez les abonnements inutiles immédiatement.
                """)
            else:
                st.success("✅ **Votre budget est maîtrisé**")
                st.markdown(f"""
                Vous avez un excédent de **{cashflow:.0f} €** par mois.
                C'est excellent ! Même si **{max_poste}** représente {max_pct:.1f}% de vos dépenses, vous arrivez à épargner.
                
                **Prochaine étape :** Virez automatiquement ces {cashflow:.0f} € vers un compte d'épargne dès le début du mois.
                """)

        with col_coach2:
            # Petit graphique camembert simplifié
            fig = px.pie(edited_expenses, values='Mensuel', names='Catégorie', 
                         title='Où part votre argent ?',
                         hole=0.4)
            fig.update_layout(margin=dict(t=30, b=0, l=0, r=0), height=250)
            st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("👈 Commencez par entrer un montant dans les dépenses à gauche.")

    # --- EXPORT ---
    st.markdown("---")
    csv_data = convert_df_to_csv(edited_income, edited_expenses, cashflow, cashflow*12)
    st.download_button("📥 Télécharger mon analyse (CSV)", data=csv_data, file_name="mon_analyse_budget.csv", mime="text/csv")

if __name__ == "__main__":
    main()
