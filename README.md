# Plateforme de Scouting Football

## Vue d'ensemble
Ce projet est une plateforme de scouting football construite à partir des `StatsBomb Open Data` sur les `5 grands championnats européens` lors de la saison `2015/2016`.

L'objectif n'est pas seulement de produire des visualisations, mais de construire un `outil d'aide à la décision` pour des usages de `recrutement`, `analyse de profils` et `benchmark joueurs`.

Le projet combine :
- une logique `data engineering` pour structurer la donnée
- une logique `football analytics` pour construire des métriques interprétables
- une logique `produit` avec une application Dash pensée pour une lecture scouting

## Objectif métier
Cette plateforme a été pensée comme un prototype exploitable par une cellule :
- de `scouting`
- de `recrutement`
- de `performance`

Elle permet notamment de :
- filtrer des populations de joueurs
- comparer des profils
- identifier des joueurs similaires
- produire des shortlists
- générer des rapports joueurs exportables
- documenter la logique des scores pour garder un outil auditable

L'idée centrale du projet est simple :
transformer des `event data` brutes en `profils joueurs lisibles`, `comparables` et `actionnables`.

## Ce que fait le projet
Le projet couvre actuellement :
- l'ingestion des données StatsBomb Open Data
- le nettoyage et la structuration des événements de match
- l'agrégation des métriques au niveau `joueur-match` puis `joueur-saison`
- la sélection d'une `position principale` par `joueur / club / championnat`
- le calcul de métriques `par 90`
- la construction de `dimensions football` interprétables
- le calcul de `scores de rôle`
- le calcul de `joueurs similaires`
- la comparaison par `groupes de poste`
- la génération de `shortlists recrutement`
- la génération de `rapports joueurs exportables`

## Fonctionnalités principales
L'application contient plusieurs modules complémentaires :

- `Accueil`
Présentation du projet, du périmètre et de la valeur métier.

- `Méthodologie`
Explication des hypothèses, des dimensions football, des rôles et des limites du modèle.

- `Cas d'usage`
Scénarios concrets de recrutement pour montrer comment utiliser l'outil dans un besoin réel.

- `Validation`
Contrôle de cohérence entre rôles, familles de poste et lectures de similarité.

- `Scouting Lab`
Classements de joueurs selon un rôle cible avec filtres championnat, équipe, poste et minutes.

- `Shortlist`
Module orienté recrutement pour construire une shortlist et l'exporter en CSV.

- `Explorateur Joueurs`
Vue d'exploration globale des profils saison.

- `Profil Joueur`
Fiche individuelle avec dimensions, meilleurs rôles et joueurs similaires.

- `Rapport Joueur`
Synthèse exportable en HTML pour construire un cas scouting ou une fiche de travail.

- `Radar Scouting`
Comparaison percentile par groupe de poste.

- `Analyse Scatter`
Positionnement d'un joueur dans une population filtrée sur deux métriques.

## Méthodologie
Le pipeline suit les étapes suivantes :

1. ingestion des compétitions, matchs, lineups et events StatsBomb
2. nettoyage des événements et standardisation des coordonnées
3. agrégation au niveau `joueur-match`
4. agrégation au niveau `joueur-saison`
5. sélection d'une ligne principale par `joueur / club / championnat`
6. ajout des minutes et calcul des métriques `par 90`
7. construction de dimensions football standardisées
8. calcul de scores de rôle
9. calcul de similarité entre joueurs
10. calcul de percentiles par groupe de poste

### Dimensions football
Le projet repose sur 5 dimensions principales :
- `Progression du ballon`
- `Création d'occasions`
- `Impact dernier tiers`
- `Activité défensive`
- `Sécurité ballon`

Ces dimensions servent de base aux rôles et à la similarité.

### Scores de rôle
Les scores de rôle sont construits à partir de pondérations explicites sur les dimensions football.

Le projet inclut actuellement des rôles comme :
- milieu progressif
- regista
- milieu récupérateur
- meneur avancé
- ailier créatif
- ailier intérieur
- défenseur central relanceur
- défenseur central stoppeur
- latéral progressif
- avant-centre de surface

Les scores sont `contextualisés par famille de poste` pour éviter des tops incohérents hors rôle cible.

### Similarité
La similarité joueur est calculée à partir :
- des dimensions football
- des scores de rôle

Elle permet de rapprocher des profils comparables dans d'autres équipes ou championnats.

## Choix importants de modélisation
Quelques principes structurants du projet :

- une ligne centrale par `joueur / club / championnat`
- priorité à des métriques `interprétables`
- pas de modèle opaque de type “black box”
- seuil de `900 minutes` pour stabiliser une partie des lectures scouting
- validation par famille de poste pour améliorer la cohérence métier

## Limites actuelles
Le projet reste volontairement cadré et présente plusieurs limites :
- une seule saison couverte dans cette version
- pas d'ajustement par style d'équipe ou volume de possession
- pas de données physiques, contractuelles ou financières
- pas de vidéo intégrée
- les scores de rôle restent dépendants des hypothèses de pondération

Le projet doit donc être lu comme un `outil d'appui à la décision`, pas comme un système autonome de recrutement.

## Stack technique
- `Python`
- `Pandas`
- `NumPy`
- `scikit-learn`
- `Dash`
- `Plotly`
- `StatsBombPy`
- `Jupyter Notebook`

## Structure du projet
```text
football-scouting-platform/
├── app/               # application Dash
├── data/              # données brutes, intermédiaires et transformées
├── notebooks/         # notebooks d'exploration et de prototypage
├── sql/               # schéma et vues SQL
├── src/
│   ├── ingestion/     # chargement des données source
│   ├── processing/    # nettoyage et structuration
│   ├── features/      # construction des métriques et scores
│   ├── modeling/      # similarité
│   └── utils/         # utilitaires métier
├── tests/             # tests unitaires ciblés
├── main.py            # point d'entrée principal
├── requirements.txt
└── README.md
```

## Installation
Créer un environnement virtuel :

```bash
python -m venv .venv
```

Activer l'environnement :

Windows :
```bash
.venv\Scripts\activate
```

Installer les dépendances :

```bash
pip install -r requirements.txt
```

## Utilisation
### Lancer le pipeline data
Pour recalculer les tables à partir d'une étape donnée :

```bash
python main.py pipeline --stage all
```

### Lancer l'application
```bash
python main.py app --debug
```

## Vérification
Lancer les tests :

```bash
python -m unittest discover -s tests -v
```

## Ce que ce projet démontre
Ce projet met en avant :
- la capacité à structurer un pipeline data propre
- la capacité à transformer des données football en indicateurs métiers
- la capacité à concevoir un outil orienté utilisateur
- la capacité à documenter les hypothèses et les limites
- la capacité à articuler `engineering`, `analytics` et `usage terrain`

## Améliorations possibles
Axes d'évolution possibles :
- ajout d'autres saisons
- ajustements par contexte collectif
- exports plus avancés
- enrichissement de la validation football
- ajout de cas d'usage performance / match analysis
- ajout de données contractuelles ou de marché si disponibles




Projet réalisé par `Mehdi`, avec une orientation forte vers les métiers de :
- `data dans le football`
- `scouting`
- `performance`
- `recrutement`
