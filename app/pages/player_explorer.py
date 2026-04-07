import dash
from dash import Input, Output, callback, dash_table, dcc, html

from app.utils.data_loader import load_primary_player_role_scores
from app.utils.filters import filter_by_minutes, filter_by_position_group, filter_by_positions, filter_by_teams
from src.utils.position_groups import POSITION_GROUPS


dash.register_page(__name__, path="/player-explorer", name="Explorateur joueurs")


df = load_primary_player_role_scores()

LEAGUE_OPTIONS = [{"label": league, "value": league} for league in sorted(df["competition_name"].dropna().unique())]
POSITION_GROUP_OPTIONS = [{"label": group, "value": group} for group in POSITION_GROUPS.keys()]


def filter_by_leagues(df_in, selected_leagues):
    if not selected_leagues:
        return df_in
    return df_in[df_in["competition_name"].isin(selected_leagues)].copy()


def build_team_options(dff):
    return [{"label": team, "value": team} for team in sorted(dff["team"].dropna().unique())]


def build_position_options(dff):
    return [{"label": pos, "value": pos} for pos in sorted(dff["position"].dropna().unique())]


layout = html.Div(
    className="page-container",
    children=[
        html.H1("Explorateur joueurs"),
        html.P(
            "Explorez les profils saison des joueurs issus des cinq grands championnats "
            "européens sur la saison 2015/2016."
        ),
        html.Div(
            className="filter-grid",
            children=[
                html.Div(
                    [
                        html.Label("Championnat"),
                        dcc.Dropdown(
                            id="explorer-league-dropdown",
                            options=LEAGUE_OPTIONS,
                            multi=True,
                            placeholder="Tous les championnats",
                        ),
                    ]
                ),
                html.Div(
                    [
                        html.Label("Équipe"),
                        dcc.Dropdown(
                            id="explorer-team-dropdown",
                            options=[],
                            multi=True,
                            placeholder="Toutes les équipes",
                        ),
                    ]
                ),
                html.Div(
                    [
                        html.Label("Groupe de poste"),
                        dcc.Dropdown(
                            id="explorer-position-group-dropdown",
                            options=POSITION_GROUP_OPTIONS,
                            placeholder="Tous les groupes",
                        ),
                    ]
                ),
                html.Div(
                    [
                        html.Label("Poste exact"),
                        dcc.Dropdown(
                            id="explorer-position-dropdown",
                            options=[],
                            multi=True,
                            placeholder="Tous les postes",
                        ),
                    ]
                ),
                html.Div(
                    [
                        html.Label("Minutes minimum"),
                        dcc.Input(
                            id="explorer-minutes-threshold",
                            type="number",
                            value=0,
                            min=0,
                            step=50,
                            className="number-input",
                        ),
                    ]
                ),
            ],
        ),
        html.Div(id="explorer-summary", className="summary-box"),
        dash_table.DataTable(
            id="explorer-table",
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
    Output("explorer-team-dropdown", "options"),
    Output("explorer-position-dropdown", "options"),
    Input("explorer-league-dropdown", "value"),
    Input("explorer-position-group-dropdown", "value"),
    Input("explorer-minutes-threshold", "value"),
)
def update_filter_options(selected_leagues, selected_position_group, min_minutes):
    dff = df.copy()
    dff = filter_by_leagues(dff, selected_leagues)
    dff = filter_by_minutes(dff, min_minutes)
    dff = filter_by_position_group(dff, selected_position_group)

    return build_team_options(dff), build_position_options(dff)


@callback(
    Output("explorer-summary", "children"),
    Output("explorer-table", "columns"),
    Output("explorer-table", "data"),
    Input("explorer-league-dropdown", "value"),
    Input("explorer-team-dropdown", "value"),
    Input("explorer-position-group-dropdown", "value"),
    Input("explorer-position-dropdown", "value"),
    Input("explorer-minutes-threshold", "value"),
)
def update_player_explorer(selected_leagues, selected_teams, selected_position_group, selected_positions, min_minutes):
    dff = df.copy()
    dff = filter_by_leagues(dff, selected_leagues)
    dff = filter_by_minutes(dff, min_minutes)
    dff = filter_by_teams(dff, selected_teams)
    dff = filter_by_position_group(dff, selected_position_group)
    dff = filter_by_positions(dff, selected_positions)

    summary = html.Div(
        [
            html.Strong(f"{len(dff)} joueurs affichés"),
            html.Span(
                f"  |  Championnat : {', '.join(selected_leagues)}"
                if selected_leagues
                else "  |  Championnat : Tous"
            ),
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
            "shots_per90",
            "xg_per90",
            "key_passes_per90",
            "progressive_passes_per90",
            "progressive_carries_per90",
            "recoveries_per90",
            "interceptions_per90",
            "duels_per90",
        ]
    ].copy()

    display_df["minutes_played"] = display_df["minutes_played"].round(1)
    display_df["shots_per90"] = display_df["shots_per90"].round(2)
    display_df["xg_per90"] = display_df["xg_per90"].round(3)
    display_df["key_passes_per90"] = display_df["key_passes_per90"].round(2)
    display_df["progressive_passes_per90"] = display_df["progressive_passes_per90"].round(2)
    display_df["progressive_carries_per90"] = display_df["progressive_carries_per90"].round(2)
    display_df["recoveries_per90"] = display_df["recoveries_per90"].round(2)
    display_df["interceptions_per90"] = display_df["interceptions_per90"].round(2)
    display_df["duels_per90"] = display_df["duels_per90"].round(2)

    columns = [
        {"name": "Joueur", "id": "player"},
        {"name": "Équipe", "id": "team"},
        {"name": "Championnat", "id": "competition_name"},
        {"name": "Poste", "id": "position"},
        {"name": "Minutes jouées", "id": "minutes_played"},
        {"name": "Tirs / 90", "id": "shots_per90"},
        {"name": "xG / 90", "id": "xg_per90"},
        {"name": "Passes clés / 90", "id": "key_passes_per90"},
        {"name": "Passes progressives / 90", "id": "progressive_passes_per90"},
        {"name": "Conduites progressives / 90", "id": "progressive_carries_per90"},
        {"name": "Récupérations / 90", "id": "recoveries_per90"},
        {"name": "Interceptions / 90", "id": "interceptions_per90"},
        {"name": "Duels / 90", "id": "duels_per90"},
    ]

    return summary, columns, display_df.to_dict("records")
