import dash
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, callback, dash_table, dcc, html

from app.utils.data_loader import load_player_group_percentiles
from src.utils.position_groups import POSITION_GROUPS


dash.register_page(__name__, path="/scouting-radar", name="Radar scouting")


df = load_player_group_percentiles()

POSITION_GROUP_OPTIONS = [{"label": group, "value": group} for group in POSITION_GROUPS.keys()]
LEAGUE_OPTIONS = [{"label": league, "value": league} for league in sorted(df["competition_name"].dropna().unique())]


METRIC_LABELS = {
    "pass_completion_pct": "Réussite de passe",
    "progressive_passes_per90": "Passes progressives / 90",
    "progressive_carries_per90": "Conduites progressives / 90",
    "passes_into_final_third_per90": "Passes vers le dernier tiers / 90",
    "passes_into_box_per90": "Passes dans la surface / 90",
    "recoveries_per90": "Récupérations / 90",
    "interceptions_per90": "Interceptions / 90",
    "duels_per90": "Duels / 90",
    "key_passes_per90": "Passes clés / 90",
    "shots_per90": "Tirs / 90",
    "xg_per90": "xG / 90",
    "touches_in_box_per90": "Touches dans la surface / 90",
    "goals_per90": "Buts / 90",
}


GROUP_METRICS = {
    "Défenseurs centraux": ["pass_completion_pct", "progressive_passes_per90", "recoveries_per90", "interceptions_per90", "duels_per90"],
    "Latéraux": ["progressive_passes_per90", "progressive_carries_per90", "passes_into_final_third_per90", "passes_into_box_per90", "recoveries_per90"],
    "Milieux défensifs": ["pass_completion_pct", "progressive_passes_per90", "recoveries_per90", "interceptions_per90", "duels_per90"],
    "Milieux centraux": ["progressive_passes_per90", "progressive_carries_per90", "key_passes_per90", "pass_completion_pct", "recoveries_per90"],
    "Milieux offensifs": ["key_passes_per90", "progressive_passes_per90", "progressive_carries_per90", "shots_per90", "xg_per90"],
    "Ailiers": ["key_passes_per90", "progressive_passes_per90", "progressive_carries_per90", "touches_in_box_per90", "xg_per90"],
    "Attaquants": ["shots_per90", "xg_per90", "touches_in_box_per90", "goals_per90", "key_passes_per90"],
    "Gardiens": ["pass_completion_pct"],
}


def filter_by_leagues(df_in: pd.DataFrame, selected_leagues):
    if not selected_leagues:
        return df_in
    return df_in[df_in["competition_name"].isin(selected_leagues)].copy()


def filter_by_teams(df_in: pd.DataFrame, selected_teams):
    if not selected_teams:
        return df_in
    return df_in[df_in["team"].isin(selected_teams)].copy()


def filter_by_group(df_in: pd.DataFrame, selected_group):
    if not selected_group:
        return df_in
    return df_in[df_in["position_group"] == selected_group].copy()


def filter_by_minutes(df_in: pd.DataFrame, min_minutes):
    if min_minutes is None:
        return df_in
    return df_in[df_in["minutes_played"] >= min_minutes].copy()


def build_team_options(dff: pd.DataFrame):
    return [{"label": team, "value": team} for team in sorted(dff["team"].dropna().unique())]


def build_player_options(dff: pd.DataFrame):
    return [{"label": f"{row['player']} - {row['team']} ({row['position']})", "value": row["player"]} for _, row in dff.sort_values(["team", "player"]).iterrows()]


def build_empty_figure(title: str):
    fig = go.Figure()
    fig.update_layout(
        template="plotly_white",
        title=title,
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        margin=dict(l=30, r=30, t=70, b=30),
    )
    return fig


def build_percentile_radar(players_df: pd.DataFrame, position_group: str):
    metrics = GROUP_METRICS.get(position_group, [])
    pct_cols = [f"{m}_pct" for m in metrics if f"{m}_pct" in players_df.columns]

    if not pct_cols:
        return build_empty_figure("Aucune métrique disponible")

    labels = [METRIC_LABELS[m] for m in metrics if f"{m}_pct" in players_df.columns]

    fig = go.Figure()
    for _, row in players_df.iterrows():
        values = [row[col] for col in pct_cols]
        values += [values[0]]
        theta = labels + [labels[0]]
        fig.add_trace(
            go.Scatterpolar(
                r=values,
                theta=theta,
                fill="toself",
                name=f"{row['player']} ({row['team']})",
                hovertemplate="<b>%{fullData.name}</b><br>%{theta}: %{r:.1f} percentile<extra></extra>",
            )
        )

    fig.update_layout(
        template="plotly_white",
        title=f"Radar scouting - {position_group}",
        polar=dict(radialaxis=dict(visible=True, range=[0, 100], tickvals=[20, 40, 60, 80, 100])),
        legend=dict(orientation="h", yanchor="bottom", y=1.08, xanchor="left", x=0),
        margin=dict(l=30, r=30, t=80, b=30),
    )
    return fig


def build_metrics_table(players_df: pd.DataFrame, position_group: str) -> pd.DataFrame:
    metrics = GROUP_METRICS.get(position_group, [])
    rows = []

    for metric in metrics:
        pct_col = f"{metric}_pct"
        if metric not in players_df.columns or pct_col not in players_df.columns:
            continue

        row = {"Métrique": METRIC_LABELS[metric]}
        for _, player_row in players_df.iterrows():
            player_name = player_row["player"]
            row[f"{player_name} (valeur)"] = round(player_row[metric], 3) if pd.notna(player_row[metric]) else None
            row[f"{player_name} (pct)"] = round(player_row[pct_col], 1) if pd.notna(player_row[pct_col]) else None
        rows.append(row)

    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows)


layout = html.Div(
    className="page-container",
    children=[
        html.H1("Radar scouting par groupe de poste"),
        html.P("Comparez les joueurs à leur groupe de poste à partir de percentiles calculés sur des métriques adaptées."),
        html.Div(
            className="filter-grid",
            children=[
                html.Div([html.Label("Championnat"), dcc.Dropdown(id="scouting-radar-league", options=LEAGUE_OPTIONS, multi=True, placeholder="Tous les championnats")]),
                html.Div([html.Label("Équipe"), dcc.Dropdown(id="scouting-radar-team", options=[], multi=True, placeholder="Toutes les équipes")]),
                html.Div([html.Label("Groupe de poste"), dcc.Dropdown(id="scouting-radar-group", options=POSITION_GROUP_OPTIONS, value="Ailiers", clearable=False)]),
                html.Div(
                    [
                        html.Label("Minutes minimum"),
                        dcc.Input(id="scouting-radar-minutes", type="number", value=900, min=0, step=50, className="number-input"),
                    ]
                ),
            ],
        ),
        html.Div(
            className="profile-card",
            children=[
                html.Label("Joueurs à comparer (2 à 4)"),
                dcc.Dropdown(id="scouting-radar-players", options=[], multi=True, placeholder="Sélectionnez 2 à 4 joueurs"),
            ],
        ),
        html.Div(id="scouting-radar-summary", className="summary-box"),
        html.Div(className="profile-card", children=[dcc.Graph(id="scouting-radar-graph")]),
        html.Div(
            className="profile-card",
            children=[
                html.H2("Détail des métriques"),
                dash_table.DataTable(
                    id="scouting-radar-metrics-table",
                    columns=[],
                    data=[],
                    style_table={"overflowX": "auto"},
                    style_cell={"textAlign": "left", "padding": "8px", "fontSize": "14px", "minWidth": "140px", "maxWidth": "240px", "whiteSpace": "normal"},
                    style_header={"fontWeight": "bold", "backgroundColor": "#f3f4f6"},
                ),
            ],
        ),
    ],
)


@callback(
    Output("scouting-radar-team", "options"),
    Output("scouting-radar-players", "options"),
    Input("scouting-radar-league", "value"),
    Input("scouting-radar-group", "value"),
    Input("scouting-radar-minutes", "value"),
    Input("scouting-radar-team", "value"),
)
def update_radar_filter_options(selected_leagues, position_group, min_minutes, selected_teams):
    dff = df.copy()
    dff = filter_by_leagues(dff, selected_leagues)
    dff = filter_by_group(dff, position_group)
    dff = filter_by_minutes(dff, min_minutes)
    return build_team_options(dff), build_player_options(filter_by_teams(dff, selected_teams))


@callback(
    Output("scouting-radar-summary", "children"),
    Output("scouting-radar-graph", "figure"),
    Output("scouting-radar-metrics-table", "columns"),
    Output("scouting-radar-metrics-table", "data"),
    Input("scouting-radar-league", "value"),
    Input("scouting-radar-team", "value"),
    Input("scouting-radar-group", "value"),
    Input("scouting-radar-minutes", "value"),
    Input("scouting-radar-players", "value"),
)
def update_radar(selected_leagues, selected_teams, position_group, min_minutes, selected_players):
    dff = df.copy()
    dff = filter_by_leagues(dff, selected_leagues)
    dff = filter_by_group(dff, position_group)
    dff = filter_by_minutes(dff, min_minutes)
    dff = filter_by_teams(dff, selected_teams)

    if not selected_players:
        summary = html.Div([html.Strong(f"{len(dff)} joueurs disponibles"), html.Span("  |  Sélectionnez 2 à 4 joueurs pour afficher le radar")])
        return summary, build_empty_figure("Sélectionnez des joueurs"), [], []

    selected_players = selected_players[:4]
    radar_df = dff[dff["player"].isin(selected_players)].copy()
    summary = html.Div(
        [
            html.Strong(f"{len(dff)} joueurs disponibles dans le groupe"),
            html.Span(f"  |  Championnat : {', '.join(selected_leagues)}" if selected_leagues else "  |  Championnat : Tous"),
            html.Span(f"  |  Groupe : {position_group}"),
            html.Span(f"  |  Joueurs comparés : {len(radar_df)}"),
            html.Span(f"  |  Minutes minimum : {min_minutes if min_minutes is not None else 0}"),
        ]
    )

    metrics_table_df = build_metrics_table(radar_df, position_group)
    return (
        summary,
        build_percentile_radar(radar_df, position_group),
        [{"name": col, "id": col} for col in metrics_table_df.columns],
        metrics_table_df.to_dict("records"),
    )
