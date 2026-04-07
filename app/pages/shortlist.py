import dash
import pandas as pd
from dash import Input, Output, State, callback, dash_table, dcc, html

from app.utils.data_loader import load_player_similarity, load_primary_player_role_scores
from app.utils.labels import ROLE_LABELS
from app.utils.recruitment import (
    apply_recruitment_filters,
    build_player_options,
    build_position_options,
    build_shortlist_table,
    build_team_options,
)
from src.utils.position_groups import POSITION_GROUPS


dash.register_page(__name__, path="/shortlist", name="Shortlist")


df = load_primary_player_role_scores()
similarity_df = load_player_similarity()


ROLE_OPTIONS = [{"label": label, "value": value} for value, label in ROLE_LABELS.items()]
LEAGUE_OPTIONS = [{"label": league, "value": league} for league in sorted(df["competition_name"].dropna().unique())]
POSITION_GROUP_OPTIONS = [{"label": group, "value": group} for group in POSITION_GROUPS.keys()]


layout = html.Div(
    className="page-container",
    children=[
        html.H1("Shortlist recrutement"),
        html.P(
            "Construisez une shortlist exploitable pour un besoin de recrutement : filtrez votre population, "
            "choisissez un rôle cible et, si besoin, rapprochez la recherche d'un joueur référence."
        ),
        html.Div(
            className="filter-grid",
            children=[
                html.Div([html.Label("Championnat"), dcc.Dropdown(id="shortlist-league-dropdown", options=LEAGUE_OPTIONS, multi=True)]),
                html.Div(
                    [
                        html.Label("Rôle cible"),
                        dcc.Dropdown(
                            id="shortlist-role-dropdown",
                            options=ROLE_OPTIONS,
                            value=ROLE_OPTIONS[0]["value"],
                            clearable=False,
                        ),
                    ]
                ),
                html.Div([html.Label("Équipe"), dcc.Dropdown(id="shortlist-team-dropdown", options=[], multi=True)]),
                html.Div([html.Label("Groupe de poste"), dcc.Dropdown(id="shortlist-position-group-dropdown", options=POSITION_GROUP_OPTIONS)]),
                html.Div([html.Label("Poste exact"), dcc.Dropdown(id="shortlist-position-dropdown", options=[], multi=True)]),
                html.Div(
                    [
                        html.Label("Minutes minimum"),
                        dcc.Input(
                            id="shortlist-minutes-threshold",
                            type="number",
                            value=900,
                            min=0,
                            step=50,
                            className="number-input",
                        ),
                    ]
                ),
                html.Div(
                    [
                        html.Label("Joueur référence"),
                        dcc.Dropdown(id="shortlist-reference-player", options=[], placeholder="Optionnel"),
                    ]
                ),
                html.Div(
                    [
                        html.Label("Nombre de profils"),
                        dcc.Input(
                            id="shortlist-top-n",
                            type="number",
                            value=12,
                            min=3,
                            max=50,
                            step=1,
                            className="number-input",
                        ),
                    ]
                ),
            ],
        ),
        html.Div(
            className="profile-card",
            children=[
                dcc.Checklist(
                    id="shortlist-options",
                    options=[{"label": "Exclure l'équipe du joueur référence", "value": "exclude_reference_team"}],
                    value=["exclude_reference_team"],
                    className="inline-checklist",
                )
            ],
        ),
        html.Div(id="shortlist-summary", className="summary-box"),
        html.Div(
            className="action-row",
            children=[html.Button("Exporter la shortlist CSV", id="shortlist-export-button", className="primary-button")],
        ),
        dash_table.DataTable(
            id="shortlist-table",
            page_size=12,
            sort_action="native",
            style_table={"overflowX": "auto"},
            style_cell={
                "textAlign": "left",
                "padding": "8px",
                "minWidth": "120px",
                "maxWidth": "280px",
                "whiteSpace": "normal",
                "fontSize": "14px",
            },
            style_header={"fontWeight": "bold", "backgroundColor": "#f3f4f6"},
        ),
        dcc.Store(id="shortlist-store"),
        dcc.Download(id="shortlist-download"),
    ],
)


@callback(
    Output("shortlist-team-dropdown", "options"),
    Output("shortlist-position-dropdown", "options"),
    Output("shortlist-reference-player", "options"),
    Input("shortlist-league-dropdown", "value"),
    Input("shortlist-position-group-dropdown", "value"),
    Input("shortlist-minutes-threshold", "value"),
)
def update_shortlist_filter_options(selected_leagues, selected_position_group, min_minutes):
    dff = apply_recruitment_filters(
        df=df,
        selected_leagues=selected_leagues,
        selected_position_group=selected_position_group,
        min_minutes=min_minutes,
    )
    return build_team_options(dff), build_position_options(dff), build_player_options(dff)


@callback(
    Output("shortlist-summary", "children"),
    Output("shortlist-table", "columns"),
    Output("shortlist-table", "data"),
    Output("shortlist-store", "data"),
    Input("shortlist-league-dropdown", "value"),
    Input("shortlist-role-dropdown", "value"),
    Input("shortlist-team-dropdown", "value"),
    Input("shortlist-position-group-dropdown", "value"),
    Input("shortlist-position-dropdown", "value"),
    Input("shortlist-minutes-threshold", "value"),
    Input("shortlist-reference-player", "value"),
    Input("shortlist-top-n", "value"),
    Input("shortlist-options", "value"),
)
def update_shortlist(
    selected_leagues,
    selected_role,
    selected_teams,
    selected_position_group,
    selected_positions,
    min_minutes,
    reference_player_key,
    top_n,
    options,
):
    top_n = top_n or 12
    exclude_reference_team = "exclude_reference_team" in (options or [])

    dff = apply_recruitment_filters(
        df=df,
        selected_leagues=selected_leagues,
        selected_teams=selected_teams,
        selected_position_group=selected_position_group,
        selected_positions=selected_positions,
        min_minutes=min_minutes,
    )

    shortlist_df = build_shortlist_table(
        base_df=dff,
        similarity_df=similarity_df,
        selected_role=selected_role,
        reference_player_key=reference_player_key,
        top_n=top_n,
        exclude_reference_team=exclude_reference_team,
    )

    role_label = ROLE_LABELS[selected_role]
    reference_text = (
        shortlist_df["reference_label"].dropna().iloc[0]
        if not shortlist_df.empty and shortlist_df["reference_label"].dropna().any()
        else None
    )

    summary = html.Div(
        [
            html.Strong(f"{len(shortlist_df)} profils retenus"),
            html.Span(f"  |  Rôle cible : {role_label}"),
            html.Span(f"  |  Référence : {reference_text}" if reference_text else "  |  Référence : aucune"),
            html.Span(f"  |  Minutes minimum : {min_minutes if min_minutes is not None else 0}"),
            html.Span(
                f"  |  Groupe de poste : {selected_position_group}"
                if selected_position_group
                else "  |  Groupe de poste : Tous"
            ),
        ]
    )

    display_df = shortlist_df[
        [
            "rank",
            "player",
            "team",
            "competition_name",
            "position",
            "minutes_played",
            "role_score",
            "reference_similarity",
            "shortlist_fit",
            "rationale",
        ]
    ].copy()

    display_df = display_df.rename(
        columns={
            "rank": "Rang",
            "player": "Joueur",
            "team": "Équipe",
            "competition_name": "Championnat",
            "position": "Poste",
            "minutes_played": "Minutes",
            "role_score": role_label,
            "reference_similarity": "Similarité réf.",
            "shortlist_fit": "Shortlist fit",
            "rationale": "Lecture",
        }
    )
    display_df = display_df.astype(object).where(pd.notna(display_df), None)

    columns = [{"name": col, "id": col} for col in display_df.columns]
    records = display_df.to_dict("records")

    return summary, columns, records, records


@callback(
    Output("shortlist-download", "data"),
    Input("shortlist-export-button", "n_clicks"),
    State("shortlist-role-dropdown", "value"),
    State("shortlist-store", "data"),
    prevent_initial_call=True,
)
def export_shortlist(n_clicks, selected_role, shortlist_records):
    if not n_clicks or not shortlist_records:
        return dash.no_update

    export_df = pd.DataFrame(shortlist_records)
    csv_content = export_df.to_csv(index=False)
    role_slug = selected_role.replace("_score", "")

    return {
        "content": csv_content,
        "filename": f"shortlist_{role_slug}.csv",
        "type": "text/csv",
    }
