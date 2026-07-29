# 🌍 Tableau de Bord d'Intelligence Économique Mondiale

Une plateforme interactive et bilingue pour explorer l'environnement macroéconomique et stratégique de **217 pays**, de **2010 à 2024** — structurée autour du cadre **PESTEL** et alimentée par **58 indicateurs réels de la Banque Mondiale**.

<p align="left">
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white" alt="Streamlit" />
  <img src="https://img.shields.io/badge/Plotly-3F4F75?style=flat&logo=plotly&logoColor=white" alt="Plotly" />
  <img src="https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas&logoColor=white" alt="Pandas" />
  <img src="https://img.shields.io/badge/NumPy-013243?style=flat&logo=numpy&logoColor=white" alt="NumPy" />
  <img src="https://img.shields.io/badge/World%20Bank%20API-0072BC?style=flat" alt="World Bank API" />
  <img src="https://img.shields.io/badge/Licence-MIT-green?style=flat" alt="Licence MIT" />
</p>

## 🚀 Lien de l'appli

***Cliquez sur ce bouton pour lancer l'application***

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://world-bi-dashboard.streamlit.app/)

---

## Aperçu

![alt text](image-1.png)

## Pourquoi ce tableau de bord ?

La plupart des outils macroéconomiques disponibles en libre accès vous obligent à choisir entre l'étendue (beaucoup de pays, peu d'indicateurs) et la profondeur (analyses riches, un seul pays à la fois). Ce tableau de bord fait les deux.

Il combine **58 indicateurs de la Banque Mondiale** couvrant toutes les dimensions PESTEL, des données issues de l'API officielle de la Banque Mondiale, et un ensemble de visualisations conçues pour l'analyse stratégique — le tout dans une interface bilingue, aussi efficace pour une recherche rapide sur un pays que pour une étude comparative rigoureuse.

## Fonctionnalités

### 🗺️ Carte mondiale

- Basculez entre **carte choroplèthe** (pays colorés) et **carte à bulles** (cercles proportionnels) pour n'importe lequel des 58 indicateurs
- Échelle logarithmique pour le PIB par habitant — chaque groupe de revenu est visuellement distinguable, pas seulement les extrêmes
- Rognage par percentile pour un meilleur contraste sur les distributions asymétriques
- Cartes de médiane régionale affichées directement sous la carte

### 📈 Tendances et corrélations

- Séries temporelles groupées par **région** ou **groupe de revenu** (2010–2024)
- Lignes verticales annotées pour le **COVID-19 (2020)** et la **vague d'inflation de 2022**
- **Scatter OLS** entre deux indicateurs quelconques, avec taille des bulles proportionnelle au poids économique
- Bandeau contextuel par indicateur expliquant ce que le chiffre signifie et comment l'interpréter

### 🔎 Profil pays

Le module le plus complet. Pour chacun des 217 pays :

- **Carte géographique** avec zoom automatique centré sur le pays sélectionné, mis en évidence dans la couleur de son groupe de revenu
- **Radar PESTEL** sur 6 piliers — avec les indicateurs inverses (inflation, dette, chômage…) automatiquement inversés pour que le radar se lise toujours "vers l'extérieur = meilleur"
- **Graphique double axe PIB vs Inflation** — production économique et pression sur les prix sur la même chronologie
- **Graphique en aires empilées 100%** de l'évolution sectorielle (Agriculture / Industrie / Services) dans le temps
- **Waterfall balance commerciale** — exportations et importations côte à côte, solde net clairement affiché
- **Heatmap normalisée sur 10 ans** — tous les indicateurs disponibles de la dernière décennie, standardisés (z-score) par colonne pour faire ressortir les performances relatives
- **Donut sectoriel** pour la dernière année disponible
- **Cartes KPI** avec variations annuelles, comparaison à la médiane mondiale et interprétation dynamique en langage naturel (ex. : « IDH : très élevé », « au-dessus de la médiane mondiale (défavorable) »)
- **Infobulles** sur chaque carte KPI avec définition bilingue statique et conseil de lecture

### ↔️ Comparaison de pays

- Sélection jusqu'à **12 pays** simultanément
- Graphique temporel en courbes, histogramme de classement et tableau de synthèse avec variations annuelles
- Fonctionne pour n'importe lequel des 58 indicateurs disponibles

### 🏗️ Structure économique

- **Treemap** de la composition sectorielle (Agriculture / Industrie / Services) par région et groupe de revenu
- **Violin plot** de la distribution du PIB par habitant (échelle log) — montre la dispersion, les concentrations et les valeurs aberrantes par groupe de revenu
- **Classement Top 10 / Bottom 10** pour n'importe quel indicateur
- **Graphique animé** de l'évolution sectorielle par région dans le temps

### 📋 Explorateur de données

- Jeu de données complet navigable avec filtres
- Mise en forme conditionnelle null-safe, avec dégradés de couleurs sémantiquement corrects : vert = mieux, rouge = pire, les indicateurs inverses sont automatiquement gérés
- **Export CSV** en un clic de n'importe quelle vue filtrée

## Cadre PESTEL

Les 58 indicateurs sont organisés en six dimensions stratégiques utilisées dans l'analyse de l'environnement macroéconomique et concurrentiel.

| Pilier | # | Exemples d'indicateurs |
|---|---|---|
| **Politique** | 4 | Dépenses militaires (% PIB & % budget), Efficacité gouvernementale (WGI), Stabilité politique (WGI) |
| **Économique** | 20 | PIB, PIB/hab. (USD & PPA), Croissance, Inflation, Dette publique, Ouverture commerciale, IDE, Compte courant, Transferts, Réserves de change, Valeur ajoutée sectorielle |
| **Social** | 16 | Population, Espérance de vie, IDH, Indice de Gini, Chômage, Chômage des jeunes, Alphabétisation, Mortalité infantile, Fécondité, Assainissement, Dépenses de santé et d'éducation |
| **Technologique** | 7 | Dépenses R&D, Chercheurs/million, Exportations haute technologie, Utilisateurs internet, Abonnements mobiles et haut débit, Détention d'un compte bancaire |
| **Environnemental** | 4 | Pollution PM2,5, Accès à l'électricité, Pertes en réseau, Rendement céréalier |
| **Légal & Gouvernance** | 7 | Contrôle de la corruption, État de droit, Qualité réglementaire, Voix et responsabilité (tous WGI), IPC (Transparency Intl.), Score de transparence, Femmes au parlement |

> **Indicateurs inverses** — pour lesquels une valeur élevée est défavorable (inflation, dette, PM2,5, chômage…) — sont gérés automatiquement dans toute l'application : inversés dans le radar PESTEL, colorés avec une échelle « plus élevé = pire » et classés dans le bon sens.

## Structure du projet

```
world-economic-dashboard/
├── __pycache__/                    # Cache Python (généré automatiquement)
│   ├── app.cpython-313.pyc
│   └── translations.cpython-313.pyc
│
├── .streamlit/                     # Configuration Streamlit
│   ── config.toml                 # Thème et paramètres de l'app
│
├── assets/                         # Ressources statiques (CSS, HTML)
│   ├── _kpi_hover_en.html          # Template tooltip EN (généré)
│   ├── _kpi_hover_fr.html          # Template tooltip FR (généré)
│   └── style.css                   # Feuille de style personnalisée
│
├── data/                           # Données et scripts de collecte
│   ├── fetch_data.py               # Script de collecte API Banque Mondiale
│   └── world_economic.csv          # Dataset agrégé (217 pays × 2010-2024)
│
├── .gitignore                      # Fichiers à ignorer par Git
├── app.py                          # Application Streamlit principale
├── translations.py                 # Dictionnaire de traductions EN/FR
├── requirements.txt                # Dépendances Python
├── README-en-us.md                 # Documentation anglaise
└── README-fr.md                    # Ce fichier, Documentation française
```

## Sources des données

| Source | Couverture | Accès |
|---|---|---|
| [Banque Mondiale — World Development Indicators (WDI)](https://databank.worldbank.org/source/world-development-indicators) | 56 indicateurs · 217 pays · 2010–2024 | API REST gratuite (`api.worldbank.org/v2`) |
| [Our World in Data — IDH](https://ourworldindata.org/human-development-index) | Indice de développement humain | Téléchargement CSV gratuit (CC BY) |
| [Our World in Data — IPC](https://ourworldindata.org/corruption) | Indice de perception de la corruption | Téléchargement CSV gratuit (CC BY) |

Toutes les données sont ouvertes et librement accessibles. Les données de la Banque Mondiale sont utilisées selon les [conditions d'utilisation des données ouvertes de la Banque Mondiale](https://www.worldbank.org/en/about/legal/terms-of-use-for-datasets).

## Disponibilité des données & limitations

### Pourquoi certaines données sont-elles manquantes pour certains pays ?

Plusieurs facteurs expliquent les lacunes dans le dataset :

1. **Capacités statistiques nationales variables** — Les pays en développement peuvent manquer des ressources ou des infrastructures nécessaires à une collecte de données régulière et standardisée, ce qui entraîne des rapports irréguliers ou absents.
2. **Création et dissolution de pays** — Certains pays n'existaient tout simplement pas avant certaines dates. Le Soudan du Sud, par exemple, a été créé en 2011 ; les données pour les années antérieures sont structurellement absentes.
3. **Conflits et instabilité politique** — Les guerres, crises et fragilités étatiques interrompent les chaînes de collecte et de publication des données, parfois pendant plusieurs années.
4. **Délais de publication** — Les organisations internationales prennent généralement 12 à 18 mois pour valider, harmoniser et publier les données officielles. L'année civile la plus récente n'est presque jamais intégralement couverte.
5. **Couverture spécifique à certains indicateurs** — Certains indicateurs ne s'appliquent qu'à des sous-ensembles de pays : le score de transparence CPIA, par exemple, ne concerne que les pays éligibles à l'IDA ; l'indice de Gini est mesuré de façon irrégulière et avec une fréquence variable selon les pays.
6. **Différences méthodologiques** — Les pays peuvent utiliser des normes de calcul différentes qui ne sont pas directement comparables d'un pays à l'autre, conduisant à des exclusions intentionnelles lors de l'harmonisation.

Le tableau de bord affiche toutes les données disponibles de manière transparente. Les cellules manquantes sont indiquées par un marqueur neutre « None » sans mise en forme colorée, afin que les lacunes ne soient jamais confondues avec des valeurs faibles.

### Pourquoi la période d'analyse se termine-t-elle en 2024 ?

1. **Disponibilité des données** — 2024 représente les données validées les plus récentes publiées par la Banque Mondiale au moment du développement.
2. **Cycle de publication de la Banque Mondiale** — Les données sont publiées avec un décalage de 12 à 18 mois. La couverture complète des indicateurs pour 2024 ne sera pas disponible avant fin 2025 ou 2026, selon l'indicateur.
3. **Cohérence** — Fixer 2024 comme année de fin garantit que les 58 indicateurs disposent d'une couverture comparable et validée, plutôt que de mélanger chiffres préliminaires et définitifs.
4. **Mise à jour facile** — Le script `fetch_data.py` peut être relancé à tout moment.

> **Note :** Un bouton **Rafraîchir depuis l'API** est disponible dans la barre latérale du tableau de bord. Un seul appel met à jour les 58 indicateurs pour les 217 pays en une seule passe.

## Cas d'utilisation

- **Business Intelligence** — scoring de risque pays, évaluation d'entrée sur un marché
- **Planification stratégique** — analyse environnementale PESTEL pour tout pays ou région
- **Benchmarking pays** — comparaison côte à côte de jusqu'à 12 pays
- **Recherche académique** — 15 ans de données World Bank harmonisées, exportables en CSV
- **Intelligence économique** — suivi des tendances macroéconomiques dans les marchés émergents
- **Analyse des politiques publiques** — monitoring des indicateurs de gouvernance, développement et durabilité
- **Enseignement** — exploration interactive des données économiques mondiales

## Auteur

**Maxime NDACLEU** — Data Analyst & Business Intelligence Analyst

[![GitHub](https://img.shields.io/badge/GitHub-maxin--dac-181717?style=flat&logo=github&logoColor=white)](https://github.com/maxin-dac)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-maximendacleu-0A66C2?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/maximendacleu)

---

## Licence

Distribué sous **licence MIT**.
Données fournies par la **Banque Mondiale** (licence Open Data) et **Our World in Data** (CC BY).
