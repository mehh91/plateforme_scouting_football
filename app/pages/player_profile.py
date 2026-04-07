from pathlib import Path

import dash
import pandas as pd
from dash import Input, Output, callback, dash_table, dcc, html

from app.utils.data_loader import load_player_similarity, load_primary_player_role_scores
from app.utils.scouting import build_role_score_map


dash.register_page(__name__, path="/player-profile", name="Profil joueur")


PROFILE_PATH = Path("data/processed/player_role_scores.parquet")
SIMILARITY_PATH = Path("data/processed/player_similarity.parquet")


def load_profile_data():
    try:
        return load_primary_player_role_scores()
    except Exception:
        return pd.read_parquet(PROFILE_PATH)


def load_similarity_data():
    try:
        return load_player_similarity()
    except Exception:
        return pd.read_parquet(SIMILARITY_PATH)


profile_df = load_profile_data()
similarity_df = load_similarity_data()

player_options = [
    {
        "label": f"{row['player']} - {row['team']} ({row['competition_name']})",
        "value": row["player_key"],
    }
    for _, row in profile_df.sort_values(["player", "team", "competition_name"]).iterrows()
]


def build_metric_bar(label: str, value: float, min_value: float = -2.5, max_value: float = 2.5):
    clipped_value = max(min(value, max_value), min_value)
    normalized = (clipped_value - min_value) / (max_value - min_value)
    width_pct = max(0, min(100, normalized * 100))

    return html.Div(
        className="metric-row",
        children=[
            html.Div(label, className="metric-label"),
            html.Div(
                className="metric-bar-container",
                children=[html.Div(className="metric-bar-fill", style={"width": f"{width_pct}%"})],
            ),
            html.Div(f"{value:.3f}", className="metric-value"),
        ],
    )


layout = html.Div(
    className="page-container",
    children=[
        html.H1("Profil joueur"),
        html.P("Explorez le profil individuel d'un joueur, ses scores de rôle et ses joueurs similaires."),
        html.Div(
            className="filter-grid",
            children=[
                html.Div(
                    [
                        html.Label("Sélectionner un joueur"),
                        dcc.Dropdown(
                            id="player-profile-dropdown",
                            options=player_options,
                            value=player_options[0]["value"] if player_options else None,
                            clearable=False,
                        ),
                    ]
                )
            ],
        ),
        html.Div(id="player-identity-cards", className="kpi-grid"),
        html.Div(
            className="profile-grid",
            children=[
                html.Div(className="profile-card", children=[html.H2("Dimensions football"), html.Div(id="dimensions-bars")]),
                html.Div(
                    className="profile-card",
                    children=[
                        html.H2("Scores par rôle"),
                        html.Div(id="best-role-box", className="best-role-box"),
                        html.Div(id="role-score-bars"),
                    ],
                ),
            ],
        ),
        html.Div(
            className="profile-card",
            children=[
                html.H2("Joueurs similaires"),
                dash_table.DataTable(
                    id="similar-players-table",
                    columns=[],
                    data=[],
                    page_size=10,
                    style_table={"overflowX": "auto"},
                    style_cell={"textAlign": "left", "padding": "8px", "fontSize": "14px"},
                    style_header={"fontWeight": "bold", "backgroundColor": "#f3f4f6"},
                ),
            ],
        ),
    ],
)


@callback(
    Output("player-identity-cards", "children"),
    Output("dimensions-bars", "children"),
    Output("best-role-box", "children"),
    Output("role-score-bars", "children"),
    Output("similar-players-table", "columns"),
    Output("similar-players-table", "data"),
    Input("player-profile-dropdown", "value"),
)
def update_player_profile(selected_player_key):
    if not selected_player_key:
        return [], [], "", [], [], []

    player_row = profile_df[profile_df["player_key"] == selected_player_key].copy()
    if player_row.empty:
        return [], [], "", [], [], []

    player_row = player_row.iloc[0]

    identity_cards = [
        html.Div(className="kpi-card", children=[html.H3("Joueur"), html.P(player_row["player"])]),
        html.Div(className="kpi-card", children=[html.H3("Équipe"), html.P(player_row["team"])]),
        html.Div(className="kpi-card", children=[html.H3("Poste"), html.P(player_row["position"])]),
        html.Div(className="kpi-card", children=[html.H3("Championnat"), html.P(player_row["competition_name"])]),
        html.Div(className="kpi-card", children=[html.H3("Minutes jouées"), html.P(round(player_row["minutes_played"], 1))]),
        html.Div(className="kpi-card", children=[html.H3("Matchs"), html.P(int(player_row["matches_played"]))]),
        html.Div(className="kpi-card", children=[html.H3("Titularisations"), html.P(int(player_row["starts"]))]),
    ]

    dimensions = {
        "Progression du ballon": float(player_row["ball_progression"]),
        "Création d'occasions": float(player_row["chance_creation"]),
        "Impact dans le dernier tiers": float(player_row["final_third_impact"]),
        "Activité défensive": float(player_row["defensive_activity"]),
        "Sécurité ballon": float(player_row["ball_security"]),
    }

    dimension_bars = [build_metric_bar(label, value) for label, value in dimensions.items()]

    role_scores = build_role_score_map(player_row)
    sorted_role_scores = sorted(role_scores.items(), key=lambda x: x[1], reverse=True)
    best_role_name, best_role_score = sorted_role_scores[0]

    best_role_box = html.Div(
        children=[
            html.Div("Meilleur rôle", className="best-role-title"),
            html.Div(best_role_name, className="best-role-name"),
            html.Div(f"Score : {best_role_score:.3f}", className="best-role-score"),
        ]
    )

    role_score_bars = [build_metric_bar(label, value) for label, value in sorted_role_scores]

    sample_note = html.Div(
        children=(
            "Échantillon solide pour le scouting (900+ minutes)."
            if int(player_row["meets_minimum_minutes_900"]) == 1
            else "Échantillon à interpréter avec prudence : moins de 900 minutes."
        ),
        className="summary-box",
    )

    similar_df = (
        similarity_df[similarity_df["player_key"] == selected_player_key]
        .copy()
        .sort_values("similarity_score", ascending=False)
        .head(5)
    )

    similar_display = similar_df[
        [
            "similar_player",
            "similar_player_team",
            "similar_player_competition",
            "similar_player_position",
            "similar_player_minutes",
            "similarity_score",
        ]
    ].copy()

    similar_display["similar_player_minutes"] = similar_display["similar_player_minutes"].round(1)
    similar_display["similarity_score"] = similar_display["similarity_score"].round(4)
    similar_display = similar_display.rename(
        columns={
            "similar_player": "Joueur",
            "similar_player_team": "Équipe",
            "similar_player_competition": "Championnat",
            "similar_player_position": "Poste",
            "similar_player_minutes": "Minutes",
            "similarity_score": "Score de similarité",
        }
    )

    similar_columns = [{"name": col, "id": col} for col in similar_display.columns]
    similar_records = similar_display.to_dict("records")

    return (
        identity_cards,
        dimension_bars,
        html.Div([best_role_box, sample_note]),
        role_score_bars,
        similar_columns,
        similar_records,
    )
