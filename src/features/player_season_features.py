from pathlib import Path

import numpy as np
import pandas as pd

from src.utils.player_profiles import IDENTITY_COLUMNS, select_primary_player_rows


INPUT_PLAYER_MATCH_PATH = Path("data/processed/player_match_stats.parquet")
OUTPUT_PLAYER_SEASON_PATH = Path("data/processed/player_season_stats.parquet")


def load_player_match_stats(input_path: Path) -> pd.DataFrame:
    return pd.read_parquet(input_path)


def build_primary_position_table(player_match_df: pd.DataFrame) -> pd.DataFrame:
    position_df = (
        player_match_df
        .dropna(subset=["player", "team", "competition_name", "position"])
        .groupby(IDENTITY_COLUMNS + ["position"], dropna=False)
        .agg(
            position_matches_played=("match_id", "nunique"),
            position_rows=("match_id", "size"),
        )
        .reset_index()
    )

    position_df = select_primary_player_rows(position_df)

    return position_df[IDENTITY_COLUMNS + ["position", "position_matches_played", "position_rows"]]


def build_player_season_stats(player_match_df: pd.DataFrame) -> pd.DataFrame:
    metric_columns = [
        "shots",
        "goals",
        "xg",
        "passes_attempted",
        "passes_completed",
        "key_passes",
        "progressive_passes",
        "carries",
        "progressive_carries",
        "passes_into_final_third",
        "passes_into_box",
        "touches_in_final_third",
        "touches_in_box",
        "recoveries",
        "interceptions",
        "duels",
    ]

    season_df = (
        player_match_df
        .groupby(IDENTITY_COLUMNS, dropna=False)
        .agg(
            matches_played=("match_id", "nunique"),
            **{col: (col, "sum") for col in metric_columns}
        )
        .reset_index()
    )

    primary_position_df = build_primary_position_table(player_match_df)
    season_df = season_df.merge(primary_position_df, on=IDENTITY_COLUMNS, how="left")

    season_df["pass_completion_pct"] = np.where(
        season_df["passes_attempted"] > 0,
        (season_df["passes_completed"] / season_df["passes_attempted"]) * 100,
        np.nan
    )

    season_df["pass_completion_pct"] = season_df["pass_completion_pct"].round(2)
    season_df["xg"] = season_df["xg"].round(4)

    ordered_columns = [
        "player",
        "team",
        "competition_name",
        "position",
        "position_matches_played",
        "matches_played",
        "shots",
        "goals",
        "xg",
        "passes_attempted",
        "passes_completed",
        "pass_completion_pct",
        "key_passes",
        "progressive_passes",
        "carries",
        "progressive_carries",
        "passes_into_final_third",
        "passes_into_box",
        "touches_in_final_third",
        "touches_in_box",
        "recoveries",
        "interceptions",
        "duels",
    ]

    return season_df[ordered_columns].sort_values(
        ["competition_name", "team", "player"]
    ).reset_index(drop=True)


def save_parquet(df: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)


def run_pipeline() -> pd.DataFrame:
    print("Loading player-match stats...")
    player_match_df = load_player_match_stats(INPUT_PLAYER_MATCH_PATH)
    print(f"Player-match shape: {player_match_df.shape}")

    print("Building player-season stats...")
    player_season_df = build_player_season_stats(player_match_df)
    print(f"Player-season shape: {player_season_df.shape}")

    print("Saving player-season stats parquet...")
    save_parquet(player_season_df, OUTPUT_PLAYER_SEASON_PATH)

    print("Player-season feature pipeline completed successfully.")
    return player_season_df


if __name__ == "__main__":
    player_season_df = run_pipeline()

    print("\nOutput file created:")
    print(OUTPUT_PLAYER_SEASON_PATH)

    print("\nPreview:")
    print(player_season_df.head())
