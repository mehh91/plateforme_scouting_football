import dash
import pandas as pd
from dash import Input, Output, State, callback, dash_table, dcc, html

from app.utils.data_loader import load_player_similarity, load_primary_player_role_scores
from app.utils.labels import DIMENSION_LABELS, METRIC_LABELS
from app.utils.scouting import build_profile_summary, get_top_dimensions, get_top_roles, get_watch_dimensions


dash.register_page(__name__, path="/player-report", name="Rapport joueur")


profile_df = load_primary_player_role_scores()
similarity_df = load_player_similarity()

REPORT_METRICS = [
    "shots_per90",
    "xg_per90",
    "key_passes_per90",
    "progressive_passes_per90",
    "progressive_carries_per90",
    "passes_into_box_per90",
    "touches_in_box_per90",
    "recoveries_per90",
    "interceptions_per90",
    "duels_per90",
    "pass_completion_pct",
]


player_options = [
    {
        "label": f"{row['player']} - {row['team']} ({row['competition_name']})",
        "value": row["player_key"],
    }
    for _, row in profile_df.sort_values(["player", "team", "competition_name"]).iterrows()
]


def build_report_html(player_row: pd.Series, summary: str, top_roles, strengths, watchpoints, metrics_df, similar_df) -> str:
    role_html = "".join([f"<li>{label}: {score:.3f}</li>" for label, score in top_roles])
    strengths_html = "".join([f"<li>{label} ({score:.3f})</li>" for label, score in strengths])
    watchpoints_html = "".join([f"<li>{label} ({score:.3f})</li>" for label, score in watchpoints])
    metrics_html = metrics_df.to_html(index=False, border=0)
    similar_html = similar_df.to_html(index=False, border=0)

    return f"""
    <html>
      <head>
        <meta charset="utf-8" />
        <title>Rapport - {player_row['player']}</title>
        <style>
          body {{ font-family: Arial, sans-serif; margin: 32px; color: #111827; }}
          h1, h2 {{ color: #0f172a; }}
          .meta {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 24px; }}
          .card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px; }}
          table {{ border-collapse: collapse; width: 100%; margin-top: 12px; }}
          th, td {{ border: 1px solid #e2e8f0; padding: 8px; text-align: left; }}
          th {{ background: #eff6ff; }}
        </style>
      </head>
      <body>
        <h1>Rapport joueur - {player_row['player']}</h1>
        <div class="meta">
          <div class="card"><strong>Équipe</strong><br />{player_row['team']}</div>
          <div class="card"><strong>Championnat</strong><br />{player_row['competition_name']}</div>
          <div class="card"><strong>Poste principal</strong><br />{player_row['position']}</div>
          <div class="card"><strong>Minutes</strong><br />{player_row['minutes_played']:.1f}</div>
        </div>
        <h2>Synthèse</h2>
        <p>{summary}</p>
        <h2>Top rôles</h2>
        <ul>{role_html}</ul>
        <h2>Points forts</h2>
        <ul>{strengths_html}</ul>
        <h2>Points de vigilance</h2>
        <ul>{watchpoints_html}</ul>
        <h2>Métriques clés</h2>
        {metrics_html}
        <h2>Joueurs similaires</h2>
        {similar_html}
      </body>
    </html>
    """


layout = html.Div(
    className="page-container",
    children=[
        html.H1("Rapport joueur"),
        html.P(
            "Générez une fiche exportable pour un joueur, avec lecture automatique du profil, "
            "top rôles, dimensions fortes et comparables."
        ),
        html.Div(
            className="filter-grid",
            children=[
                html.Div(
                    [
                        html.Label("Sélectionner un joueur"),
                        dcc.Dropdown(
                            id="player-report-dropdown",
                            options=player_options,
                            value=player_options[0]["value"] if player_options else None,
                            clearable=False,
                        ),
                    ]
                ),
            ],
        ),
        html.Div(
            className="action-row",
            children=[html.Button("Exporter le rapport HTML", id="player-report-export", className="primary-button")],
        ),
        html.Div(id="player-report-header", className="kpi-grid"),
        html.Div(id="player-report-summary", className="summary-box"),
        html.Div(
            className="profile-grid",
            children=[
                html.Div(className="profile-card", children=[html.H2("Top rôles"), html.Div(id="player-report-roles")]),
                html.Div(className="profile-card", children=[html.H2("Dimensions"), html.Div(id="player-report-dimensions")]),
            ],
        ),
        html.Div(
            className="profile-grid",
            children=[
                html.Div(className="profile-card", children=[html.H2("Points forts"), html.Ul(id="player-report-strengths")]),
                html.Div(
                    className="profile-card",
                    children=[html.H2("Points de vigilance"), html.Ul(id="player-report-watchpoints")],
                ),
            ],
        ),
        html.Div(
            className="profile-card",
            children=[
                html.H2("Métriques clés"),
                dash_table.DataTable(
                    id="player-report-metrics",
                    columns=[],
                    data=[],
                    style_table={"overflowX": "auto"},
                    style_cell={"textAlign": "left", "padding": "8px", "fontSize": "14px"},
                    style_header={"fontWeight": "bold", "backgroundColor": "#f3f4f6"},
                ),
            ],
        ),
        html.Div(
            className="profile-card",
            children=[
                html.H2("Joueurs similaires"),
                dash_table.DataTable(
                    id="player-report-similar",
                    columns=[],
                    data=[],
                    page_size=5,
                    style_table={"overflowX": "auto"},
                    style_cell={"textAlign": "left", "padding": "8px", "fontSize": "14px"},
                    style_header={"fontWeight": "bold", "backgroundColor": "#f3f4f6"},
                ),
            ],
        ),
        dcc.Store(id="player-report-store"),
        dcc.Download(id="player-report-download"),
    ],
)


@callback(
    Output("player-report-header", "children"),
    Output("player-report-summary", "children"),
    Output("player-report-roles", "children"),
    Output("player-report-dimensions", "children"),
    Output("player-report-strengths", "children"),
    Output("player-report-watchpoints", "children"),
    Output("player-report-metrics", "columns"),
    Output("player-report-metrics", "data"),
    Output("player-report-similar", "columns"),
    Output("player-report-similar", "data"),
    Output("player-report-store", "data"),
    Input("player-report-dropdown", "value"),
)
def update_player_report(selected_player_key):
    if not selected_player_key:
        return [], "", [], [], [], [], [], [], [], [], {}

    player_row = profile_df[profile_df["player_key"] == selected_player_key]
    if player_row.empty:
        return [], "", [], [], [], [], [], [], [], [], {}

    player_row = player_row.iloc[0]
    top_roles = get_top_roles(player_row, top_n=3)
    top_dimensions = get_top_dimensions(player_row, top_n=3)
    watch_dimensions = get_watch_dimensions(player_row, top_n=2)
    summary = build_profile_summary(player_row)

    header_cards = [
        html.Div(className="kpi-card", children=[html.H3("Joueur"), html.P(player_row["player"])]),
        html.Div(className="kpi-card", children=[html.H3("Équipe"), html.P(player_row["team"])]),
        html.Div(className="kpi-card", children=[html.H3("Championnat"), html.P(player_row["competition_name"])]),
        html.Div(className="kpi-card", children=[html.H3("Poste"), html.P(player_row["position"])]),
        html.Div(className="kpi-card", children=[html.H3("Minutes"), html.P(f"{player_row['minutes_played']:.1f}")]),
        html.Div(className="kpi-card", children=[html.H3("Matchs"), html.P(f"{int(player_row['matches_played'])}")]),
    ]

    roles_block = html.Ul([html.Li(f"{label}: {score:.3f}") for label, score in top_roles])
    dimensions_block = html.Ul(
        [html.Li(f"{label}: {float(player_row[column]):.3f}") for column, label in DIMENSION_LABELS.items()]
    )
    strengths_block = [html.Li(f"{label} ({score:.3f})") for label, score in top_dimensions]
    watchpoints_block = [html.Li(f"{label} ({score:.3f})") for label, score in watch_dimensions]

    metrics_df = pd.DataFrame(
        [
            {"Métrique": METRIC_LABELS[metric], "Valeur": round(float(player_row[metric]), 3)}
            for metric in REPORT_METRICS
            if metric in player_row.index and pd.notna(player_row[metric])
        ]
    )
    metrics_columns = [{"name": col, "id": col} for col in metrics_df.columns]
    metrics_data = metrics_df.to_dict("records")

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
            "similarity_score",
        ]
    ].rename(
        columns={
            "similar_player": "Joueur",
            "similar_player_team": "Équipe",
            "similar_player_competition": "Championnat",
            "similar_player_position": "Poste",
            "similarity_score": "Similarité",
        }
    )
    if not similar_display.empty:
        similar_display["Similarité"] = similar_display["Similarité"].round(4)
    similar_columns = [{"name": col, "id": col} for col in similar_display.columns]
    similar_data = similar_display.to_dict("records")

    store_data = {
        "player_key": selected_player_key,
        "player_name": player_row["player"],
        "summary": summary,
        "top_roles": top_roles,
        "strengths": top_dimensions,
        "watchpoints": watch_dimensions,
        "metrics": metrics_data,
        "similar": similar_data,
    }

    return (
        header_cards,
        summary,
        roles_block,
        dimensions_block,
        strengths_block,
        watchpoints_block,
        metrics_columns,
        metrics_data,
        similar_columns,
        similar_data,
        store_data,
    )


@callback(
    Output("player-report-download", "data"),
    Input("player-report-export", "n_clicks"),
    State("player-report-store", "data"),
    prevent_initial_call=True,
)
def export_player_report(n_clicks, report_store):
    if not n_clicks or not report_store:
        return dash.no_update

    player_row = profile_df[profile_df["player_key"] == report_store["player_key"]].iloc[0]
    metrics_df = pd.DataFrame(report_store["metrics"])
    similar_df = pd.DataFrame(report_store["similar"])
    html_content = build_report_html(
        player_row=player_row,
        summary=report_store["summary"],
        top_roles=report_store["top_roles"],
        strengths=report_store["strengths"],
        watchpoints=report_store["watchpoints"],
        metrics_df=metrics_df,
        similar_df=similar_df,
    )

    slug = report_store["player_name"].lower().replace(" ", "_").replace("'", "")
    return {
        "content": html_content,
        "filename": f"rapport_{slug}.html",
        "type": "text/html",
    }
