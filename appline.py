import streamlit as st
import pandas as pd
import re
import altair as alt

# --- CONFIGURATION ET FONCTIONS ---

st.set_page_config(layout="wide", page_title="Dashboard Coinafrique - Final Déployable")
st.title("DIT-Dashboard Coinafrique Animaux (etudiant:ATSAGHE BISSIRIOU Yacouba J)")

# 1. Fonction de NETTOYAGE (Pour le Web Scraper)
@st.cache_data
def clean_data(df):
    """Prépare les données pour l'analyse (conversion de prix, extraction de catégorie)."""
    
    df = df.rename(columns={
        'titre': 'Nom_Annonce',
        'prix': 'Prix_Brut',
        'lieu': 'Localisation',
        'annonce': 'URL_Annonce' 
    })
    
    df['Prix_Net'] = df['Prix_Brut'].apply(lambda x: int(re.sub(r'[^\d]', '', str(x).split('CFA')[0].replace(',', ''))) 
                                            if pd.notna(x) and 'sur demande' not in str(x).lower() else None)

    def extract_category(url):
        if isinstance(url, str):
            if 'chiens' in url: return 'Chiens'
            if 'moutons' in url: return 'Moutons'
            if 'poules-lapins-et-pigeons' in url: return 'Volailles & Lapins'
            if 'autres-animaux' in url: return 'Autres Animaux'
        return 'Divers'
    df['Catégorie'] = df['URL_Annonce'].apply(extract_category)
    
    df.dropna(subset=['Prix_Net'], inplace=True)
    return df

# 2. Fonction de CHARGEMENT DIRECT À PARTIR DE LA RACINE
@st.cache_data
def load_files_from_root():
    """Tente de charger les deux fichiers XLSX à partir du répertoire racine du dépôt."""
    
    dataframes = {}
    
    paths = {
        'Web_Scraper': 'coinafrique_animaux.xlsx',    
        'Selenium': 'coinafrique_selenium.xlsx'      
    }
    
    for key, path in paths.items():
        try:
            # Tente de lire directement sans le préfixe 'data/'
            df_temp = pd.read_excel(path) 
            dataframes[key] = df_temp
        except Exception as e:
            st.error(f"Erreur: Impossible de charger le fichier {path} en ligne. ({e})")

    return dataframes 

# Chargement initial des données brutes
RAW_DATA = load_files_from_root()

# Nettoyage exclusif du fichier Web Scraper si disponible
CLEANED_WEB_SCRAPER_DATA = pd.DataFrame()
if 'Web_Scraper' in RAW_DATA:
    CLEANED_WEB_SCRAPER_DATA = clean_data(RAW_DATA['Web_Scraper'].copy())


# 3. Fonction d'AFFICHAGE ET DE TÉLÉCHARGEMENT
def display_and_download(df, source_name, is_cleaned=False):
    """Affiche le DataFrame et ajoute un bouton de téléchargement."""
    st.subheader(f"Tableau des Données ({source_name} - {'Nettoyées' if is_cleaned else 'Brutes'})")
    st.write(f'Dimension : {df.shape[0]} lignes et {df.shape[1]} colonnes.')
    
    st.dataframe(df, use_container_width=True)
    
    csv = df.to_csv(index=False).encode('utf-8')
    status = 'nettoyee' if is_cleaned else 'brute'
    st.download_button(
        label=f"Télécharger les données {source_name} ({status} - CSV)",
        data=csv,
        file_name=f'coinafrique_{source_name.lower()}_{status}.csv',
        mime='text/csv',
        key=f'download_button_{source_name}_{status}'
    )
    st.markdown("---") 


# --- LAYOUT DE L'APPLICATION (ONGLETS) ---
tab1, tab2, tab3 = st.tabs([
    "Fichiers Chargés / Téléchargement (Brut)",
    "Nettoyage Web Scraper",
    "Évaluation"
])

# ==============================================================================
# Onglet 1 : Fichiers Chargés / Téléchargement (Brut)
# ==============================================================================
with tab1:
    st.header("1. Présentation et Téléchargement des Données Brutes")
    
    col1, col2 = st.columns(2) 
    
    # VUE ET TÉLÉCHARGEMENT WEB SCRAPER
    if 'Web_Scraper' in RAW_DATA:
        df_webscraper = RAW_DATA['Web_Scraper']
        st.success(f"Web Scraper chargé : {len(df_webscraper)} lignes brutes.")
        with col1:
            if st.button('Afficher / Télécharger Données Web Scraper (Brut)', key='view_ws_brut'):
                display_and_download(df_webscraper, 'Web Scraper')
        
    # VUE ET TÉLÉCHARGEMENT SELENIUM
    if 'Selenium' in RAW_DATA:
        df_selenium = RAW_DATA['Selenium']
        st.info(f"Selenium chargé : {len(df_selenium)} lignes brutes.")
        with col2:
            if st.button('Afficher / Télécharger Données Selenium (Brut)', key='view_sel_brut'):
                display_and_download(df_selenium, 'Selenium')
        
    if not RAW_DATA:
        st.error("ÉCHEC: Veuillez vérifier que les fichiers .xlsx sont à la racine de votre dépôt GitHub.")

# ==============================================================================
# Onglet 2 : Nettoyage Web Scraper
# ==============================================================================
with tab2:
    st.header("2. Données Nettoyées (Issues de Web Scraper)")
    
    if not CLEANED_WEB_SCRAPER_DATA.empty:
        display_and_download(CLEANED_WEB_SCRAPER_DATA, 'Web Scraper', is_cleaned=True)
        
        st.subheader("Validation du Nettoyage : Prix Moyen par Catégorie")
        avg_price = CLEANED_WEB_SCRAPER_DATA.groupby('Catégorie')['Prix_Net'].mean().sort_values(ascending=False)
        st.bar_chart(avg_price)
    else:
        st.warning("Impossible d'effectuer le nettoyage. Le fichier Web Scraper est manquant ou n'a pas pu être chargé.")

# ==============================================================================
# Onglet 3 : Formulaire d'Évaluation (Objectif 4)
# ==============================================================================
with tab3:
    st.header("3. Formulaire d'Évaluation")
    with st.form("evaluation_form"):
        st.slider("Note globale (sur 5)", 1, 5, 4)
        st.text_area("Vos commentaires")
        if st.form_submit_button("Soumettre l'évaluation"):
            st.success("Évaluation enregistrée.")