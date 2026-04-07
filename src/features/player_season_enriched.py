# src/features/player_season_enriched.py

from pathlib import Path

import numpy as np
import pandas as pd


INPUT_PLAYER_SEASON_PATH = Path("data/processed/player_season_stats.parquet")
INPUT_PLAYER_MATCH_MINUTES_PATH = Path("data/interim/player_match_minutes.parquet")
INPUT_MATCHES_PATH = Path("data/raw/matches.csv")
OUTPUT_PLAYER_SEASON_ENRICHED_PATH = Path("data/processed/player_season_enriched.parquet")


PER90_COLUMNS = [
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


def load_player_season_stats(input_path: Path) -> pd.DataFrame:
    """
    Load player season stats table.
    """
    return pd.read_parquet(input_path)


def load_player_match_minutes(input_path: Path) -> pd.DataFrame:
    """
    Load player match minutes table.
    """
    return pd.read_parquet(input_path)


def load_matches(input_path: Path) -> pd.DataFrame:
    """
    Load matches table to recover competition context.
    """
    return pd.read_csv(input_path)


def build_player_season_minutes(
    player_match_minutes_df: pd.DataFrame,
    matches_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Aggregate player-match minutes to player/team/competition season level.
    """
    match_context = matches_df[["match_id", "competition_name"]].drop_duplicates()

    minutes_df = player_match_minutes_df.merge(
        match_context,
        on="match_id",
        how="left",
    )

    season_minutes_df = (
        minutes_df
        .groupby(["player_name", "team_name", "competition_name"], dropna=False)
        .agg(
            matches_in_minutes_table=("match_id", "nunique"),
            starts=("is_starter", "sum"),
            minutes_played=("minutes_played", "sum"),
        )
        .reset_index()
        .rename(columns={"player_name": "player", "team_name": "team"})
    )

    season_minutes_df["minutes_played"] = season_minutes_df["minutes_played"].round(2)

    return season_minutes_df


def add_per90_metrics(df: pd.DataFrame, metric_columns: list[str]) -> pd.DataFrame:
    """
    Add per-90 metrics for selected columns.
    """
    df = df.copy()

    for col in metric_columns:
        per90_col = f"{col}_per90"
        df[per90_col] = np.where(
            df["minutes_played"] > 0,
            (df[col] / df["minutes_played"]) * 90,
            np.nan
        )

        if col == "xg":
            df[per90_col] = df[per90_col].round(4)
        else:
            df[per90_col] = df[per90_col].round(2)

    return df


def build_enriched_player_season(
    player_season_df: pd.DataFrame,
    player_match_minutes_df: pd.DataFrame,
    matches_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Merge season stats with season minutes and compute per-90 metrics.
    """
    season_minutes_df = build_player_season_minutes(player_match_minutes_df, matches_df)

    enriched_df = player_season_df.merge(
        season_minutes_df,
        on=["player", "team", "competition_name"],
        how="left"
    )

    enriched_df["starts"] = enriched_df["starts"].fillna(0).astype(int)
    enriched_df["minutes_played"] = enriched_df["minutes_played"].fillna(0.0)
    enriched_df["matches_in_minutes_table"] = enriched_df["matches_in_minutes_table"].fillna(0).astype(int)

    enriched_df = add_per90_metrics(enriched_df, PER90_COLUMNS)

    # Minimum-minutes flag for scouting reliability
    enriched_df["meets_minimum_minutes_900"] = (enriched_df["minutes_played"] >= 900).astype(int)

    return enriched_df.sort_values(["team", "player"]).reset_index(drop=True)


def save_parquet(df: pd.DataFrame, output_path: Path) -> None:
    """
    Save dataframe as parquet.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)


def run_pipeline() -> pd.DataFrame:
    """
    Run full enrichment pipeline for player-season table.
    """
    print("Loading player-season stats...")
    player_season_df = load_player_season_stats(INPUT_PLAYER_SEASON_PATH)
    print(f"Player-season stats shape: {player_season_df.shape}")

    print("Loading player-match minutes...")
    player_match_minutes_df = load_player_match_minutes(INPUT_PLAYER_MATCH_MINUTES_PATH)
    print(f"Player-match minutes shape: {player_match_minutes_df.shape}")

    print("Loading matches...")
    matches_df = load_matches(INPUT_MATCHES_PATH)
    print(f"Matches shape: {matches_df.shape}")

    print("Building enriched player-season table...")
    enriched_df = build_enriched_player_season(player_season_df, player_match_minutes_df, matches_df)
    print(f"Enriched player-season shape: {enriched_df.shape}")

    print("Saving enriched player-season parquet...")
    save_parquet(enriched_df, OUTPUT_PLAYER_SEASON_ENRICHED_PATH)

    print("Player-season enrichment pipeline completed successfully.")
    return enriched_df


if __name__ == "__main__":
    enriched_df = run_pipeline()

    print("\nOutput file created:")
    print(OUTPUT_PLAYER_SEASON_ENRICHED_PATH)

    print("\nPreview:")
    print(enriched_df.head())
