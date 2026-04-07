import dash
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html

from app.utils.data_loader import load_primary_player_role_scores
from app.utils.labels import ROLE_LABELS
from src.utils.position_groups import POSITION_GROUPS


dash.register_page(__name__, path="/radar", name="Comparaison radar")


df = load_primary_player_role_scores()

TEAM_OPTIONS = [{"label": team, "value": team} for team in sorted(df["team"].dropna().unique())]
POSITION_GROUP_OPTIONS = [{"label": group, "value": group} for group in POSITION_GROUPS.keys()]
RADAR_MODE_OPTIONS = [{"label": "Dimensions football", "value": "dimensions"}, {"label": "Scores par rôle", "value": "roles"}]

DIMENSION_COLUMNS = {
    "ball_progression": "Progression du ballon",
    "chance_creation": "Création d'occasions",
    "final_third_impact": "Impact dans le dernier tiers",
    "defensive_activity": "Activité défensive",
    "ball_security": "Sécurité ballon",
}

ROLE_SCORE_COLUMNS = {column: label for column, label in ROLE_LABELS.items() if column in df.columns}


def apply_filters(data: pd.DataFrame, selected_teams, selected_position_group, min_minutes) -> pd.DataFrame:
    dff = data.copy()
    if min_minutes is not None:
        dff = dff[dff["minutes_played"] >= min_minutes]
    if selected_teams:
        dff = dff[dff["team"].isin(selected_teams)]
    if selected_position_group:
        allowed_positions = POSITION_GROUPS.get(selected_position_group, [])
        dff = dff[dff["position"].isin(allowed_positions)]
    return dff


def build_empty_radar(title: str):
    fig = go.Figure()
    fig.update_layout(template="plotly_white", title=title, polar=dict(radialaxis=dict(visible=True, showticklabels=True)), margin=dict(l=30, r=30, t=60, b=30))
    return fig


def build_radar_figure(players_df: pd.DataFrame, mode: str):
    if players_df.empty:
        return build_empty_radar("Aucune donnée disponible")

    if mode == "roles":
        metric_map = ROLE_SCORE_COLUMNS
        title = "Comparaison radar - Scores par rôle"
    else:
        metric_map = DIMENSION_COLUMNS
        title = "Comparaison radar - Dimensions football"

    metric_keys = list(metric_map.keys())
    metric_labels = list(metric_map.values())
    fig = go.Figure()

    for _, row in players_df.iterrows():
        values = [row[col] for col in metric_keys]
        values += [values[0]]
        theta = metric_labels + [metric_labels[0]]
        fig.add_trace(
            go.Scatterpolar(
                r=values,
                theta=theta,
                fill="toself",
                name=f"{row['player']} ({row['team']})",
                hovertemplate="<b>%{fullData.name}</b><br>%{theta}: %{r:.3f}<extra></extra>",
            )
        )

    fig.update_layout(
        template="plotly_white",
        title=title,
        polar=dict(radialaxis=dict(visible=True, showticklabels=True)),
        legend=dict(orientation="h", yanchor="bottom", y=1.08, xanchor="left", x=0),
        margin=dict(l=30, r=30, t=80, b=30),
    )
    return fig


layout = html.Div(
    className="page-container",
    children=[
        html.H1("Comparaison radar"),
        html.P("Comparez visuellement plusieurs joueurs à partir des dimensions football ou des scores par rôle."),
        html.Div(
            className="filter-grid",
            children=[
                html.Div([html.Label("Équipe"), dcc.Dropdown(id="radar-team-dropdown", options=TEAM_OPTIONS, multi=True, placeholder="Toutes les équipes")]),
                html.Div([html.Label("Groupe de poste"), dcc.Dropdown(id="radar-position-group-dropdown", options=POSITION_GROUP_OPTIONS, placeholder="Tous les groupes")]),
                html.Div([html.Label("Minutes minimum"), dcc.Input(id="radar-minutes-threshold", type="number", value=900, min=0, step=50, className="number-input")]),
                html.Div([html.Label("Type de radar"), dcc.Dropdown(id="radar-mode-dropdown", options=RADAR_MODE_OPTIONS, value="dimensions", clearable=False)]),
            ],
        ),
        html.Div(
            className="profile-card",
            children=[
                html.Label("Joueurs à comparer (2 à 4)"),
                dcc.Dropdown(id="radar-player-dropdown", options=[], multi=True, placeholder="Sélectionnez 2 à 4 joueurs"),
            ],
        ),
        html.Div(id="radar-summary", className="summary-box"),
        html.Div(className="profile-card", children=[dcc.Graph(id="radar-graph")]),
    ],
)


@callback(
    Output("radar-player-dropdown", "options"),
    Input("radar-team-dropdown", "value"),
    Input("radar-position-group-dropdown", "value"),
    Input("radar-minutes-threshold", "value"),
)
def update_player_options(selected_teams, selected_position_group, min_minutes):
    dff = apply_filters(df, selected_teams, selected_position_group, min_minutes)
    return [{"label": f"{row['player']} - {row['team']} ({row['position']})", "value": row["player"]} for _, row in dff.sort_values(["team", "player"]).iterrows()]


@callback(
    Output("radar-summary", "children"),
    Output("radar-graph", "figure"),
    Input("radar-player-dropdown", "value"),
    Input("radar-team-dropdown", "value"),
    Input("radar-position-group-dropdown", "value"),
    Input("radar-minutes-threshold", "value"),
    Input("radar-mode-dropdown", "value"),
)
def update_radar(selected_players, selected_teams, selected_position_group, min_minutes, radar_mode):
    dff = apply_filters(df, selected_teams, selected_position_group, min_minutes)

    if not selected_players:
        summary = html.Div([html.Strong(f"{len(dff)} joueurs disponibles après filtres"), html.Span("  |  Sélectionnez 2 à 4 joueurs pour générer le radar")])
        return summary, build_empty_radar("Sélectionnez des joueurs")

    selected_players = selected_players[:4]
    radar_df = dff[dff["player"].isin(selected_players)].copy()
    summary = html.Div(
        [
            html.Strong(f"{len(dff)} joueurs disponibles après filtres"),
            html.Span(f"  |  Joueurs comparés : {len(radar_df)}"),
            html.Span(f"  |  Minutes minimum : {min_minutes if min_minutes is not None else 0}"),
            html.Span(f"  |  Groupe de poste : {selected_position_group}" if selected_position_group else "  |  Groupe de poste : Tous"),
        ]
    )
    return summary, build_radar_figure(radar_df, radar_mode)
