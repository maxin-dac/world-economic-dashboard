# 🌍 Tableau de Bord d'Intelligence Économique Mondiale

Plateforme interactive bilingue (FR/EN) - 217 pays · 2000-2024 · 58 indicateurs Banque Mondiale structurés selon le cadre **PESTEL**, complétés d'un module dédié **Intelligence Investissement**.

<p align="left">
<img src="https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white" alt="Python" />
<img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white" alt="Streamlit" />
<img src="https://img.shields.io/badge/Plotly-3F4F75?style=flat&logo=plotly&logoColor=white" alt="Plotly" />
<img src="https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas&logoColor=white" alt="Pandas" />
<img src="https://img.shields.io/badge/NumPy-013243?style=flat&logo=numpy&logoColor=white" alt="NumPy" />
<img src="https://img.shields.io/badge/Matplotlib-11557C?style=flat&logo=matplotlib&logoColor=white" alt="Matplotlib" />
<img src="https://img.shields.io/badge/Statsmodels-4B3F72?style=flat" alt="Statsmodels" />
<img src="https://img.shields.io/badge/Requests-3776AB?style=flat&logo=python&logoColor=white" alt="Requests" />
<img src="https://img.shields.io/badge/pytest-0A9EDC?style=flat&logo=pytest&logoColor=white" alt="pytest" />
<img src="https://img.shields.io/badge/GitHub_Actions-2088FF?style=flat&logo=githubactions&logoColor=white" alt="GitHub Actions" />
<img src="https://img.shields.io/badge/HTML5-E34F26?style=flat&logo=html5&logoColor=white" alt="HTML5" />
<img src="https://img.shields.io/badge/CSS3-1572B6?style=flat&logo=css3&logoColor=white" alt="CSS3" />
<img src="https://img.shields.io/badge/API_Banque_Mondiale-0072BC?style=flat" alt="API Banque Mondiale" />
<img src="https://img.shields.io/badge/Licence_MIT-green?style=flat" alt="Licence MIT" />
</p>

<p align="left">
<a href="https://world-bi-dashboard.streamlit.app/">
<img src="https://img.shields.io/badge/D%C3%A9mo_en_ligne-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Démo en ligne" />
</a>
</p>

![Aperçu](assets/image-2.png)

> **Version anglaise :** [README.md](README.md)

## Fonctionnalités

**7 vues coordonnées** + 1 module d'investissement :

- **Carte mondiale** - choroplèthe + bulles, rognage par percentile, cartes de médiane régionale
- **Tendances & corrélations** - séries par région/revenu, lignes de chocs annotées (2008, 2020, 2022), scatter OLS
- **Profil pays** - radar PESTEL, heatmap normalisée 10 ans, double axe PIB/inflation, aires sectorielles, cascade balance commerciale, donut sectoriel
- **Comparaison pays** - jusqu'à 12 pays, séries + barres de classement + tableau synthétique
- **Structure économique** - treemap sectoriel, violin plot log du PIB/hab., Top/Bottom 10
- **Explorateur de données** - jeu filtrable, mise en forme conditionnelle null-safe, export CSV en un clic
- **Score Investissement** - score composite 0-100 (8 indicateurs pondérés), matrice risque/rendement 4 quadrants, détecteur de signaux d'alerte, shortlist d'opportunités propres

## Couverture PESTEL (58 indicateurs)

| Pilier | # | Exemples |
|---|---|---|
| Politique | 4 | Dépenses militaires, Efficacité gouvernementale, Stabilité politique (WGI) |
| Économique | 20 | PIB, PIB/hab., Croissance, Inflation, Dette publique, Ouverture commerciale, IDE, Compte courant |
| Social | 16 | Population, Espérance de vie, IDH, Gini, Chômage, Alphabétisation, Mortalité infantile |
| Technologique | 7 | R&D, Chercheurs, Exportations haute technologie, Utilisateurs internet, Abonnements mobiles |
| Environnemental | 4 | PM2,5, Accès électricité, Pertes en réseau, Rendement céréalier |
| Légal & Gouvernance | 7 | Contrôle de la corruption, État de droit, Qualité réglementaire, IPC, Score de transparence |

## Structure du projet

    world-economic-dashboard/
    ├── .github/workflows/
    │   └── update-data.yml              # Pipeline CI/CD mensuel
    ├── .streamlit/config.toml           # Thème de l'app
    ├── assets/style.css                 # Feuille de style personnalisée
    ├── data/
    │   ├── fetch_data.py                # Collecteur API Banque Mondiale
    │   └── world_economic.csv           # Dataset agrégé (217 x 2000-2024)
    ├── docs/OPERATIONS.md               # Guide d'exploitation
    ├── scripts/changelog_entry.py       # Générateur de changelog
    ├── tests/test_investment.py         # Suite pytest
    ├── CHANGELOG.md                     # Historique des rafraîchissements mensuels
    ├── app.py                           # Application Streamlit
    ├── translations.py                  # Dictionnaire EN/FR
    ├── requirements.txt                 # Dépendances
    ├── LICENSE                          # MIT
    ├── README.md                        # Documentation anglaise
    └── README-fr.md                     # Ce fichier

## Stack

**Python · Streamlit · Plotly · Pandas · NumPy · Matplotlib · Statsmodels · pytest · GitHub Actions**

Données collectées via l'**API REST de la Banque Mondiale** et **Our World in Data**, **actualisées automatiquement le premier lundi de chaque mois** via un pipeline GitHub Actions (tests, collecte, changelog, commit, redéploiement Streamlit Cloud). Déclenchement manuel possible depuis l'onglet Actions du dépôt.

## Qualité des données & limitations

- 2024 est la dernière année entièrement validée (décalage de publication Banque Mondiale de 12-18 mois)
- Cellules nulles affichées en "**-**" (tableaux) / "**N/A**" (cartes KPI) sur fond gris neutre
- Changelog mensuel traçant couverture, taux de nulls et indicateurs les moins couverts

## Auteur

**Maxime NDACLEU** - Data Analyst & Business Intelligence Analyst

<p>
<a href="https://github.com/maxin-dac"><img src="https://img.shields.io/badge/GitHub-maxin--dac-181717?style=flat&logo=github&logoColor=white" alt="GitHub" /></a>
<a href="https://www.linkedin.com/in/maximendacleu"><img src="https://img.shields.io/badge/LinkedIn-maximendacleu-0A66C2?style=flat&logo=linkedin&logoColor=white" alt="LinkedIn" /></a>
</p>

## Licence

Distribué sous **licence MIT** (voir [LICENSE](LICENSE)).
Données fournies par la **Banque Mondiale** (licence Open Data) et **Our World in Data** (CC BY).
