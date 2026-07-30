# 🌍 Tableau de Bord d'Intelligence Économique Mondiale

Une plateforme interactive et bilingue pour explorer l'environnement macroéconomique et stratégique de **217 pays**, de **2000 à 2024** — structurée autour du cadre **PESTEL** et alimentée par **58 indicateurs réels de la Banque Mondiale**.

<p align="left">
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white" alt="Streamlit" />
  <img src="https://img.shields.io/badge/Plotly-3F4F75?style=flat&logo=plotly&logoColor=white" alt="Plotly" />
  <img src="https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas&logoColor=white" alt="Pandas" />
  <img src="https://img.shields.io/badge/NumPy-013243?style=flat&logo=numpy&logoColor=white" alt="NumPy" />
  <img src="https://img.shields.io/badge/World%20Bank%20API-0072BC?style=flat" alt="World Bank API" />
  <img src="https://img.shields.io/badge/Licence-MIT-green?style=flat" alt="Licence MIT" />
</p>

***Cliquez sur le bouton ci-dessous pour lancer l'application***
<p align="left">
  <a href="https://world-bi-dashboard.streamlit.app/">
    <img src="https://img.shields.io/badge/D%C3%A9mo%20en%20ligne-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Démo en ligne" />
  </a>
</p>

> 🇬🇧 **Version anglaise :** [README-en-us.md](README-en-us.md)

---

## Aperçu

![alt text](image.png)

## Pourquoi ce tableau de bord ?

La plupart des outils macroéconomiques disponibles en libre accès vous obligent à choisir entre l'étendue (beaucoup de pays, peu d'indicateurs) et la profondeur (analyses riches, un seul pays à la fois). Ce tableau de bord fait les deux.

Il combine **58 indicateurs de la Banque Mondiale** couvrant toutes les dimensions PESTEL, des données issues de l'API officielle de la Banque Mondiale, et un ensemble de visualisations conçues pour l'analyse stratégique — le tout dans une interface bilingue, aussi efficace pour une recherche rapide sur un pays que pour une étude comparative rigoureuse. L'ensemble est réparti en **sept vues coordonnées**, de la carte mondiale jusqu'au module dédié d'intelligence investissement.

## Fonctionnalités

### 🗺️ Carte mondiale

- Basculez entre **carte choroplèthe** (pays colorés) et **carte à bulles** (cercles proportionnels) pour n'importe lequel des 58 indicateurs.
- Rognage par percentile pour un meilleur contraste sur les distributions asymétriques.
- Cartes de médiane régionale affichées directement sous la carte.

### 📈 Tendances et corrélations

- Séries temporelles groupées par **région** ou **groupe de revenu** (2000–2024).
- Lignes verticales annotées pour les chocs majeurs — crise financière de **2008**, **COVID-19 (2020)** et vague d'inflation de **2022** (affichées lorsque l'année fait partie de la plage sélectionnée).
- **Scatter OLS** entre deux indicateurs quelconques, avec taille des bulles proportionnelle au poids économique.
- Bandeau contextuel par indicateur expliquant ce que le chiffre signifie et comment l'interpréter.

### 🔎 Profil pays

Le module le plus complet. Pour chacun des 217 pays :

- **Carte géographique** avec zoom automatique centré sur le pays sélectionné, mis en évidence dans la couleur de son groupe de revenu.
- **Radar PESTEL** sur 6 piliers — avec les indicateurs inverses (inflation, dette, chômage…) automatiquement inversés pour que le radar se lise toujours « vers l'extérieur = meilleur ».
- **Graphique double axe PIB vs Inflation** — production économique et pression sur les prix sur la même chronologie.
- **Graphique en aires empilées 100 %** de l'évolution sectorielle (Agriculture / Industrie / Services) dans le temps.
- **Waterfall balance commerciale** — exportations et importations côte à côte, solde net clairement affiché.
- **Heatmap normalisée sur 10 ans** — tous les indicateurs disponibles de la dernière décennie, normalisés min-max (0–1) par colonne pour faire ressortir les performances relatives.
- **Donut sectoriel** pour la dernière année disponible.
- **Cartes KPI** avec variations annuelles, comparaison à la médiane mondiale et interprétation dynamique en langage naturel (ex. : « IDH : très élevé », « au-dessus de la médiane mondiale (défavorable) »).
- **Infobulles** sur chaque carte KPI affichant la valeur courante et l'écart à la médiane mondiale ; la **définition bilingue statique et le conseil de lecture** de chaque indicateur sont, eux, portés par les bannières contextuelles bleues.

### ↔️ Comparaison de pays

- Sélection jusqu'à **12 pays** simultanément.
- Graphique temporel en courbes, histogramme de classement et tableau de synthèse avec variations annuelles.
- Fonctionne pour n'importe lequel des 58 indicateurs disponibles.

### 🏗️ Structure économique

- **Treemap** de la composition sectorielle (Agriculture / Industrie / Services) par région et groupe de revenu.
- **Violin plot** de la distribution du PIB par habitant (échelle log) — montre la dispersion, les concentrations et les valeurs aberrantes par groupe de revenu.
- **Classement Top 10 / Bottom 10** pour n'importe quel indicateur.

### 📋 Explorateur de données

- Jeu de données complet navigable avec filtres.
- Mise en forme conditionnelle *null-safe*, avec dégradés de couleurs sémantiquement corrects : vert = mieux, rouge = pire, les indicateurs inverses sont automatiquement gérés.
- **Export CSV** en un clic de n'importe quelle vue filtrée.

### 💎 Score d'investissement — Criblage risque & opportunités

Un module d'aide à la décision qui transforme les 58 indicateurs en une lecture directement actionnable pour l'entrée sur un marché ou l'allocation de portefeuille.

- **Score d'attractivité composite (0–100)** calculé sur 8 indicateurs pondérés ; carte choroplèthe et classement **Top 10** filtrable par région et par niveau de revenu.
- **Matrice Risque / Rendement** : TCAC du PIB par habitant sur 5 ans (axe X) contre volatilité de l'inflation (axe Y), taille des bulles = PIB, quatre quadrants de type BCG (*Star / Question Mark / Cash Cow / Dog*).
- **Détecteur de signaux d'alerte** : signale les pays franchissant des seuils de risque standards, avec sévérité 🔴 /  et filtres *tous / rouges / tout signal*.
- **Shortlist d'opportunités « propres »** : Top 10 des pays les mieux notés **sans aucun drapeau rouge**, avec un focus Top 3.

**Construction du score** — 8 indicateurs pondérés, normalisés min-max par année ; les indicateurs inverses sont retournés pour que *plus élevé = plus attractif* toujours :

| Poids | Indicateur | Sens |
|---|---|---|
| 20 % | Croissance du PIB | plus élevé = meilleur |
| 20 % | Stabilité politique (WGI) | plus élevé = meilleur |
| 15 % | Contrôle de la corruption (WGI) | plus élevé = meilleur |
| 15 % | Inflation | inverse (plus faible = meilleur) |
| 10 % | Dette publique (% PIB) | inverse |
| 10 % | Ouverture commerciale | plus élevé = meilleur |
| 5 % | Accès à l'électricité | plus élevé = meilleur |
| 5 % | Utilisateurs d'Internet | plus élevé = meilleur |

**Seuils de risque** utilisés par le détecteur de signaux d'alerte :

| Signal | Seuil | Sévérité |
|---|---|---|
| Inflation | > 10 % | 🔴 |
| Dette publique | > 80 % du PIB | 🔴 |
| Chômage | > 15 % | 🔴 |
| Stabilité politique | < -1 (WGI) | 🔴 |
| Perception de la corruption | < 25 (IPC) | 🔴 |
| Inflation | 5–10 % | 🟡 |
| Dette publique | 50–80 % du PIB | 🟡 |

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

```text
world-economic-dashboard/
├── .streamlit/
│   └── config.toml                 # Thème et paramètres de l'app
├── assets/
│   └── style.css                   # Feuille de style personnalisée
├── data/
│   ├── fetch_data.py               # Script de collecte API Banque Mondiale & OWID
│   └── world_economic.csv          # Dataset agrégé (217 pays × 2000-2024)
├── .gitignore                      # Fichiers à ignorer par Git
├── app.py                          # Application Streamlit principale
├── translations.py                 # Dictionnaire de traductions EN/FR
├── requirements.txt                # Dépendances Python
├── LICENSE                         # Licence MIT
├── README.md                       # Documentation anglaise
└── README-fr.md                    # Ce fichier, documentation française
```

## Sources des données

| Source | Couverture | Accès |
|---|---|---|
| [Banque Mondiale — World Development Indicators (WDI)](https://databank.worldbank.org/source/world-development-indicators) | 56 indicateurs · 217 pays · 2000–2024 | API REST gratuite (`api.worldbank.org/v2`) |
| [Our World in Data — IDH](https://ourworldindata.org/human-development-index) | Indice de développement humain | Téléchargement CSV gratuit (CC BY) |
| [Our World in Data — IPC](https://ourworldindata.org/corruption) | Indice de perception de la corruption | Téléchargement CSV gratuit (CC BY) |

Toutes les données sont ouvertes et librement accessibles. Les données de la Banque Mondiale sont utilisées selon les [conditions d'utilisation des données ouvertes de la Banque Mondiale](https://www.worldbank.org/en/about/legal/terms-of-use-for-datasets).

## Disponibilité des données & limitations

### Pourquoi certaines données sont-elles manquantes pour certains pays ?

1. **Capacités statistiques nationales variables** — Les pays en développement peuvent manquer des ressources ou des infrastructures nécessaires à une collecte de données régulière et standardisée, ce qui entraîne des rapports irréguliers ou absents.
2. **Création et dissolution de pays** — Certains pays n'existaient tout simplement pas avant certaines dates. Le Soudan du Sud, par exemple, a été créé en 2011 ; les données pour les années antérieures sont structurellement absentes.
3. **Conflits et instabilité politique** — Les guerres, crises et fragilités étatiques interrompent les chaînes de collecte et de publication des données, parfois pendant plusieurs années.
4. **Délais de publication** — Les organisations internationales prennent généralement 12 à 18 mois pour valider, harmoniser et publier les données officielles. L'année civile la plus récente n'est presque jamais intégralement couverte.
5. **Couverture spécifique à certains indicateurs** — Certains indicateurs ne s'appliquent qu'à des sous-ensembles de pays : le score de transparence CPIA, par exemple, ne concerne que les pays éligibles à l'IDA ; l'indice de Gini est mesuré de façon irrégulière et avec une fréquence variable selon les pays.
6. **Différences méthodologiques** — Les pays peuvent utiliser des normes de calcul différentes qui ne sont pas directement comparables d'un pays à l'autre, conduisant à des exclusions intentionnelles lors de l'harmonisation.

Le tableau de bord affiche toutes les données disponibles de manière transparente. Les cellules manquantes apparaissent comme « **—** » dans les tableaux et « **N/A** » sur les cartes, avec un fond gris neutre non sémantique, afin que les lacunes ne soient jamais confondues avec des valeurs faibles.

### Pourquoi la période d'analyse se termine-t-elle en 2024 ?

1. **Disponibilité des données** — 2024 représente les données validées les plus récentes publiées par la Banque Mondiale au moment du développement.
2. **Cycle de publication de la Banque Mondiale** — Les données sont publiées avec un décalage de 12 à 18 mois. La couverture complète des indicateurs pour 2024 ne sera pas disponible avant fin 2025 ou 2026, selon l'indicateur.
3. **Cohérence** — Fixer 2024 comme année de fin garantit que les 58 indicateurs disposent d'une couverture comparable et validée, plutôt que de mélanger chiffres préliminaires et définitifs.
4. **Mise à jour facile** — Le script `fetch_data.py` peut être relancé à tout moment.

> **Note :** Un bouton **Rafraîchir depuis l'API** est disponible dans la barre latérale du tableau de bord. Un seul appel met à jour les 58 indicateurs pour les 217 pays en une seule passe.

## Limites méthodologiques & positionnement

Le module **Score d'investissement** est un outil de **criblage de premier niveau**, pas un indice d'attractivité validé économétriquement. Il sert à dégrossir un shortlist de pays à creuser, pas à trancher une décision d'allocation. À interpréter comme une grille de lecture, dont les limites sont assumées :

- **Pondérations non validées** — les poids du score composite (20/20/15/15/10/10/5/5) sont des choix d'analyste, non calibrés contre une référence externe (flux d'IDE réels, spreads souverains).
- **Normalisation min-max sensible aux extrêmes** — un cas d'hyperinflation (Venezuela, Zimbabwe) écrase l'échelle pour les autres pays ; les économies « normales » sont peu différenciées au milieu du classement.
- **Redondance des indicateurs** — PIB/hab, accès à l'électricité, pénétration d'Internet et croissance sont fortement corrélés ; le score récompense en partie plusieurs fois le même niveau de développement.
- **« Rendement » = croissance passée** — le TCAC sur 5 ans mesure une dynamique passée, sensible à l'année de départ (effet rebond post-2020), et non un rendement futur d'investissement.
- **Risque partiellement capturé** — la matrice risque/rendement ne modélise que la volatilité de l'inflation ; le risque politique, de change et de défaut souverain ne sont pas intégrés (le radar PESTEL et les signaux d'alerte complètent partiellement).
- **Seuil de dette binaire** — le drapeau « dette > 80 % du PIB » signale aussi des pays développés très sûrs (Japon, États-Unis, France), dont la dette n'a pas la même signification que celle d'un émergent endetté en devises.
- **Biais de données manquantes** — les pays les plus fragiles ont souvent des indicateurs de gouvernance lacunaires, ce qui peut les exclure du score ou biaiser le classement vers les pays disposant de bonnes données.
- **Absence de contexte institutionnel/légal** — l'état de droit, l'exécution des contrats et l'indépendance judiciaire ne sont pas capturés, alors qu'ils sont cruciaux pour les investisseurs.
- **Instantané statique** — la logique de drapeau rouge est déterministe ; elle ne modélise pas de seuils conditionnels ni d'interactions entre indicateurs.

**Positionnement.** Les outils existants se répartissent entre bibliothèques de données gratuites mais en silo (Banque Mondiale, Our World in Data) et indices d'attractivité propriétaires, fermés et mono-angle. Ce projet se place à leur intersection : un outil **open source et bilingue** qui structure des indicateurs publics selon le cadre PESTEL et y ajoute une couche d'aide à la décision — gratuit et personnalisable, à utiliser en amont d'une étude de risque approfondie.

## Auteur

**Maxime NDACLEU** — Data Analyst & Business Intelligence Analyst

<p>
  <a href="https://github.com/maxin-dac"><img src="https://img.shields.io/badge/GitHub-maxin--dac-181717?style=flat&logo=github&logoColor=white" alt="GitHub" /></a>
  <a href="https://www.linkedin.com/in/maximendacleu"><img src="https://img.shields.io/badge/LinkedIn-maximendacleu-0A66C2?style=flat&logo=linkedin&logoColor=white" alt="LinkedIn" /></a>
</p>



---

## Licence

Distribué sous **licence MIT** (voir [LICENSE](LICENSE)).
Données fournies par la **Banque Mondiale** (licence Open Data) et **Our World in Data** (CC BY).
