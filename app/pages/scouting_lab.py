import dash
import pandas as pd
from dash import Input, Output, callback, dash_table, dcc, html

from app.utils.data_loader import load_primary_player_role_scores
from app.utils.filters import filter_by_minutes, filter_by_position_group, filter_by_positions, filter_by_teams
from app.utils.labels import ROLE_LABELS
from src.utils.position_groups import POSITION_GROUPS


dash.register_page(__name__, path="/scouting-lab", name="Scouting Lab")


df = load_primary_player_role_scores()

ROLE_OPTIONS = [{"label": label, "value": value} for value, label in ROLE_LABELS.items()]
LEAGUE_OPTIONS = [{"label": league, "value": league} for league in sorted(df["competition_name"].dropna().unique())]
POSITION_GROUP_OPTIONS = [{"label": group, "value": group} for group in POSITION_GROUPS.keys()]


def filter_by_leagues(df_in, selected_leagues):
    if not selected_leagues:
        return df_in
    return df_in[df_in["competition_name"].isin(selected_leagues)].copy()


def build_team_options(dff: pd.DataFrame):
    return [{"label": team, "value": team} for team in sorted(dff["team"].dropna().unique())]


def build_position_options(dff: pd.DataFrame):
    return [{"label": pos, "value": pos} for pos in sorted(dff["position"].dropna().unique())]


layout = html.Div(
    className="page-container",
    children=[
        html.H1("Scouting Lab"),
        html.P(
            "Classez et filtrez les joueurs selon un rôle, un championnat, une équipe, "
            "un groupe de poste, un poste exact et un temps de jeu minimum."
        ),
        html.Div(
            className="filter-grid",
            children=[
                html.Div([html.Label("Championnat"), dcc.Dropdown(id="scouting-league-dropdown", options=LEAGUE_OPTIONS, multi=True, placeholder="Tous les championnats")]),
                html.Div([html.Label("Rôle"), dcc.Dropdown(id="scouting-role-dropdown", options=ROLE_OPTIONS, value="progressive_midfielder_score", clearable=False)]),
                html.Div([html.Label("Équipe"), dcc.Dropdown(id="scouting-team-dropdown", options=[], multi=True, placeholder="Toutes les équipes")]),
                html.Div([html.Label("Groupe de poste"), dcc.Dropdown(id="scouting-position-group-dropdown", options=POSITION_GROUP_OPTIONS, placeholder="Tous les groupes")]),
                html.Div([html.Label("Poste exact"), dcc.Dropdown(id="scouting-position-dropdown", options=[], multi=True, placeholder="Tous les postes")]),
                html.Div(
                    [
                        html.Label("Minutes minimum"),
                        dcc.Input(
                            id="scouting-minutes-threshold",
                            type="number",
                            value=900,
                            min=0,
                            step=50,
                            className="number-input",
                        ),
                    ]
                ),
            ],
        ),
        html.Div(id="scouting-summary", className="summary-box"),
        dash_table.DataTable(
            id="scouting-table",
            page_size=20,
            sort_action="native",
            filter_action="native",
            style_table={"overflowX": "auto"},
            style_cell={
                "textAlign": "left",
                "padding": "8px",
                "minWidth": "120px",
                "maxWidth": "220px",
                "whiteSpace": "normal",
                "fontSize": "14px",
            },
            style_header={"fontWeight": "bold", "backgroundColor": "#f3f4f6"},
        ),
    ],
)


@callback(
    Output("scouting-team-dropdown", "options"),
    Output("scouting-position-dropdown", "options"),
    Input("scouting-league-dropdown", "value"),
    Input("scouting-position-group-dropdown", "value"),
    Input("scouting-minutes-threshold", "value"),
)
def update_filter_options(selected_leagues, selected_position_group, min_minutes):
    dff = df.copy()
    dff = filter_by_leagues(dff, selected_leagues)
    dff = filter_by_minutes(dff, min_minutes)
    dff = filter_by_position_group(dff, selected_position_group)

    return build_team_options(dff), build_position_options(dff)


@callback(
    Output("scouting-summary", "children"),
    Output("scouting-table", "columns"),
    Output("scouting-table", "data"),
    Input("scouting-league-dropdown", "value"),
    Input("scouting-role-dropdown", "value"),
    Input("scouting-team-dropdown", "value"),
    Input("scouting-position-group-dropdown", "value"),
    Input("scouting-position-dropdown", "value"),
    Input("scouting-minutes-threshold", "value"),
)
def update_scouting_lab(
    selected_leagues,
    selected_role,
    selected_teams,
    selected_position_group,
    selected_positions,
    min_minutes,
):
    dff = df.copy()
    dff = filter_by_leagues(dff, selected_leagues)
    dff = filter_by_minutes(dff, min_minutes)
    dff = filter_by_teams(dff, selected_teams)
    dff = filter_by_position_group(dff, selected_position_group)
    dff = filter_by_positions(dff, selected_positions)

    dff = dff.sort_values(selected_role, ascending=False).copy()
    dff["role_score"] = dff[selected_role].round(3)
    dff["minutes_played"] = dff["minutes_played"].round(1)
    dff["ball_progression"] = dff["ball_progression"].round(3)
    dff["chance_creation"] = dff["chance_creation"].round(3)
    dff["final_third_impact"] = dff["final_third_impact"].round(3)
    dff["defensive_activity"] = dff["defensive_activity"].round(3)
    dff["ball_security"] = dff["ball_security"].round(3)

    summary = html.Div(
        [
            html.Strong(f"{len(dff)} joueurs affichés"),
            html.Span(f"  |  Championnat : {', '.join(selected_leagues)}" if selected_leagues else "  |  Championnat : Tous"),
            html.Span(
                f"  |  Groupe de poste : {selected_position_group}"
                if selected_position_group
                else "  |  Groupe de poste : Tous"
            ),
            html.Span(f"  |  Minutes minimum : {min_minutes if min_minutes is not None else 0}"),
        ]
    )

    display_df = dff[
        [
            "player",
            "team",
            "competition_name",
            "position",
            "minutes_played",
            "role_score",
            "ball_progression",
            "chance_creation",
            "final_third_impact",
            "defensive_activity",
            "ball_security",
        ]
    ].copy()

    columns = [
        {"name": "Joueur", "id": "player"},
        {"name": "Équipe", "id": "team"},
        {"name": "Championnat", "id": "competition_name"},
        {"name": "Poste", "id": "position"},
        {"name": "Minutes jouées", "id": "minutes_played"},
        {"name": ROLE_LABELS[selected_role], "id": "role_score"},
        {"name": "Progression du ballon", "id": "ball_progression"},
        {"name": "Création d'occasions", "id": "chance_creation"},
        {"name": "Impact dans le dernier tiers", "id": "final_third_impact"},
        {"name": "Activité défensive", "id": "defensive_activity"},
        {"name": "Sécurité ballon", "id": "ball_security"},
    ]

    return summary, columns, display_df.to_dict("records")
