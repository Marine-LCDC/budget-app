import streamlit as st
import pandas as pd
import plotly.express as px
import io

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Mon Simulateur Budgétaire",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLE CSS PERSONNALISÉ (Pour faire "Pro" dans l'iframe Systeme.io) ---
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .block-container {padding-top: 2rem; padding-bottom: 2rem;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- DONNÉES INITIALES (Basées sur votre CSV) ---
# Nous définissons ici les catégories par défaut pour que l'utilisateur n'ait plus qu'à remplir
DEFAULT_EXPENSES = [
    {"Catégorie": "Foyer", "Poste": "Loyer résidence principale", "Mensuel": 0.0},
    {"Catégorie": "Foyer", "Poste": "Assurance Habitation", "Mensuel": 0.0},
    {"Catégorie": "Foyer", "Poste": "Electricité / Eau", "Mensuel": 0.0},
    {"Catégorie": "Foyer", "Poste": "Télécommunication (Internet/Mobile)", "Mensuel": 0.0},
    {"Catégorie": "Vie Courante", "Poste": "Dépenses alimentaires", "Mensuel": 0.0},
    {"Catégorie": "Vie Courante", "Poste": "Dépenses vestimentaires", "Mensuel": 0.0},
    {"Catégorie": "Vie Courante", "Poste": "Entretien (ménage, jardin)", "Mensuel": 0.0},
    {"Catégorie": "Enfants", "Poste": "Scolarité / Garde", "Mensuel": 0.0},
    {"Catégorie": "Loisirs", "Poste": "Sport / Musique", "Mensuel": 0.0},
    {"Catégorie": "Loisirs", "Poste": "Ciné / Restaurant / Bar", "Mensuel": 0.0},
    {"Catégorie": "Loisirs", "Poste": "Voyages / Vacances (lissé au mois)", "Mensuel": 0.0},
    {"Catégorie": "Loisirs", "Poste": "Addiction (Cigarette, Jeux...)", "Mensuel": 0.0},
    {"Catégorie": "Transport", "Poste": "Entretien véhicule / Carburant", "Mensuel": 0.0},
    {"Catégorie": "Transport", "Poste": "Abonnements / Assurance Auto", "Mensuel": 0.0},
    {"Catégorie": "Animaux", "Poste": "Alimentation / Véto", "Mensuel": 0.0},
    {"Catégorie": "Banque & Impôts", "Poste": "Remboursement Prêts Immo", "Mensuel": 0.0},
    {"Catégorie": "Banque & Impôts", "Poste": "Impôt sur le revenu (mensualisé)", "Mensuel": 0.0},
    {"Catégorie": "Banque & Impôts", "Poste": "Taxes locales (Foncière/Habitation)", "Mensuel": 0.0},
]

DEFAULT_INCOME = [
    {"Type": "Travail", "Source": "Salaires (Net)", "Mensuel": 0.0},
    {"Type": "Travail", "Source": "Bénéfices (BIC/BNC/BA)", "Mensuel": 0.0},
    {"Type": "Travail", "Source": "Indemnités / Primes", "Mensuel": 0.0},
    {"Type": "Patrimoine", "Source": "Revenus Fonciers (Loyers perçus)", "Mensuel": 0.0},
    {"Type": "Patrimoine", "Source": "Dividendes / Intérêts", "Mensuel": 0.0},
    {"Type": "Aides & Divers", "Source": "Pensions (Retraite/Alimentaire)", "Mensuel": 0.0},
    {"Type": "Aides & Divers", "Source": "Aides de l'Etat (CAF, APL, Chômage)", "Mensuel": 0.0},
    {"Type": "Aides & Divers", "Source": "Autres revenus", "Mensuel": 0.0},
]

# --- FONCTIONS UTILITAIRES ---
def load_data():
    """Initialise les données dans la session si elles n'existent pas encore."""
    if 'df_expenses' not in st.session_state:
        st.session_state.df_expenses = pd.DataFrame(DEFAULT_EXPENSES)
    if 'df_income' not in st.session_state:
        st.session_state.df_income = pd.DataFrame(DEFAULT_INCOME)

def calculate_totals(df):
    """Calcule les totaux mensuels et annuels."""
    total_monthly = df["Mensuel"].sum()
    total_annual = total_monthly * 12
    return total_monthly, total_annual

def convert_df_to_csv(df_inc, df_exp, balance_m, balance_a):
    """Prépare un fichier CSV pour l'export complet."""
    output = io.StringIO()
    output.write("--- RAPPORT BUDGETAIRE ---\n\n")
    output.write(f"Trésorerie Mensuelle Nette;{balance_m}\n")
    output.write(f"Trésorerie Annuelle Nette;{balance_a}\n\n")
    
    output.write("--- REVENUS ---\n")
    df_inc.to_csv(output, index=False, sep=";")
    
    output.write("\n--- DEPENSES ---\n")
    df_exp.to_csv(output, index=False, sep=";")
    
    return output.getvalue().encode('utf-8')

# --- MAIN APP ---
def main():
    load_data()

    st.title("📊 Mon Tableau de Bord Budgétaire")
    st.markdown("Remplissez les cases ci-dessous pour analyser votre situation financière.")

    # --- SECTION DE SAISIE (Layout 2 colonnes) ---
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.subheader("💸 Vos Dépenses")
        st.info("Double-cliquez sur les montants pour les modifier.")
        
        # Éditeur de données interactif pour les Dépenses
        edited_expenses = st.data_editor(
            st.session_state.df_expenses,
            column_config={
                "Mensuel": st.column_config.NumberColumn(
                    "Montant Mensuel (€)",
                    help="Entrez le coût mensuel estimé",
                    min_value=0,
                    format="%.2f €"
                ),
                "Catégorie": st.column_config.TextColumn("Catégorie", disabled=True),
                "Poste": st.column_config.TextColumn("Poste de dépense", disabled=True),
            },
            hide_index=True,
            use_container_width=True,
            key="editor_expenses"
        )
        # Calcul en temps réel
        total_exp_m, total_exp_a = calculate_totals(edited_expenses)
        st.metric(label="Total Dépenses / Mois", value=f"{total_exp_m:,.2f} €", delta=f"-{total_exp_a:,.2f} € / an", delta_color="inverse")

    with col2:
        st.subheader("💰 Vos Revenus")
        st.info("Indiquez vos rentrées d'argent nettes.")
        
        # Éditeur de données interactif pour les Revenus
        edited_income = st.data_editor(
            st.session_state.df_income,
            column_config={
                "Mensuel": st.column_config.NumberColumn(
                    "Montant Mensuel (€)",
                    help="Entrez le revenu mensuel net",
                    min_value=0,
                    format="%.2f €"
                ),
                "Type": st.column_config.TextColumn("Type", disabled=True),
                "Source": st.column_config.TextColumn("Source de revenu", disabled=True),
            },
            hide_index=True,
            use_container_width=True,
            key="editor_income"
        )
        # Calcul en temps réel
        total_inc_m, total_inc_a = calculate_totals(edited_income)
        st.metric(label="Total Revenus / Mois", value=f"{total_inc_m:,.2f} €", delta=f"+{total_inc_a:,.2f} € / an")

    st.markdown("---")

    # --- SECTION RÉSULTATS (KPIs & Coach) ---
    
    # Calcul du Reste à Vivre (Trésorerie)
    cashflow_m = total_inc_m - total_exp_m
    cashflow_a = total_inc_a - total_exp_a

    st.header("🎯 Analyse & Coaching")
    
    kpi1, kpi2, kpi3 = st.columns(3)
    
    kpi1.metric("Revenus Totaux", f"{total_inc_m:,.2f} €")
    kpi2.metric("Dépenses Totales", f"{total_exp_m:,.2f} €")
    kpi3.metric("Reste à vivre (Cashflow)", f"{cashflow_m:,.2f} €", delta=f"{'Positif' if cashflow_m >= 0 else 'Négatif'}", delta_color="normal")

    # --- LE COACH VIRTUEL (Logique du fichier Excel) ---
    st.write("### 🧠 L'avis du Coach")
    
    if cashflow_m < 0:
        st.error(f"⚠️ **Attention : Trésorerie Négative (-{abs(cashflow_m):.2f} €)**")
        st.markdown("""
        Votre budget est en déséquilibre. Voici les actions recommandées :
        1. **Réduire les frais variables** : Vérifiez les postes 'Loisirs', 'Addiction' ou 'Abonnements' dans le tableau de gauche.
        2. **Optimiser** : Pouvez-vous renégocier vos contrats (Assurance, Internet) ?
        3. **Augmenter les revenus** : Envisagez des revenus complémentaires si la réduction des coûts n'est pas suffisante.
        """)
    elif cashflow_m == 0:
        st.warning("⚖️ **Budget à l'équilibre (0 €)**")
        st.markdown("Vous ne perdez pas d'argent, mais vous n'épargnez pas. Essayez de dégager une petite marge de sécurité pour les imprévus.")
    else:
        st.success(f"✅ **Bravo : Capacité d'épargne (+{cashflow_m:.2f} €/mois)**")
        st.markdown(f"""
        Votre trésorerie est saine. Vous disposez de **{cashflow_a:,.2f} € par an** pour avancer.
        **Suggestions pour cet excédent :**
        * **Épargne de précaution :** Avez-vous 3 à 6 mois de dépenses de côté ?
        * **Investissement :** Immo, Bourse ou Crypto selon votre profil de risque.
        * **Remboursement anticipé :** Avez-vous des crédits à taux élevé à solder ?
        """)

    # --- VISUALISATION ---
    st.markdown("---")
    viz_col1, viz_col2 = st.columns(2)
    
    with viz_col1:
        st.subheader("Répartition des Dépenses")
        if total_exp_m > 0:
            # Regrouper par Catégorie pour le graphique
            fig_pie = px.pie(edited_expenses, values='Mensuel', names='Catégorie', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Remplissez vos dépenses pour voir le graphique.")

    with viz_col2:
        st.subheader("Jauge de Santé Financière")
        # Simple bar chart comparatif
        data_bar = pd.DataFrame({
            "Type": ["Dépenses", "Revenus"],
            "Montant": [total_exp_m, total_inc_m]
        })
        fig_bar = px.bar(data_bar, x="Montant", y="Type", orientation='h', color="Type", 
                         color_discrete_map={"Dépenses": "#EF553B", "Revenus": "#00CC96"})
        st.plotly_chart(fig_bar, use_container_width=True)

    # --- EXPORT ---
    st.markdown("---")
    st.subheader("💾 Sauvegarder votre travail")
    st.markdown("Téléchargez votre budget pour le conserver sur votre ordinateur.")
    
    csv_data = convert_df_to_csv(edited_income, edited_expenses, cashflow_m, cashflow_a)
    
    st.download_button(
        label="📥 Télécharger mon Budget (CSV)",
        data=csv_data,
        file_name="mon_budget_simulateur.csv",
        mime="text/csv",
    )

if __name__ == "__main__":
    main()
