import dash
import pandas as pd
from dash import dash_table, html

from app.utils.data_loader import load_player_similarity, load_primary_player_role_scores
from app.utils.labels import ROLE_LABELS
from app.utils.recruitment import apply_recruitment_filters, build_shortlist_table


dash.register_page(__name__, path="/use-cases", name="Cas d'usage")


df = load_primary_player_role_scores()
similarity_df = load_player_similarity()


def find_player_key(name_fragment: str) -> str | None:
    matches = df[df["player"].str.contains(name_fragment, case=False, na=False)].copy()
    if matches.empty:
        return None
    matches = matches.sort_values("minutes_played", ascending=False)
    return matches.iloc[0]["player_key"]


def scenario_table(
    selected_role: str,
    selected_leagues,
    selected_position_group: str | None,
    min_minutes: int,
    top_n: int,
    reference_player_key: str | None = None,
) -> pd.DataFrame:
    filtered_df = apply_recruitment_filters(
        df=df,
        selected_leagues=selected_leagues,
        selected_position_group=selected_position_group,
        min_minutes=min_minutes,
    )

    result = build_shortlist_table(
        base_df=filtered_df,
        similarity_df=similarity_df,
        selected_role=selected_role,
        reference_player_key=reference_player_key,
        top_n=top_n,
        exclude_reference_team=bool(reference_player_key),
    )

    display_df = result[["rank", "player", "team", "competition_name", "position", "minutes_played", "role_score", "reference_similarity"]].copy()
    display_df = display_df.rename(
        columns={
            "rank": "Rang",
            "player": "Joueur",
            "team": "Équipe",
            "competition_name": "Championnat",
            "position": "Poste",
            "minutes_played": "Minutes",
            "role_score": ROLE_LABELS[selected_role],
            "reference_similarity": "Similarité réf.",
        }
    )
    return display_df.astype(object).where(pd.notna(display_df), None)


scenarios = [
    {
        "title": "Scénario 1 - Cibler un ailier créatif en Ligue 1",
        "description": "Filtrer rapidement une population pour identifier des titulaires offensifs capables de créer et de peser dans le dernier tiers.",
        "role": "creative_winger_score",
        "leagues": ["Ligue 1"],
        "position_group": "Ailiers",
        "minutes": 1200,
        "top_n": 5,
        "reference_player_key": None,
    },
    {
        "title": "Scénario 2 - Chercher un latéral progressif de remplacement",
        "description": "Partir d'un joueur référence et trouver des profils proches dans d'autres clubs pour alimenter une short-list de remplacement.",
        "role": "progressive_fullback_score",
        "leagues": None,
        "position_group": "Latéraux",
        "minutes": 1200,
        "top_n": 5,
        "reference_player_key": find_player_key("Aaron Cresswell"),
    },
    {
        "title": "Scénario 3 - Comparer des avant-centres de surface multi-ligues",
        "description": "Produire une short-list d'attaquants centrés sur la surface avec un filtre minutes pour limiter le bruit d'échantillon.",
        "role": "penalty_box_forward_score",
        "leagues": ["Serie A", "1. Bundesliga", "Ligue 1"],
        "position_group": "Attaquants",
        "minutes": 1500,
        "top_n": 5,
        "reference_player_key": None,
    },
]


scenario_blocks = []
for scenario in scenarios:
    table_df = scenario_table(
        selected_role=scenario["role"],
        selected_leagues=scenario["leagues"],
        selected_position_group=scenario["position_group"],
        min_minutes=scenario["minutes"],
        top_n=scenario["top_n"],
        reference_player_key=scenario["reference_player_key"],
    )

    scenario_blocks.append(
        html.Div(
            className="profile-card",
            children=[
                html.H2(scenario["title"]),
                html.P(scenario["description"]),
                html.Div(
                    className="summary-box",
                    children=[
                        html.Strong(f"Rôle cible : {ROLE_LABELS[scenario['role']]}"),
                        html.Span(f"  |  Championnats : {', '.join(scenario['leagues'])}" if scenario["leagues"] else "  |  Championnats : Top 5"),
                        html.Span(f"  |  Groupe de poste : {scenario['position_group']}"),
                        html.Span(f"  |  Minutes minimum : {scenario['minutes']}"),
                    ],
                ),
                dash_table.DataTable(
                    columns=[{"name": col, "id": col} for col in table_df.columns],
                    data=table_df.to_dict("records"),
                    page_size=scenario["top_n"],
                    style_table={"overflowX": "auto"},
                    style_cell={"textAlign": "left", "padding": "8px", "fontSize": "14px"},
                    style_header={"fontWeight": "bold", "backgroundColor": "#f3f4f6"},
                ),
            ],
        )
    )


layout = html.Div(
    className="page-container",
    children=[
        html.H1("Cas d'usage recrutement"),
        html.P(
            "Cette page montre comment la plateforme peut être mobilisée dans des besoins concrets de cellule recrutement : "
            "ciblage d'une population, recherche d'un remplaçant, benchmark multi-ligues."
        ),
        *scenario_blocks,
    ],
)
