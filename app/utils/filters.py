import pandas as pd
from src.utils.player_profiles import select_primary_player_rows
from src.utils.position_groups import POSITION_GROUPS


def filter_by_minutes(df: pd.DataFrame, min_minutes: float | None) -> pd.DataFrame:
    if min_minutes is None:
        return df
    return df[df["minutes_played"] >= min_minutes].copy()


def filter_by_teams(df: pd.DataFrame, selected_teams: list[str] | None) -> pd.DataFrame:
    if not selected_teams:
        return df
    return df[df["team"].isin(selected_teams)].copy()


def filter_by_positions(df: pd.DataFrame, selected_positions: list[str] | None) -> pd.DataFrame:
    if not selected_positions:
        return df
    return df[df["position"].isin(selected_positions)].copy()


def filter_by_position_group(df: pd.DataFrame, selected_group: str | None) -> pd.DataFrame:
    if not selected_group:
        return df

    positions = POSITION_GROUPS.get(selected_group, [])
    return df[df["position"].isin(positions)].copy()


def deduplicate_players_by_primary_position(df: pd.DataFrame) -> pd.DataFrame:
    return select_primary_player_rows(df)
