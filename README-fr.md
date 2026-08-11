# 🌍 Tableau de Bord d'Intelligence Économique Mondiale

Plateforme interactive bilingue (FR/EN) - 217 pays · 2000-2024 · 58 indicateurs Banque Mondiale structurés selon le cadre **PESTEL**, complétés d'un module dédié **Intelligence Investissement**.

<p align="left">
<img src="https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white" alt="Python" />
<img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white" alt="Streamlit" />
<img src="https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white" alt="Docker" />
<img src="https://img.shields.io/badge/Plotly-3F4F75?style=flat&logo=plotly&logoColor=white" alt="Plotly" />
<img src="https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas&logoColor=white" alt="Pandas" />
<img src="https://img.shields.io/badge/NumPy-013243?style=flat&logo=numpy&logoColor=white" alt="NumPy" />
<img src="https://img.shields.io/badge/Matplotlib-11557C?style=flat&logo=matplotlib&logoColor=white" alt="Matplotlib" />
<img src="https://img.shields.io/badge/Statsmodels-4B3F72?style=flat" alt="Statsmodels" />
<img src="https://img.shields.io/badge/pytest-0A9EDC?style=flat&logo=pytest&logoColor=white" alt="pytest" />
<img src="https://img.shields.io/badge/GitHub_Actions-2088FF?style=flat&logo=githubactions&logoColor=white" alt="GitHub Actions" />
<img src="https://img.shields.io/badge/API_Banque_Mondiale-0072BC?style=flat" alt="API Banque Mondiale" />
<img src="https://img.shields.io/badge/Licence_MIT-green?style=flat" alt="Licence MIT" />
</p>

<p align="left">
<a href="https://world-bi-dashboard.streamlit.app/">
<img src="https://img.shields.io/badge/D%C3%A9mo_en_ligne-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Démo en ligne" />
</a>
</p>

![Aperçu](static/globe.png)

> **Version anglaise :** [README.md](README.md)

## Fonctionnalités

**7 vues coordonnées** + modules d'analyse spécialisés :

- **Carte mondiale** - Choroplèthe + bulles, rognage par percentile, cartes de médiane régionale.
- **Tendances & corrélations** - Séries temporelles par région/revenu, lignes de chocs annotées (2008, 2020, 2022), scatter OLS.
- **Profil pays** - Radar PESTEL, heatmap normalisée 10 ans, double axe PIB/inflation, cascade balance commerciale.
- **Comparaison & Similarité pays** - Benchmarking multi-pays (jusqu'à 12 pays) et moteur de recherche de pays similaires.
- **Structure & Résilience économique** - Treemap sectoriel, violin plot log du PIB/hab., analyse de la résilience et des chocs.
- **Explorateur de données & Audit Qualité** - Jeu de données filtrable avec audit des données manquantes, mise en forme conditionnelle null-safe, export CSV en un clic.
- **Score Investissement** - Score composite 0-100 (8 indicateurs pondérés), matrice risque/rendement 4 quadrants, détecteur de signaux d'alerte, shortlist d'opportunités propres.

## Couverture PESTEL (58 indicateurs)

| Pilier | # | Exemples |
|---|---|---|
| Politique | 4 | Dépenses militaires, Efficacité gouvernementale, Stabilité politique (WGI) |
| Économique | 20 | PIB, PIB/hab., Croissance, Inflation, Dette publique, Ouverture commerciale, IDE, Compte courant |
| Social | 16 | Population, Espérance de vie, IDH, Gini, Chômage, Alphabétisation, Mortalité infantile |
| Technologique | 7 | R&D, Chercheurs, Exportations haute technologie, Utilisateurs internet, Abonnements mobiles |
| Environnemental | 4 | PM2,5, Accès électricité, Pertes en réseau, Rendement céréalier |
| Légal & Gouvernance | 7 | Contrôle de la corruption, État de droit, Qualité réglementaire, IPC, Score de transparence |

## Architecture du Projet

```
world-economic-dashboard/
├── .github/workflows/
│   ├── lint.yml                      # Pipeline CI de contrôle de qualité du code
│   └── update-data.yml               # Pipeline CI/CD mensuel d'actualisation des données
├── .streamlit/config.toml            # Configuration du thème Streamlit
├── assets/style.css                  # Style CSS sur-mesure (Glassmorphism)
├── core/                             # Package Python modulaire principal
│   ├── __init__.py
│   ├── analytics.py                  # Calculs statistiques et transformations
│   ├── constants.py                  # Définitions PESTEL, couleurs & schémas
│   ├── data.py                       # Chargement des données et optimisation mémoire
│   ├── indicators.py                 # Moteur de calcul des indicateurs
│   ├── investment.py                 # Algorithmes de scoring d'investissement et quadrants
│   └── labels.py                     # Résolution des libellés multilingues
├── data/
│   ├── fetch_data.py                 # Script de collecte API Banque Mondiale
│   └── world_economic.csv            # Dataset agrégé (217 pays x 2000-2024)
├── docs/OPERATIONS.md                # Guide d'exploitation et maintenance
├── static/
│   └── globe.png                     # Visuels du tableau de bord
├── tests/
│   └── test_investment.py            # Suite de tests automatisés pytest
├── app.py                            # Point d'entrée de l'application Streamlit
├── dataquality.py                    # Module d'audit de qualité des données et couverture
├── exports.py                        # Moteur d'exportation de rapports et données
├── resilience.py                     # Module d'analyse de résilience économique
├── similar.py                        # Moteur d'analyse de similarité entre pays
├── translations.py                   # Dictionnaire de traduction bilingue (FR/EN)
├── Dockerfile                        # Configuration de conteneurisation Docker
├── .dockerignore                     # Rôles d'exclusion pour le build Docker
├── requirements.txt                  # Dépendances Python
├── LICENSE                           # Licence MIT
├── README.md                         # Documentation en anglais
└── README-fr.md                      # French Documentation
```

## Démarrage rapide & Installation

### Option 1 : Installation Locale

1. **Cloner le dépôt :**
   ```bash
   git clone https://github.com/maxin-dac/world-economic-dashboard.git
   cd world-economic-dashboard
   ```

2. **Installer les dépendances :**
   ```bash
   pip install -r requirements.txt
   ```

3. **Lancer l'application Streamlit :**
   ```bash
   streamlit run app.py
   ```

### Option 2 : Déploiement avec Docker

1. **Construire l'image Docker :**
   ```bash
   docker build -t world-economic-dashboard .
   ```

2. **Lancer le conteneur :**
   ```bash
   docker run -p 8501:8501 world-economic-dashboard
   ```

3. Ouvrir `http://localhost:8501` dans votre navigateur web.

## Stack & Pipeline de Données

**Python 3.12 · Streamlit · Docker · Plotly · Pandas · NumPy · Matplotlib · Statsmodels · pytest · GitHub Actions**

Les données sont collectées via l'**API REST de la Banque Mondiale** et **Our World in Data**, puis **actualisées automatiquement le premier lundi de chaque mois** via un pipeline GitHub Actions (tests, collecte, génération de changelog, commit automatique et redéploiement Streamlit Cloud).

## Qualité des données & limitations

- 2024 est la dernière année entièrement validée (décalage de publication Banque Mondiale de 12-18 mois)
- Cellules nulles affichées en "**-**" (tableaux) / "**N/A**" (cartes KPI) sur fond gris neutre
- Le module d'audit de qualité dédié surveille les taux de couverture et l'état des indicateurs

## Auteur

**Maxime NDACLEU** - Data Analyst & Business Intelligence Analyst

<p>
<a href="https://github.com/maxin-dac"><img src="https://img.shields.io/badge/GitHub-maxin--dac-181717?style=flat&logo=github&logoColor=white" alt="GitHub" /></a>
<a href="https://www.linkedin.com/in/maximendacleu"><img src="https://img.shields.io/badge/LinkedIn-maximendacleu-0A66C2?style=flat&logo=linkedin&logoColor=white" alt="LinkedIn" /></a>
</p>

## Licence

Distribué sous **licence MIT** (voir [LICENSE](LICENSE)).
Données fournies par la **Banque Mondiale** (licence Open Data) et **Our World in Data** (CC BY).
