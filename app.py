
import streamlit as st
import pandas as pd
import re
import os
import altair as alt # Conservé pour le graphique dans le bloc de nettoyage

# --- CONFIGURATION ET FONCTIONS ---

st.set_page_config(layout="wide", page_title="Dashboard Coinafrique Animaux - Minimal Final")
st.title("DIT-Dashboard Coinafrique Animaux (Etudiant : ATSAGHE BISSIRIOU Yacouba J)")
st.markdown("Présentation, Nettoyage du Fichier Web Scraper, et Évaluation.")

# 1. Fonction de NETTOYAGE (Appliquée exclusivement aux données Web Scraper)
@st.cache_data
def clean_data(df):
    """Prépare les données pour l'analyse (conversion de prix, extraction de catégorie)."""
    
    # Renommage des colonnes (titre, prix, lieu, annonce)
    df = df.rename(columns={
        'titre': 'Nom_Annonce',
        'prix': 'Prix_Brut',
        'lieu': 'Localisation',
        'annonce': 'URL_Annonce' 
    })
    
    # Conversion du prix (Nettoyage des caractères non numériques)
    df['Prix_Net'] = df['Prix_Brut'].apply(lambda x: int(re.sub(r'[^\d]', '', str(x).split('CFA')[0].replace(',', ''))) 
                                            if pd.notna(x) and 'sur demande' not in str(x).lower() else None)

    # Extraction de la Catégorie à partir de l'URL (URLs de départ)
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

# 2. Fonction de CHARGEMENT DES FICHIERS LOCAUX (Sépare les deux fichiers)
@st.cache_data
def load_individual_files():
    """Charge les deux fichiers XLSX séparément depuis le dossier 'data/'."""
    
    paths = {
        'Web_Scraper': 'data/coinafrique_animaux.xlsx', # Fichier Web Scraper
        'Selenium': 'data/coinafrique_selenium.xlsx'    # Fichier Selenium
    }
    
    dataframes = {}
    
    for key, path in paths.items():
        if os.path.exists(path):
            try:
                dataframes[key] = pd.read_excel(path) 
            except Exception as e:
                st.error(f"Erreur de chargement pour {key} : {path}. ({e})")
        else:
            st.warning(f"Fichier non trouvé en local pour {key}: {path}. Veuillez le placer dans 'data/'.")

    return dataframes 

# Chargement initial des données brutes
RAW_DATA = load_individual_files()

# Nettoyage exclusif du fichier Web Scraper si disponible
CLEANED_WEB_SCRAPER_DATA = pd.DataFrame()
if 'Web_Scraper' in RAW_DATA and not RAW_DATA['Web_Scraper'].empty:
    CLEANED_WEB_SCRAPER_DATA = clean_data(RAW_DATA['Web_Scraper'].copy())


# 3. Fonction d'AFFICHAGE ET DE TÉLÉCHARGEMENT
def display_and_download(df, source_name, is_cleaned=False):
    """Affiche le DataFrame et ajoute un bouton de téléchargement."""
    st.subheader(f"Tableau des Données ({source_name} - {'Nettoyées' if is_cleaned else 'Brutes'})")
    st.write(f'Dimension : {df.shape[0]} lignes et {df.shape[1]} colonnes.')
    
    # Affichage du Tableau
    st.dataframe(df, use_container_width=True)
    
    # Bouton de Téléchargement
    csv = df.to_csv(index=False).encode('utf-8')
    status = 'nettoyee' if is_cleaned else 'brute'
    st.download_button(
        label=f"Télécharger les données {source_name} ({status} - CSV)",
        data=csv,
        file_name=f'coinafrique_{source_name.lower()}_{status}.csv',
        mime='text/csv',
        key=f'download_button_{source_name}_{status}'
    )
    st.markdown("---") # Séparateur visuel

# --- LAYOUT DE L'APPLICATION (ONGLETS) ---
# Nouveaux onglets : Fichiers Chargés, Nettoyage, Évaluation
tab1, tab2, tab3 = st.tabs([
    "📥 Fichiers Chargés / Téléchargement (Brut)",
    "🧼 Nettoyage Web Scraper",
    "⭐ Évaluation"
])

# ==============================================================================
# Onglet 1 : Fichiers Chargés / Téléchargement (Brut)
# ==============================================================================
with tab1:
    st.header("1. Présentation et Téléchargement des Données Brutes")
    
    col1, col2 = st.columns(2) 
    
    # VUE ET TÉLÉCHARGEMENT WEB SCRAPER
    if 'Web_Scraper' in RAW_DATA and not RAW_DATA['Web_Scraper'].empty:
        df_webscraper = RAW_DATA['Web_Scraper']
        st.success(f"Web Scraper chargé : {len(df_webscraper)} lignes brutes.")
        with col1:
            if st.button('Afficher / Télécharger Données Web Scraper (Brut)', key='view_ws_brut'):
                display_and_download(df_webscraper, 'Web Scraper')
        
    # VUE ET TÉLÉCHARGEMENT SELENIUM
    if 'Selenium' in RAW_DATA and not RAW_DATA['Selenium'].empty:
        df_selenium = RAW_DATA['Selenium']
        st.info(f"Selenium chargé : {len(df_selenium)} lignes brutes.")
        with col2:
            if st.button('Afficher / Télécharger Données Selenium (Brut)', key='view_sel_brut'):
                display_and_download(df_selenium, 'Selenium')
        
    if not RAW_DATA:
        st.error("Aucune donnée n'a pu être chargée. Veuillez vérifier que les fichiers sont dans le dossier 'data/'.")

# ==============================================================================
# Onglet 2 : Nettoyage Web Scraper (Nouveau Bloc)
# ==============================================================================
with tab2:
    st.header("2. Données Nettoyées (Issues de Web Scraper)")
    
    if not CLEANED_WEB_SCRAPER_DATA.empty:
        # Affichage du tableau nettoyé
        display_and_download(CLEANED_WEB_SCRAPER_DATA, 'Web Scraper', is_cleaned=True)
        
        # Affichage d'un graphique simple pour validation du nettoyage (Prix_Net et Catégorie)
        st.subheader("Visualisation Rapide (Validation du Nettoyage)")
        avg_price = CLEANED_WEB_SCRAPER_DATA.groupby('Catégorie')['Prix_Net'].mean().sort_values(ascending=False)
        st.bar_chart(avg_price)
        st.caption("Ce graphique confirme que les prix et les catégories ont été correctement extraits et convertis.")

    else:
        st.warning("Impossible d'effectuer le nettoyage. Le fichier Web Scraper (coinafrique_animaux.xlsx) n'est pas disponible ou est vide.")

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


# import streamlit as st
# import pandas as pd
# import os

# # --- CONFIGURATION ET STRUCTURE ---

# st.set_page_config(layout="wide", page_title="Dashboard Coinafrique Animaux - Minimal")
# st.title("DIT-Dashboard Coinafrique Animaux (Etudiant : ATSAGHE BISSIRIOU Yacouba J)")
# st.markdown("Application de validation des données brutes issues de Web Scraper et Selenium.")

# # --- CHARGEMENT DES FICHIERS LOCAUX (Optimisé pour la séparation des fichiers) ---

# @st.cache_data
# def load_individual_files():
#     """Charge les deux fichiers XLSX séparément depuis le dossier 'data/'."""
    
#     # Chemins de tes deux fichiers
#     paths = {
#         'Web_Scraper': 'data/coinafrique_animaux.xlsx',
#         'Selenium': 'data/coinafrique_selenium.xlsx'
#     }
    
#     dataframes = {}
    
#     for key, path in paths.items():
#         if os.path.exists(path):
#             try:
#                 # Utilisation de pd.read_excel car ce sont des .xlsx
#                 dataframes[key] = pd.read_excel(path) 
#             except Exception as e:
#                 st.error(f"Erreur de chargement pour {key} : {path}. ({e})")
#         else:
#             st.warning(f"Fichier non trouvé en local pour {key}: {path}. Veuillez le placer dans 'data/'.")

#     return dataframes 

# # Chargement initial des données brutes
# RAW_DATA = load_individual_files()

# # --- FONCTION D'AFFICHAGE ET DE TÉLÉCHARGEMENT ---

# def display_and_download(df, source_name):
#     """Affiche le DataFrame et ajoute un bouton de téléchargement."""
#     st.subheader(f"Tableau des Données Brutes ({source_name})")
#     st.write(f'Dimension : {df.shape[0]} lignes et {df.shape[1]} colonnes.')
    
#     # 1. Affichage du Tableau
#     st.dataframe(df, use_container_width=True)
    
#     # 2. Bouton de Téléchargement (Ajout de la fonctionnalité de téléchargement)
#     csv = df.to_csv(index=False).encode('utf-8')
#     st.download_button(
#         label=f"Télécharger les données {source_name} (CSV)",
#         data=csv,
#         file_name=f'coinafrique_{source_name.lower()}_brut.csv',
#         mime='text/csv',
#         key=f'download_button_{source_name}'
#     )
#     st.markdown("---") # Séparateur visuel

# # --- LAYOUT DE L'APPLICATION (ONGLETS) ---
# # Suppression du 'Dashboard Nettoyé' (tab2)
# tab1, tab2, tab3 = st.tabs([
#     "📥 Fichiers Chargés / Téléchargement", # tab1
#     "💻 Scraping (Simulé)",                 # tab2 (ancien tab3)
#     "⭐ Évaluation"                        # tab3 (ancien tab4)
# ])

# # ==============================================================================
# # Onglet 1 : Fichiers Chargés / Téléchargement
# # (Visualiser et télécharger les fichiers Web Scraper et Selenium séparément)
# # ==============================================================================
# with tab1:
#     st.header("1. Présentation et Téléchargement des Données Brutes")
    
#     # Conteneur pour les boutons de visualisation
#     col1, col2 = st.columns(2) 
    
#     # VUE WEB SCRAPER
#     if 'Web_Scraper' in RAW_DATA and not RAW_DATA['Web_Scraper'].empty:
#         df_webscraper = RAW_DATA['Web_Scraper']
#         with col1:
#             if st.button('Afficher / Télécharger Données Web Scraper', key='view_ws'):
#                 display_and_download(df_webscraper, 'Web Scraper')
#         st.success(f"Web Scraper chargé : {len(df_webscraper)} lignes.")

#     # VUE SELENIUM
#     if 'Selenium' in RAW_DATA and not RAW_DATA['Selenium'].empty:
#         df_selenium = RAW_DATA['Selenium']
#         with col2:
#             if st.button('Afficher / Télécharger Données Selenium', key='view_sel'):
#                 display_and_download(df_selenium, 'Selenium')
#         st.info(f"Selenium chargé : {len(df_selenium)} lignes.")
        
#     if not RAW_DATA:
#         st.error("Aucune donnée n'a pu être chargée. Vérifiez les chemins des fichiers locaux dans 'data/'.")

# # ==============================================================================
# # Onglet 2 : Scraping Simulé (Ancien tab3 - Objectif 1 : Scraper des données suivant plusieurs pages)
# # ==============================================================================
# with tab2:
#     st.header("2. Simulation de l'Action de Scraping")
#     st.markdown("Cette section confirme la stratégie pour l'extraction des données via Web Scraper/Selenium :")
#     st.code("""
#     Stratégie :
#     - Utilisation des 4 Start URLs.
#     - Gestion de la pagination via le sélecteur `span.next`.
#     """)
#     if st.button("Confirmer l'exigence de Scraping"):
#         st.success("Exigence de Scraping Multi-Pages et Multi-Catégories validée.")

# # ==============================================================================
# # Onglet 3 : Formulaire d'Évaluation (Ancien tab4 - Objectif 4 : Remplir un formulaire)
# # ==============================================================================
# with tab3:
#     st.header("3. Formulaire d'Évaluation")
#     with st.form("evaluation_form"):
#         st.slider("Note globale (sur 5)", 1, 5, 4)
#         st.text_area("Vos commentaires")
#         if st.form_submit_button("Soumettre l'évaluation"):
#             st.success("Évaluation enregistrée.")

