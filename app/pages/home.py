from pathlib import Path

import dash
import pandas as pd
from dash import html

from app.utils.data_loader import load_primary_player_role_scores


dash.register_page(__name__, path="/", name="Accueil")


DATA_PATH = Path("data/processed/player_role_scores.parquet")


def load_data():
    try:
        return load_primary_player_role_scores()
    except Exception:
        return pd.read_parquet(DATA_PATH)


df = load_data()

total_players = df["player"].nunique()
eligible_players = df[df["meets_minimum_minutes_900"] == 1]["player"].nunique()
total_teams = df["team"].nunique()
total_leagues = df["competition_name"].nunique()
avg_minutes = round(df["minutes_played"].mean(), 1)
avg_matches = round(df["matches_played"].mean(), 1)


layout = html.Div(
    className="page-container",
    children=[
        html.H1("Plateforme de scouting football"),
        html.P(
            "Outil d'aide à la décision construit à partir des StatsBomb Open Data "
            "sur les cinq grands championnats européens lors de la saison 2015/2016."
        ),
        html.Div(
            className="kpi-grid",
            children=[
                html.Div(className="kpi-card", children=[html.H3("Joueurs"), html.P(f"{total_players}")]),
                html.Div(className="kpi-card", children=[html.H3("Championnats"), html.P(f"{total_leagues}")]),
                html.Div(className="kpi-card", children=[html.H3("Équipes"), html.P(f"{total_teams}")]),
                html.Div(className="kpi-card", children=[html.H3("Matchs moyens"), html.P(f"{avg_matches}")]),
                html.Div(
                    className="kpi-card",
                    children=[html.H3("Joueurs éligibles (900+ min)"), html.P(f"{eligible_players}")],
                ),
                html.Div(className="kpi-card", children=[html.H3("Minutes moyennes"), html.P(f"{avg_minutes}")]),
            ],
        ),
        html.H2("Présentation du projet"),
        html.P(
            "Cette plateforme a été conçue comme un support de scouting et de benchmark joueurs. "
            "Elle transforme des données événementielles brutes en profils saison lisibles, comparables "
            "et exploitables dans une logique de recrutement."
        ),
        html.H2("Modules disponibles"),
        html.Ul(
            [
                html.Li("Cas d'usage : démonstrations de scénarios recrutement concrets."),
                html.Li("Validation : contrôle de cohérence poste / rôle et lecture des comparables."),
                html.Li("Scouting Lab : classements et filtres par rôle."),
                html.Li("Shortlist : ciblage recrutement avec export CSV."),
                html.Li("Explorateur joueurs : exploration de la base de profils saison."),
                html.Li("Profil joueur : fiche individuelle avec dimensions, rôles et similaires."),
                html.Li("Rapport joueur : synthèse exportable pour étude de cas ou shortlist."),
                html.Li("Radar scouting : comparaison percentile à l'intérieur d'un groupe de poste."),
                html.Li("Analyse scatter : positionnement d'un joueur dans une population filtrée."),
                html.Li("Méthodologie : hypothèses, dimensions, rôles et limites du modèle."),
            ]
        ),
        html.H2("Méthodologie"),
        html.Ul(
            [
                html.Li("Données événementielles sur les cinq grands championnats européens, saison 2015/2016."),
                html.Li("Agrégation à la saison sur une ligne principale par joueur / club / championnat."),
                html.Li("Normalisation des métriques pour construire des dimensions interprétables."),
                html.Li("Scores de rôle transparents à partir de pondérations métier explicites."),
                html.Li("Contexte de rôle intégré pour éviter les classements hors famille de poste."),
                html.Li("Comparaison de profils via similarité sur dimensions et scores de rôle."),
            ]
        ),
        html.H2("Valeur pour un club"),
        html.Ul(
            [
                html.Li("Identifier rapidement une population pertinente pour un besoin de recrutement."),
                html.Li("Comparer un joueur à des profils similaires dans d'autres clubs ou ligues."),
                html.Li("Produire une shortlist et un rapport joueur exportable pour nourrir une discussion."),
                html.Li("Documenter clairement les hypothèses du modèle pour garder un outil auditable."),
            ]
        ),
    ],
)
