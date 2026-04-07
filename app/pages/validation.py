import dash
import pandas as pd
from dash import dash_table, html

from app.utils.data_loader import load_player_similarity, load_primary_player_role_scores
from app.utils.labels import ROLE_LABELS, ROLE_TARGET_GROUPS
from src.utils.position_groups import assign_position_group


dash.register_page(__name__, path="/validation", name="Validation")


df = load_primary_player_role_scores().copy()
similarity_df = load_player_similarity()
df["position_group"] = df["position"].apply(assign_position_group)


def build_role_validation_table(top_n: int = 30) -> pd.DataFrame:
    rows = []
    eligible_df = df[df["minutes_played"] >= 900].copy()

    for role_column, role_label in ROLE_LABELS.items():
        if role_column not in eligible_df.columns:
            continue
        top_df = eligible_df.sort_values(role_column, ascending=False).head(top_n)
        alignment_rate = top_df["position_group"].isin(ROLE_TARGET_GROUPS[role_column]).mean() * 100
        rows.append(
            {
                "Rôle": role_label,
                "Groupes cibles": ", ".join(ROLE_TARGET_GROUPS[role_column]),
                f"Top {top_n} aligné": round(alignment_rate, 1),
                "Meilleur profil": top_df.iloc[0]["player"] if not top_df.empty else None,
                "Club": top_df.iloc[0]["team"] if not top_df.empty else None,
            }
        )

    return pd.DataFrame(rows).sort_values(f"Top {top_n} aligné", ascending=False)


def build_similarity_examples() -> list[dict[str, object]]:
    examples = []
    candidate_roles = ["creative_winger_score", "deep_lying_playmaker_score", "progressive_fullback_score"]

    for role_column in candidate_roles:
        role_top = df[df["minutes_played"] >= 900].sort_values(role_column, ascending=False).head(1)
        if role_top.empty:
            continue

        player_row = role_top.iloc[0]
        similar = similarity_df[similarity_df["player_key"] == player_row["player_key"]].sort_values("similarity_score", ascending=False).head(3)
        examples.append(
            {
                "role": ROLE_LABELS[role_column],
                "player": player_row["player"],
                "team": player_row["team"],
                "position": player_row["position"],
                "similar": similar[["similar_player", "similar_player_team", "similar_player_position", "similarity_score"]].rename(
                    columns={
                        "similar_player": "Joueur similaire",
                        "similar_player_team": "Équipe",
                        "similar_player_position": "Poste",
                        "similarity_score": "Similarité",
                    }
                ),
            }
        )

    return examples


validation_df = build_role_validation_table(top_n=30)
similarity_examples = build_similarity_examples()


example_blocks = []
for example in similarity_examples:
    similar_df = example["similar"].copy()
    similar_df["Similarité"] = similar_df["Similarité"].round(4)
    example_blocks.append(
        html.Div(
            className="profile-card",
            children=[
                html.H2(f"Exemple de similarité - {example['role']}"),
                html.P(
                    f"Profil de référence : {example['player']} ({example['team']}, {example['position']}). "
                    "Objectif : vérifier que les voisins proposés restent plausibles à la lecture football."
                ),
                dash_table.DataTable(
                    columns=[{"name": col, "id": col} for col in similar_df.columns],
                    data=similar_df.to_dict("records"),
                    page_size=3,
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
        html.H1("Validation football"),
        html.P(
            "Cette page sert à objectiver la cohérence des sorties du modèle. "
            "Elle ne remplace pas la vidéo, mais permet de vérifier que les tops et les comparables "
            "restent cohérents avec les familles de poste visées."
        ),
        html.Div(
            className="kpi-grid",
            children=[
                html.Div(className="kpi-card", children=[html.H3("Rôles évalués"), html.P(f"{len(validation_df)}")]),
                html.Div(className="kpi-card", children=[html.H3("Seuil validation"), html.P("900+")]),
                html.Div(className="kpi-card", children=[html.H3("Population testée"), html.P(f"{int((df['minutes_played'] >= 900).sum())}")]),
                html.Div(className="kpi-card", children=[html.H3("Lectures de similarité"), html.P(f"{len(similarity_examples)}")]),
            ],
        ),
        html.Div(
            className="profile-card",
            children=[
                html.H2("Alignement rôle / famille de poste"),
                html.P(
                    "Lecture : pour chaque rôle, on mesure la part des Top 30 profils qui appartiennent bien à la famille de poste cible. "
                    "Cette validation vérifie que le ranking reste interprétable."
                ),
                dash_table.DataTable(
                    columns=[{"name": col, "id": col} for col in validation_df.columns],
                    data=validation_df.to_dict("records"),
                    page_size=10,
                    style_table={"overflowX": "auto"},
                    style_cell={"textAlign": "left", "padding": "8px", "fontSize": "14px"},
                    style_header={"fontWeight": "bold", "backgroundColor": "#f3f4f6"},
                ),
            ],
        ),
        *example_blocks,
        html.Div(
            className="profile-card",
            children=[
                html.H2("Lecture critique"),
                html.Ul(
                    [
                        html.Li("Une bonne cohérence quantitative ne dispense jamais d'une validation vidéo."),
                        html.Li("Les rôles restent sensibles au choix des pondérations et à la couverture de données disponible."),
                        html.Li("La validation sert ici à montrer que le moteur est auditable et perfectible, pas à prétendre à l'infaillibilité."),
                    ]
                ),
            ],
        ),
    ],
)
