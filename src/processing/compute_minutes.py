# src/processing/compute_minutes.py

import ast
from pathlib import Path

import numpy as np
import pandas as pd


INPUT_LINEUPS_PATH = Path("data/raw/lineups.csv")
OUTPUT_PLAYER_MATCH_MINUTES_PATH = Path("data/interim/player_match_minutes.parquet")


def load_lineups(input_path: Path) -> pd.DataFrame:
    """
    Load raw lineups CSV.
    """
    return pd.read_csv(input_path, low_memory=False)


def parse_positions(value):
    """
    Parse the 'positions' column from string to Python list.
    """
    if pd.isna(value):
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, str):
        value = value.strip()
        if not value:
            return []
        try:
            parsed = ast.literal_eval(value)
            if isinstance(parsed, list):
                return parsed
        except (ValueError, SyntaxError):
            return []

    return []


def safe_minute(value, default=None):
    """
    Safely convert minute-like values to float.

    Supported formats:
    - numeric values: 12, 45.0
    - numeric strings: "12", "45.0"
    - clock strings: "00:00", "45:30"
    """
    if value is None or pd.isna(value):
        return default

    if isinstance(value, (int, float)):
        return float(value)

    if isinstance(value, str):
        value = value.strip()
        if not value:
            return default

        if ":" in value:
            try:
                minutes, seconds = value.split(":")
                return float(minutes) + float(seconds) / 60
            except ValueError:
                return default

        try:
            return float(value)
        except ValueError:
            return default

    return default


def compute_player_minutes_from_positions(positions: list) -> dict:
    """
    Compute minutes played and starter flag from position segments.

    Assumptions:
    - each element in positions is a dict describing one playing segment
    - segment duration = to - from
    - if 'to' is missing, we assume end at minute 90 for V1

    Returns a dict with:
    - minutes_played
    - is_starter
    - start_minute
    - end_minute
    """
    if not positions:
        return {
            "minutes_played": 0.0,
            "is_starter": 0,
            "start_minute": np.nan,
            "end_minute": np.nan,
        }

    segments = []
    start_minutes = []
    end_minutes = []

    for pos in positions:
        if not isinstance(pos, dict):
            continue

        start_min = safe_minute(pos.get("from"), default=np.nan)
        end_min = safe_minute(pos.get("to"), default=90.0)

        if pd.isna(start_min):
            continue

        if pd.isna(end_min):
            end_min = 90.0

        if end_min < start_min:
            continue

        segments.append(end_min - start_min)
        start_minutes.append(start_min)
        end_minutes.append(end_min)

    if not segments:
        return {
            "minutes_played": 0.0,
            "is_starter": 0,
            "start_minute": np.nan,
            "end_minute": np.nan,
        }

    start_minute = min(start_minutes)
    end_minute = max(end_minutes)
    minutes_played = sum(segments)

    # V1 rule: starter if first observed segment starts at 0
    is_starter = int(start_minute == 0)

    return {
        "minutes_played": round(minutes_played, 2),
        "is_starter": is_starter,
        "start_minute": start_minute,
        "end_minute": end_minute,
    }


def build_player_match_minutes(lineups_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build player-match minutes table from lineups.
    """
    df = lineups_df.copy()

    df["positions"] = df["positions"].apply(parse_positions)

    minutes_records = df["positions"].apply(compute_player_minutes_from_positions)
    minutes_df = pd.DataFrame(minutes_records.tolist(), index=df.index)

    df = pd.concat([df, minutes_df], axis=1)

    keep_cols = [
        "match_id",
        "player_id",
        "player_name",
        "player_nickname",
        "team_name",
        "minutes_played",
        "is_starter",
        "start_minute",
        "end_minute",
    ]

    available_cols = [col for col in keep_cols if col in df.columns]
    df = df[available_cols].copy()

    df = df.sort_values(
        ["match_id", "team_name", "player_name"]
    ).reset_index(drop=True)

    return df


def save_parquet(df: pd.DataFrame, output_path: Path) -> None:
    """
    Save dataframe as parquet.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)


def run_pipeline() -> pd.DataFrame:
    """
    Run full minutes computation pipeline.
    """
    print("Loading lineups...")
    lineups_df = load_lineups(INPUT_LINEUPS_PATH)
    print(f"Lineups shape: {lineups_df.shape}")

    print("Building player-match minutes table...")
    player_match_minutes_df = build_player_match_minutes(lineups_df)
    print(f"Player-match minutes shape: {player_match_minutes_df.shape}")

    print("Saving player-match minutes parquet...")
    save_parquet(player_match_minutes_df, OUTPUT_PLAYER_MATCH_MINUTES_PATH)

    print("Minutes pipeline completed successfully.")
    return player_match_minutes_df


if __name__ == "__main__":
    player_match_minutes_df = run_pipeline()

    print("\nOutput file created:")
    print(OUTPUT_PLAYER_MATCH_MINUTES_PATH)

    print("\nPreview:")
    print(player_match_minutes_df.head())