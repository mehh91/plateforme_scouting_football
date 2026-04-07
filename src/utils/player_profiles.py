from __future__ import annotations

import pandas as pd

from src.utils.position_groups import POSITION_PRIORITY


IDENTITY_COLUMNS = ["player", "team", "competition_name"]


def add_player_key(
    df: pd.DataFrame,
    output_col: str = "player_key",
    player_col: str = "player",
    team_col: str = "team",
    competition_col: str = "competition_name",
) -> pd.DataFrame:
    """
    Add a stable key for one seasonal player profile.
    """
    required_cols = [player_col, team_col, competition_col]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        return df.copy()

    dff = df.copy()
    dff[output_col] = (
        dff[player_col].fillna("").astype(str)
        + "||"
        + dff[team_col].fillna("").astype(str)
        + "||"
        + dff[competition_col].fillna("").astype(str)
    )
    return dff


def select_primary_player_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    Keep one main seasonal row per player/team/competition.

    Sorting priority:
    1) more matches in the selected position if available
    2) more season matches if available
    3) more minutes if available
    4) higher business priority as a final tie-breaker
    """
    missing_cols = [col for col in IDENTITY_COLUMNS if col not in df.columns]
    if missing_cols:
        return df.copy()

    dff = df.copy()

    if "position" in dff.columns:
        dff["position_priority"] = dff["position"].map(POSITION_PRIORITY).fillna(0)
    else:
        dff["position_priority"] = 0

    if "position_matches_played" not in dff.columns:
        dff["position_matches_played"] = 0

    if "matches_played" not in dff.columns:
        dff["matches_played"] = 0

    if "minutes_played" not in dff.columns:
        dff["minutes_played"] = 0.0

    if "position_rows" not in dff.columns:
        dff["position_rows"] = 0

    dff = dff.sort_values(
        IDENTITY_COLUMNS + ["position_matches_played", "position_rows", "matches_played", "minutes_played", "position_priority"],
        ascending=[True, True, True, False, False, False, False, False],
    )

    dff = dff.drop_duplicates(subset=IDENTITY_COLUMNS, keep="first").reset_index(drop=True)

    return dff.drop(columns=["position_priority"], errors="ignore")
