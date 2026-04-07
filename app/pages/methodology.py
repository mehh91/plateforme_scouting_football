import dash
from dash import html

from app.utils.data_loader import load_player_group_percentiles, load_primary_player_role_scores
from app.utils.labels import DIMENSION_LABELS
from app.utils.scouting import dimension_methodology_rows
from src.utils.role_definitions import ROLE_DEFINITIONS


dash.register_page(__name__, path="/methodology", name="Méthodologie")


profile_df = load_primary_player_role_scores()
percentiles_df = load_player_group_percentiles()


method_steps = [
    "Ingestion des compétitions, matchs, lineups et événements depuis StatsBomb Open Data.",
    "Nettoyage des événements et standardisation des coordonnées terrain.",
    "Agrégation au niveau joueur-match puis joueur-saison.",
    "Sélection d'une position principale par joueur / club / championnat.",
    "Calcul des métriques par 90, des dimensions football, des scores de rôle et de la similarité.",
    "Comparaison percentile à l'intérieur des groupes de poste.",
]


assumptions = [
    "Les scores sont des aides à la décision et ne remplacent pas l'observation vidéo.",
    "Le seuil 900 minutes sert à mieux stabiliser les lectures scouting.",
    "Les dimensions sont construites à partir de z-scores sur des métriques par 90 ou de sécurité ballon.",
    "Les rôles sont contextualisés par famille de poste afin d'éviter des tops incohérents hors position cible.",
    "La similarité s'appuie sur les dimensions et les scores de rôle, pas sur une projection de valeur marchande.",
    "Les comparaisons radar scouting sont faites à l'intérieur d'un même groupe de poste.",
]


limitations = [
    "Pas d'ajustement par style d'équipe ou volume de possession dans cette version.",
    "Pas de données physiques, contractuelles, d'âge ou de valeur marchande.",
    "Une seule saison est couverte dans la version actuelle.",
    "Les rôles sont définis par des pondérations expertes et doivent être confrontés au terrain.",
]


dimension_cards = []
for row in dimension_methodology_rows():
    dimension_cards.append(
        html.Div(
            className="info-card",
            children=[
                html.Div(row["label"], className="info-card-title"),
                html.P(row["description"]),
            ],
        )
    )


role_cards = []
for _, definition in ROLE_DEFINITIONS.items():
    role_cards.append(
        html.Div(
            className="info-card",
            children=[
                html.Div(definition["label"], className="info-card-title"),
                html.P(definition["description"]),
                html.Div(
                    "Groupes cibles : " + ", ".join(definition["target_groups"]),
                    className="info-card-meta",
                ),
                html.Ul(
                    [
                        html.Li(f"{DIMENSION_LABELS.get(metric, metric)} : {weight:.0%}")
                        for metric, weight in definition["weights"].items()
                    ]
                ),
            ],
        )
    )


layout = html.Div(
    className="page-container",
    children=[
        html.H1("Méthodologie"),
        html.P(
            "Cette page explicite les choix de construction du projet afin de rendre les scores, "
            "les comparaisons et les recommandations auditables par un staff performance ou recrutement."
        ),
        html.Div(
            className="kpi-grid",
            children=[
                html.Div(className="kpi-card", children=[html.H3("Profils saison"), html.P(f"{len(profile_df)}")]),
                html.Div(
                    className="kpi-card",
                    children=[html.H3("Joueurs 900+"), html.P(f"{int((profile_df['minutes_played'] >= 900).sum())}")],
                ),
                html.Div(
                    className="kpi-card",
                    children=[html.H3("Groupes radar"), html.P(f"{percentiles_df['position_group'].nunique()}")],
                ),
                html.Div(
                    className="kpi-card",
                    children=[html.H3("Rôles modélisés"), html.P(f"{len(ROLE_DEFINITIONS)}")],
                ),
            ],
        ),
        html.Div(className="profile-card", children=[html.H2("Pipeline"), html.Ol([html.Li(step) for step in method_steps])]),
        html.Div(
            className="profile-card",
            children=[html.H2("Dimensions football"), html.Div(className="info-grid", children=dimension_cards)],
        ),
        html.Div(
            className="profile-card",
            children=[html.H2("Bibliothèque de rôles"), html.Div(className="info-grid", children=role_cards)],
        ),
        html.Div(
            className="profile-grid",
            children=[
                html.Div(
                    className="profile-card",
                    children=[html.H2("Hypothèses"), html.Ul([html.Li(item) for item in assumptions])],
                ),
                html.Div(
                    className="profile-card",
                    children=[html.H2("Limites"), html.Ul([html.Li(item) for item in limitations])],
                ),
            ],
        ),
    ],
)
