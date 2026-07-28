# 🌍 World Economic Intelligence Dashboard

Une plateforme bilingue interactive permettant d'explorer, d'analyser et d'évaluer l'environnement macroéconomique de **217 pays**, sur la période **2000 à 2024**.

<p align="left">
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white" alt="Streamlit" />
  <img src="https://img.shields.io/badge/Plotly-3F4F75?style=flat&logo=plotly&logoColor=white" alt="Plotly" />
  <img src="https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas&logoColor=white" alt="Pandas" />
  <img src="https://img.shields.io/badge/NumPy-013243?style=flat&logo=numpy&logoColor=white" alt="NumPy" />
  <img src="https://img.shields.io/badge/statsmodels-6A5ACD?style=flat" alt="statsmodels" />
  <img src="https://img.shields.io/badge/World%20Bank%20API-0072BC?style=flat" alt="World Bank API" />
</p>

> 🇬🇧 **English version:** [README-en-us.md](README-en-us.md)

---

## Aperçu

_Ajoutez ici une capture d'écran ou un GIF animé de l'application._

---

## Fonctionnalités clés

- **Cadre d'analyse PESTEL** – Explorez **58 indicateurs de la Banque Mondiale** organisés selon six dimensions stratégiques : Politique, Économique, Social, Technologique, Environnemental et Légal & Gouvernance.
- **Cartographies mondiales interactives** – Basculez entre des cartes choroplèthes et des cartes à bulles avec des échelles de couleurs adaptées (rognage par percentile pour un meilleur contraste) afin d'identifier rapidement les disparités régionales.
- **Analyse des tendances et des corrélations** – Analysez les évolutions historiques par région ou groupe de revenu et identifiez les relations entre indicateurs grâce à une régression intégrée OLS (Ordinary Least Squares), avec annotations des événements historiques (2008, 2020, 2022).
- **Profils pays détaillés** – Accédez à une vue analytique complète pour chaque pays comprenant :
  - Une carte interactive avec zoom automatique sur le pays sélectionné
  - Un radar de performance PESTEL (les indicateurs inverses sont correctement inversés)
  - Une cascade de la balance commerciale
  - Un graphique en aires empilées 100 % de l'évolution sectorielle
  - Une carte de chaleur normalisée des indicateurs (10 dernières années)
  - Un graphique à double axe PIB vs inflation
  - Les indicateurs clés de performance (KPIs) avec variation annuelle
  - La structure sectorielle de l'économie (graphique en donut)
- **Comparaison multi-pays** – Comparez jusqu'à 12 pays simultanément sur n'importe quel indicateur disponible, avec un graphique temporel, des barres de classement et un tableau de synthèse avec variations annuelles.
- **Analyse économique structurelle** – Visualisez la contribution des secteurs (Agriculture, Industrie, Services) grâce aux Treemaps, analysez la distribution des indicateurs avec des Violin Plots et parcourez les classements Top/Bottom 10.
- **Explorateur de données interactif** – Parcourez l'ensemble du dataset grâce à des filtres avancés (année, région, pilier PESTEL), une mise en forme conditionnelle qui respecte les cellules vides, et une exportation CSV en un clic.
- **Interface entièrement bilingue** – Basculez instantanément l'ensemble de l'application — graphiques, étiquettes, légendes, infobulles et en-têtes de tableau — entre le français et l'anglais sans rechargement de la page. Les **180+ clés de traduction** sont centralisées dans un seul fichier `translations.py`, avec un validateur de parité intégré.
- **Code source 100 % en anglais** – Tous les noms de variables, commentaires, docstrings et noms de fonctions sont rédigés en anglais. Seul le texte visible par l'utilisateur est bilingue, géré via la couche de traduction.

---

## Cadre PESTEL

Le tableau de bord organise **58 indicateurs de la Banque Mondiale** selon six dimensions stratégiques couramment utilisées dans l'analyse de l'environnement macroéconomique et stratégique.

| Dimension          | Nb | Exemples d'indicateurs                                                                  |
| ------------------ | -- | --------------------------------------------------------------------------------------- |
| Politique          | 5  | Dépenses militaires, Aide publique au développement, Efficacité de l'État, Stabilité politique |
| Économique         | 18 | PIB, PIB par habitant, Croissance du PIB, Inflation, Dette, Commerce, IDE, Réserves, Valeur ajoutée sectorielle |
| Social             | 14 | Population, Chômage, Chômage des jeunes, Espérance de vie, Indice de Gini, IDH, Alphabétisation, Dépenses de santé et d'éducation |
| Technologique      | 8  | Dépenses en R&D, Demandes de brevets, Exportations de haute technologie, Accès Internet, Abonnements mobiles et fixe |
| Environnemental    | 8  | Émissions CO₂ et GES, Énergies renouvelables, Surface forestière et terres arables, Accès à l'électricité, Rendement céréalier |
| Légal & Gouvernance| 5  | Perception de la corruption (IPC), État de droit, Délais de création d'entreprise, Femmes au parlement |

> **Note :** Les indicateurs pour lesquels une valeur *élevée* est *défavorable* (inflation, dette, chômage, CO₂, etc.) sont marqués comme **indicateurs inverses**. Ils sont automatiquement inversés dans le radar PESTEL, colorés avec une échelle « élevé = défavorable » et classés dans le bon sens.

---

## Structure du projet

```text
world-economic-dashboard/
├── app.py                  # Application Streamlit principale (code anglais, interface bilingue)
├── translations.py         # Dictionnaire centralisé des traductions EN/FR (180+ clés) + validateur
├── requirements.txt        # Dépendances Python
├── data/
│   ├── world_economic.csv  # Dataset agrégé (217 pays × 2000–2024)
│   └── fetch_data.py       # Script de collecte via l'API Banque Mondiale
├── README-en-us.md         # Documentation anglaise
└── README-fr.md            # Ce fichier — documentation française
```

---

## Démarrage rapide

### 1. Cloner le dépôt

```bash
git clone https://github.com/maxin-dac/world-economic-dashboard.git
cd world-economic-dashboard
```

### 2. Créer un environnement virtuel

```bash
# Linux / macOS
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. (Optionnel) Actualiser le dataset

Le projet contient déjà un dataset prétraité dans `data/world_economic.csv`.

> **Note :** Ce fichier est généré à partir de données réelles de l'API Banque Mondiale. Les valeurs sont exactes. Pour récupérer les derniers chiffres :

```bash
python data/fetch_data.py
```

Ce script appelle directement l'API REST v2 de la Banque Mondiale (sans bibliothèque tierce), gère la pagination automatiquement et écrase `world_economic.csv`. Comptez 3 à 5 minutes pour la collecte complète (~58 indicateurs × 217 pays).

### 5. Lancer l'application

```bash
streamlit run app.py
```

Ouvrez votre navigateur à l'adresse `http://localhost:8501`.

### 6. (Optionnel) Valider les traductions

```bash
python translations.py
```

Cette commande exécute le validateur de parité intégré et signale toute clé manquante ou mal formée entre les dictionnaires anglais et français.

---

## Dépendances

| Bibliothèque | Version | Rôle                                                    |
| ------------ | ------- | ------------------------------------------------------- |
| streamlit    | ≥ 1.35  | Interface web                                           |
| plotly       | ≥ 5.20  | Graphiques et cartes                                    |
| pandas       | ≥ 2.0   | Chargement et manipulation des données                  |
| numpy        | ≥ 1.26  | Calculs numériques                                      |
| statsmodels  | ≥ 0.14  | Droites de tendance OLS dans les graphiques de dispersion |
| matplotlib   | ≥ 3.7   | Calcul des dégradés de couleur dans le tableau de données |
| requests     | ≥ 2.31  | Client HTTP pour les appels à l'API Banque Mondiale     |

Toutes les dépendances sont déclarées dans `requirements.txt` et s'installent en une seule commande `pip install -r requirements.txt`.

---

## Déploiement

L'application est entièrement configurée pour un déploiement sur **Streamlit Community Cloud**.

### Déployer en quelques étapes

1. Publiez le projet sur votre dépôt GitHub.
2. Connectez-vous à [Streamlit Community Cloud](https://share.streamlit.io).
3. Cliquez sur **New App**.
4. Sélectionnez le dépôt `maxin-dac/world-economic-dashboard`, branche `main`, fichier d'entrée `app.py`.
5. Cliquez sur **Deploy**.

Une fois déployé, votre tableau de bord sera accessible publiquement via une URL Streamlit dédiée — partageable sur LinkedIn, GitHub ou avec des clients.

---

## Vue d'ensemble du tableau de bord

| Onglet           | Contenu                                                                                      |
| ---------------- | -------------------------------------------------------------------------------------------- |
| 🗺️ Carte mondiale | Choroplèthe ou bubble map · échelle de couleur avec rognage par percentile · médianes régionales |
| 📈 Tendances     | Séries temporelles par région ou groupe de revenu · scatter OLS · annotations d'événements (2008, 2020, 2022) |
| 🔎 Profil pays   | Carte avec zoom géographique · radar PESTEL · cascade · aires 100 % · heatmap · double axe · KPIs · donut sectoriel |
| ↔️ Comparaison   | Jusqu'à 12 pays · graphique temporel · barres de classement · tableau de synthèse avec variations |
| 🏗️ Structure     | Treemap · violin plot · classement Top/Bottom 10                                             |
| 📋 Données       | Filtre PESTEL · mise en forme conditionnelle null-safe · export CSV                          |

---

## Source des données

**World Development Indicators (WDI) — Banque Mondiale Open Data**

- Endpoint API : `https://api.worldbank.org/v2/country/all/indicator/{CODE}?format=json`
- Les données sont collectées via des appels REST directs (sans bibliothèque tierce), nettoyées et sauvegardées dans `world_economic.csv`.
- Licence : [Conditions d'utilisation des données ouvertes de la Banque Mondiale](https://www.worldbank.org/en/about/legal/terms-of-use-for-datasets)

---

## Cas d'utilisation

Business Intelligence · Benchmarking pays · Analyse économique · Planification stratégique · Recherche académique · Intelligence économique · Analyse des politiques publiques · Études internationales

---

## Améliorations futures

- Recommandations pays assistées par IA
- Prévisions et analyses prédictives
- Détection d'anomalies temporelles
- Export de rapports PDF et PowerPoint
- Intégration des données OCDE et FMI
- Constructeur de tableau de bord personnalisé

---

## Auteur

**Maxime NDACLEU** — Data Analyst & Business Intelligence Analyst

- GitHub : [github.com/maxin-dac](https://github.com/maxin-dac)
- LinkedIn : [linkedin.com/in/maximendacleu](https://www.linkedin.com/in/maximendacleu)

---

## Licence

Ce projet est distribué sous la licence **MIT**. Les données utilisées sont fournies par la Banque Mondiale selon sa licence Open Data.
