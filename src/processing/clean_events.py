# src/processing/clean_events.py

import ast
from pathlib import Path

import numpy as np
import pandas as pd


RAW_EVENTS_PATH = Path("data/raw/events.csv")
PROCESSED_EVENTS_PATH = Path("data/interim/events_clean.parquet")


COLUMNS_TO_KEEP = [
    # Core context
    "match_id",
    "id",
    "index",
    "period",
    "timestamp",
    "minute",
    "second",
    "type",
    "possession",
    "possession_team",
    "play_pattern",
    "team",
    "player",
    "position",
    "duration",
    "under_pressure",
    "counterpress",

    # Spatial
    "location",

    # Pass
    "pass_end_location",
    "pass_length",
    "pass_angle",
    "pass_height",
    "pass_outcome",
    "pass_type",
    "pass_body_part",
    "pass_cross",
    "pass_switch",
    "pass_shot_assist",
    "pass_goal_assist",

    # Shot
    "shot_end_location",
    "shot_statsbomb_xg",
    "shot_outcome",
    "shot_body_part",
    "shot_type",
    "shot_first_time",
    "shot_one_on_one",
    "shot_open_goal",

    # Carry
    "carry_end_location",

    # Dribble / Duel / Interception / Recovery
    "dribble_outcome",
    "duel_type",
    "interception_outcome",
    "ball_recovery_recovery_failure",
]


def load_events_csv(input_path: Path) -> pd.DataFrame:
    """
    Load raw events CSV.

    low_memory=False avoids fragmented dtype inference and reduces
    mixed-type warnings when reading large wide CSV files.
    """
    return pd.read_csv(input_path, low_memory=False)


def keep_relevant_columns(df: pd.DataFrame, columns_to_keep: list[str]) -> pd.DataFrame:
    """
    Keep only columns that are both requested and present in the dataframe.
    """
    available_columns = [col for col in columns_to_keep if col in df.columns]
    return df[available_columns].copy()


def parse_coordinate(value):
    """
    Safely parse a coordinate value stored as a string like '[61.0, 40.1]'.

    Returns:
        - list/tuple if parsing succeeds
        - np.nan if value is missing or malformed
    """
    if pd.isna(value):
        return np.nan

    if isinstance(value, (list, tuple)):
        return value

    if isinstance(value, str):
        value = value.strip()
        if not value:
            return np.nan
        try:
            parsed = ast.literal_eval(value)
            if isinstance(parsed, (list, tuple)):
                return parsed
        except (ValueError, SyntaxError):
            return np.nan

    return np.nan


def extract_xy(value):
    """
    Extract x and y from a 2D coordinate.
    Returns (np.nan, np.nan) if unavailable.
    """
    if isinstance(value, (list, tuple)) and len(value) >= 2:
        return value[0], value[1]
    return np.nan, np.nan


def extract_xyz_end(value):
    """
    Extract x and y from an end-location coordinate.
    Works for:
        - pass_end_location: usually [x, y]
        - carry_end_location: usually [x, y]
        - shot_end_location: may be [x, y, z]

    Returns only x and y for the V1 pipeline.
    """
    if isinstance(value, (list, tuple)) and len(value) >= 2:
        return value[0], value[1]
    return np.nan, np.nan


def add_location_coordinates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Parse coordinate columns and create explicit numeric x/y columns.
    """
    df = df.copy()

    coordinate_columns = [
        "location",
        "pass_end_location",
        "carry_end_location",
        "shot_end_location",
    ]

    for col in coordinate_columns:
        if col in df.columns:
            df[col] = df[col].apply(parse_coordinate)

    if "location" in df.columns:
        df[["x", "y"]] = pd.DataFrame(
            df["location"].apply(extract_xy).tolist(),
            index=df.index
        )

    if "pass_end_location" in df.columns:
        df[["pass_end_x", "pass_end_y"]] = pd.DataFrame(
            df["pass_end_location"].apply(extract_xyz_end).tolist(),
            index=df.index
        )

    if "carry_end_location" in df.columns:
        df[["carry_end_x", "carry_end_y"]] = pd.DataFrame(
            df["carry_end_location"].apply(extract_xyz_end).tolist(),
            index=df.index
        )

    if "shot_end_location" in df.columns:
        df[["shot_end_x", "shot_end_y"]] = pd.DataFrame(
            df["shot_end_location"].apply(extract_xyz_end).tolist(),
            index=df.index
        )

    return df


def cast_boolean_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert selected flag columns to pandas nullable boolean dtype when present.
    """
    df = df.copy()

    boolean_columns = [
        "under_pressure",
        "counterpress",
        "pass_cross",
        "pass_switch",
        "pass_shot_assist",
        "pass_goal_assist",
        "shot_first_time",
        "shot_one_on_one",
        "shot_open_goal",
        "ball_recovery_recovery_failure",
    ]

    for col in boolean_columns:
        if col in df.columns:
            df[col] = df[col].astype("boolean")

    return df


def cast_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert selected columns to numeric where relevant.
    """
    df = df.copy()

    numeric_columns = [
        "match_id",
        "index",
        "period",
        "minute",
        "second",
        "possession",
        "duration",
        "pass_length",
        "pass_angle",
        "shot_statsbomb_xg",
        "x",
        "y",
        "pass_end_x",
        "pass_end_y",
        "carry_end_x",
        "carry_end_y",
        "shot_end_x",
        "shot_end_y",
    ]

    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def sort_events(df: pd.DataFrame) -> pd.DataFrame:
    """
    Sort events in match order.
    """
    sort_cols = [col for col in ["match_id", "period", "minute", "second", "index"] if col in df.columns]
    return df.sort_values(sort_cols).reset_index(drop=True)


def save_as_parquet(df: pd.DataFrame, output_path: Path) -> None:
    """
    Save cleaned dataframe as parquet.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)


def run_pipeline(input_path: Path, output_path: Path) -> pd.DataFrame:
    """
    Run the full cleaning pipeline.
    """
    print("Loading raw events CSV...")
    events_df = load_events_csv(input_path)
    print(f"Raw shape: {events_df.shape}")

    print("Keeping relevant columns...")
    events_df = keep_relevant_columns(events_df, COLUMNS_TO_KEEP)
    print(f"Shape after column selection: {events_df.shape}")

    print("Parsing coordinates and creating x/y columns...")
    events_df = add_location_coordinates(events_df)

    print("Casting boolean columns...")
    events_df = cast_boolean_columns(events_df)

    print("Casting numeric columns...")
    events_df = cast_numeric_columns(events_df)

    print("Sorting events...")
    events_df = sort_events(events_df)

    print("Saving parquet...")
    save_as_parquet(events_df, output_path)

    print("Cleaning pipeline completed successfully.")
    print(f"Final shape: {events_df.shape}")

    return events_df


if __name__ == "__main__":
    clean_df = run_pipeline(RAW_EVENTS_PATH, PROCESSED_EVENTS_PATH)

    print("\nOutput file created:")
    print(PROCESSED_EVENTS_PATH)

    print("\nColumns:")
    print(clean_df.columns.tolist())