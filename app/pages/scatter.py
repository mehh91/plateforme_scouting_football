import dash
import pandas as pd
import plotly.express as px
from dash import Input, Output, callback, dcc, html

from app.utils.data_loader import load_primary_player_role_scores
from app.utils.filters import (
    deduplicate_players_by_primary_position,
    filter_by_minutes,
    filter_by_position_group,
    filter_by_positions,
    filter_by_teams,
)
from app.utils.labels import DIMENSION_LABELS, METRIC_LABELS, ROLE_LABELS
from src.utils.position_groups import POSITION_GROUPS


dash.register_page(__name__, path="/scatter", name="Analyse scatter")


df = load_primary_player_role_scores()

LEAGUE_OPTIONS = [{"label": league, "value": league} for league in sorted(df["competition_name"].dropna().unique())]
POSITION_GROUP_OPTIONS = [{"label": group, "value": group} for group in POSITION_GROUPS.keys()]

SCATTER_METRIC_LABELS = {}
SCATTER_METRIC_LABELS.update(DIMENSION_LABELS)
SCATTER_METRIC_LABELS.update(METRIC_LABELS)
SCATTER_METRIC_LABELS.update({column: f"Score {label}" for column, label in ROLE_LABELS.items() if column in df.columns})
SCATTER_OPTIONS = [{"label": label, "value": value} for value, label in SCATTER_METRIC_LABELS.items()]


def filter_by_leagues(df_in, selected_leagues):
    if not selected_leagues:
        return df_in
    return df_in[df_in["competition_name"].isin(selected_leagues)].copy()


def build_team_options(dff: pd.DataFrame):
    return [{"label": team, "value": team} for team in sorted(dff["team"].dropna().unique())]


def build_position_options(dff: pd.DataFrame):
    return [{"label": pos, "value": pos} for pos in sorted(dff["position"].dropna().unique())]


def build_player_options(dff: pd.DataFrame):
    return [{"label": f"{row['player']} - {row['team']} ({row['position']})", "value": row["player"]} for _, row in dff.sort_values(["team", "player"]).iterrows()]


def build_empty_scatter(title: str):
    fig = px.scatter()
    fig.update_layout(template="plotly_white", title=title, margin=dict(l=20, r=20, t=60, b=20))
    return fig


def build_scatter_figure(dff: pd.DataFrame, x_metric: str, y_metric: str, highlighted_player: str | None):
    if dff.empty:
        return build_empty_scatter("Aucune donnée disponible")

    plot_df = dff.copy()
    plot_df["highlight"] = plot_df["player"].eq(highlighted_player)
    fig = px.scatter(
        plot_df,
        x=x_metric,
        y=y_metric,
        color="highlight",
        hover_data=["player", "team", "competition_name", "position", "minutes_played"],
        color_discrete_map={True: "#dc2626", False: "#2563eb"},
        opacity=0.80,
    )

    fig.update_traces(marker=dict(size=11, line=dict(width=0.6, color="white")))
    fig.update_layout(
        template="plotly_white",
        title=f"{SCATTER_METRIC_LABELS[x_metric]} vs {SCATTER_METRIC_LABELS[y_metric]}",
        legend_title_text="Joueur mis en évidence",
        margin=dict(l=20, r=20, t=60, b=20),
    )
    fig.update_xaxes(title_text=SCATTER_METRIC_LABELS[x_metric])
    fig.update_yaxes(title_text=SCATTER_METRIC_LABELS[y_metric])
    return fig


layout = html.Div(
    className="page-container",
    children=[
        html.H1("Analyse scatter"),
        html.P("Positionnez un joueur dans une population filtrée selon deux métriques de votre choix."),
        html.Div(
            className="filter-grid",
            children=[
                html.Div([html.Label("Championnat"), dcc.Dropdown(id="scatter-league-dropdown", options=LEAGUE_OPTIONS, multi=True)]),
                html.Div([html.Label("Équipe"), dcc.Dropdown(id="scatter-team-dropdown", options=[], multi=True)]),
                html.Div([html.Label("Groupe de poste"), dcc.Dropdown(id="scatter-position-group-dropdown", options=POSITION_GROUP_OPTIONS)]),
                html.Div([html.Label("Poste exact"), dcc.Dropdown(id="scatter-position-dropdown", options=[], multi=True)]),
                html.Div([html.Label("Minutes minimum"), dcc.Input(id="scatter-minutes-threshold", type="number", value=900, min=0, step=50, className="number-input")]),
                html.Div([html.Label("Joueur à mettre en évidence"), dcc.Dropdown(id="scatter-highlight-player", options=[])]),
                html.Div([html.Label("Axe X"), dcc.Dropdown(id="scatter-x-axis", options=SCATTER_OPTIONS, value="ball_progression", clearable=False)]),
                html.Div([html.Label("Axe Y"), dcc.Dropdown(id="scatter-y-axis", options=SCATTER_OPTIONS, value="chance_creation", clearable=False)]),
            ],
        ),
        html.Div(id="scatter-summary", className="summary-box"),
        html.Div(className="profile-card", children=[dcc.Graph(id="scatter-graph")]),
    ],
)


@callback(
    Output("scatter-team-dropdown", "options"),
    Output("scatter-position-dropdown", "options"),
    Output("scatter-highlight-player", "options"),
    Input("scatter-league-dropdown", "value"),
    Input("scatter-position-group-dropdown", "value"),
    Input("scatter-minutes-threshold", "value"),
)
def update_scatter_filter_options(selected_leagues, selected_position_group, min_minutes):
    dff = df.copy()
    dff = filter_by_leagues(dff, selected_leagues)
    dff = filter_by_minutes(dff, min_minutes)
    dff = filter_by_position_group(dff, selected_position_group)
    dff = deduplicate_players_by_primary_position(dff)
    return build_team_options(dff), build_position_options(dff), build_player_options(dff)


@callback(
    Output("scatter-summary", "children"),
    Output("scatter-graph", "figure"),
    Input("scatter-league-dropdown", "value"),
    Input("scatter-team-dropdown", "value"),
    Input("scatter-position-group-dropdown", "value"),
    Input("scatter-position-dropdown", "value"),
    Input("scatter-minutes-threshold", "value"),
    Input("scatter-highlight-player", "value"),
    Input("scatter-x-axis", "value"),
    Input("scatter-y-axis", "value"),
)
def update_scatter_page(
    selected_leagues,
    selected_teams,
    selected_position_group,
    selected_positions,
    min_minutes,
    highlighted_player,
    x_metric,
    y_metric,
):
    dff = df.copy()
    dff = filter_by_leagues(dff, selected_leagues)
    dff = filter_by_minutes(dff, min_minutes)
    dff = filter_by_teams(dff, selected_teams)
    dff = filter_by_position_group(dff, selected_position_group)
    dff = filter_by_positions(dff, selected_positions)
    dff = deduplicate_players_by_primary_position(dff)

    summary = html.Div(
        [
            html.Strong(f"{len(dff)} joueurs affichés"),
            html.Span(f"  |  Championnat : {', '.join(selected_leagues)}" if selected_leagues else "  |  Championnat : Tous"),
            html.Span(f"  |  Groupe de poste : {selected_position_group}" if selected_position_group else "  |  Groupe de poste : Tous"),
            html.Span(f"  |  Minutes minimum : {min_minutes if min_minutes is not None else 0}"),
        ]
    )
    return summary, build_scatter_figure(dff, x_metric, y_metric, highlighted_player)
