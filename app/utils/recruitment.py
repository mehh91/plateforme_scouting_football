from __future__ import annotations

import pandas as pd

from app.utils.filters import (
    deduplicate_players_by_primary_position,
    filter_by_minutes,
    filter_by_position_group,
    filter_by_positions,
    filter_by_teams,
)
from app.utils.scouting import build_shortlist_rationale


def filter_by_leagues(df_in: pd.DataFrame, selected_leagues) -> pd.DataFrame:
    if not selected_leagues:
        return df_in
    return df_in[df_in["competition_name"].isin(selected_leagues)].copy()


def build_team_options(dff: pd.DataFrame):
    return [{"label": team, "value": team} for team in sorted(dff["team"].dropna().unique())]


def build_position_options(dff: pd.DataFrame):
    return [{"label": pos, "value": pos} for pos in sorted(dff["position"].dropna().unique())]


def build_player_options(dff: pd.DataFrame):
    return [
        {
            "label": f"{row['player']} - {row['team']} ({row['competition_name']})",
            "value": row["player_key"],
        }
        for _, row in dff.sort_values(["player", "team", "competition_name"]).iterrows()
    ]


def apply_recruitment_filters(
    df: pd.DataFrame,
    selected_leagues=None,
    selected_teams=None,
    selected_position_group=None,
    selected_positions=None,
    min_minutes=None,
) -> pd.DataFrame:
    dff = df.copy()
    dff = filter_by_leagues(dff, selected_leagues)
    dff = filter_by_minutes(dff, min_minutes)
    dff = filter_by_teams(dff, selected_teams)
    dff = filter_by_position_group(dff, selected_position_group)
    dff = filter_by_positions(dff, selected_positions)
    dff = deduplicate_players_by_primary_position(dff)
    return dff


def build_shortlist_table(
    base_df: pd.DataFrame,
    similarity_df: pd.DataFrame,
    selected_role: str,
    reference_player_key: str | None,
    top_n: int,
    exclude_reference_team: bool,
) -> pd.DataFrame:
    shortlist_df = base_df.copy()

    shortlist_df["role_score"] = shortlist_df[selected_role]
    shortlist_df["role_fit_pct"] = shortlist_df["role_score"].rank(pct=True) * 100
    shortlist_df["reference_similarity"] = pd.NA
    shortlist_df["reference_similarity_pct"] = pd.NA

    reference_label = None

    if reference_player_key:
        reference_row = base_df[base_df["player_key"] == reference_player_key]
        if not reference_row.empty:
            reference_row = reference_row.iloc[0]
            reference_label = f"{reference_row['player']} - {reference_row['team']}"

            if exclude_reference_team:
                shortlist_df = shortlist_df[shortlist_df["team"] != reference_row["team"]].copy()

            sim_subset = similarity_df[similarity_df["player_key"] == reference_player_key][
                ["similar_player_key", "similarity_score"]
            ].rename(
                columns={
                    "similar_player_key": "player_key",
                    "similarity_score": "reference_similarity",
                }
            )

            shortlist_df = shortlist_df.merge(sim_subset, on="player_key", how="left", suffixes=("", "_from_ref"))
            if "reference_similarity_from_ref" in shortlist_df.columns:
                shortlist_df["reference_similarity"] = shortlist_df["reference_similarity_from_ref"].combine_first(
                    shortlist_df["reference_similarity"]
                )
                shortlist_df = shortlist_df.drop(columns=["reference_similarity_from_ref"])

            shortlist_df["reference_similarity"] = pd.to_numeric(shortlist_df["reference_similarity"], errors="coerce")
            shortlist_df["reference_similarity_pct"] = shortlist_df["reference_similarity"].rank(pct=True) * 100
            shortlist_df["shortlist_fit"] = (
                shortlist_df["role_fit_pct"] * 0.7
                + shortlist_df["reference_similarity_pct"].fillna(0) * 0.3
            )
        else:
            shortlist_df["shortlist_fit"] = shortlist_df["role_fit_pct"]
    else:
        shortlist_df["shortlist_fit"] = shortlist_df["role_fit_pct"]

    shortlist_df = shortlist_df[shortlist_df["player_key"] != reference_player_key].copy()
    shortlist_df["reference_similarity"] = pd.to_numeric(shortlist_df["reference_similarity"], errors="coerce")
    shortlist_df["shortlist_fit"] = shortlist_df["shortlist_fit"].round(2)
    shortlist_df["role_score"] = shortlist_df["role_score"].round(3)
    shortlist_df["reference_similarity"] = shortlist_df["reference_similarity"].round(4)
    shortlist_df["minutes_played"] = shortlist_df["minutes_played"].round(1)
    shortlist_df["rationale"] = shortlist_df.apply(
        lambda row: build_shortlist_rationale(row, selected_role),
        axis=1,
    )

    shortlist_df = shortlist_df.sort_values(
        ["shortlist_fit", "role_score", "minutes_played"],
        ascending=[False, False, False],
    ).head(top_n)

    shortlist_df["rank"] = range(1, len(shortlist_df) + 1)
    shortlist_df["reference_label"] = reference_label

    return shortlist_df
