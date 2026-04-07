from pathlib import Path

import numpy as np
import pandas as pd


INPUT_EVENTS_PATH = Path("data/interim/events_clean.parquet")
INPUT_MATCHES_PATH = Path("data/raw/matches.csv")
OUTPUT_PLAYER_MATCH_PATH = Path("data/processed/player_match_stats.parquet")


GOAL_X = 120
GOAL_Y = 40


def load_events(input_path: Path) -> pd.DataFrame:
    return pd.read_parquet(input_path)


def load_matches(input_path: Path) -> pd.DataFrame:
    return pd.read_csv(input_path)


def distance_to_goal(x: pd.Series, y: pd.Series) -> pd.Series:
    return np.sqrt((GOAL_X - x) ** 2 + (GOAL_Y - y) ** 2)


def add_feature_flags(events_df: pd.DataFrame) -> pd.DataFrame:
    df = events_df.copy()

    pass_shot_assist = df["pass_shot_assist"].fillna(False) if "pass_shot_assist" in df.columns else False

    df["is_shot"] = (df["type"] == "Shot").astype(int)
    df["is_goal"] = ((df["type"] == "Shot") & (df["shot_outcome"] == "Goal")).astype(int)
    df["is_pass"] = (df["type"] == "Pass").astype(int)
    df["is_completed_pass"] = ((df["type"] == "Pass") & (df["pass_outcome"].isna())).astype(int)
    df["is_key_pass"] = ((df["type"] == "Pass") & pass_shot_assist).astype(int)
    df["is_carry"] = (df["type"] == "Carry").astype(int)
    df["is_recovery"] = (df["type"] == "Ball Recovery").astype(int)
    df["is_interception"] = (df["type"] == "Interception").astype(int)
    df["is_duel"] = (df["type"] == "Duel").astype(int)

    df["xg"] = np.where(df["type"] == "Shot", df["shot_statsbomb_xg"], 0.0)
    df["xg"] = df["xg"].fillna(0.0)

    df["start_distance_to_goal"] = distance_to_goal(df["x"], df["y"])
    df["pass_end_distance_to_goal"] = distance_to_goal(df["pass_end_x"], df["pass_end_y"])
    df["carry_end_distance_to_goal"] = distance_to_goal(df["carry_end_x"], df["carry_end_y"])

    df["pass_progress_gain"] = df["start_distance_to_goal"] - df["pass_end_distance_to_goal"]
    df["carry_progress_gain"] = df["start_distance_to_goal"] - df["carry_end_distance_to_goal"]

    df["is_progressive_pass"] = ((df["type"] == "Pass") & (df["pass_progress_gain"] > 10)).astype(int)
    df["is_progressive_carry"] = ((df["type"] == "Carry") & (df["carry_progress_gain"] > 10)).astype(int)

    df["is_pass_into_final_third"] = ((df["type"] == "Pass") & (df["pass_end_x"] >= 80)).astype(int)
    df["is_pass_into_box"] = (
        (df["type"] == "Pass") &
        (df["pass_end_x"] >= 102) &
        (df["pass_end_y"].between(18, 62))
    ).astype(int)

    df["is_touch_in_final_third"] = (
        df["location"].notna() &
        (df["x"] >= 80)
    ).astype(int)

    df["is_touch_in_box"] = (
        df["location"].notna() &
        (df["x"] >= 102) &
        (df["y"].between(18, 62))
    ).astype(int)

    return df


def enrich_with_competition(events_df: pd.DataFrame, matches_df: pd.DataFrame) -> pd.DataFrame:
    match_cols = ["match_id", "competition_name"]
    matches_df = matches_df[match_cols].drop_duplicates()

    df = events_df.merge(matches_df, on="match_id", how="left")
    return df


def build_player_match_stats(events_df: pd.DataFrame) -> pd.DataFrame:
    group_cols = ["match_id", "competition_name", "player", "team", "position"]

    player_match_df = (
        events_df
        .dropna(subset=["player", "team", "competition_name"])
        .groupby(group_cols, dropna=False)
        .agg(
            shots=("is_shot", "sum"),
            goals=("is_goal", "sum"),
            xg=("xg", "sum"),
            passes_attempted=("is_pass", "sum"),
            passes_completed=("is_completed_pass", "sum"),
            key_passes=("is_key_pass", "sum"),
            progressive_passes=("is_progressive_pass", "sum"),
            carries=("is_carry", "sum"),
            progressive_carries=("is_progressive_carry", "sum"),
            passes_into_final_third=("is_pass_into_final_third", "sum"),
            passes_into_box=("is_pass_into_box", "sum"),
            touches_in_final_third=("is_touch_in_final_third", "sum"),
            touches_in_box=("is_touch_in_box", "sum"),
            recoveries=("is_recovery", "sum"),
            interceptions=("is_interception", "sum"),
            duels=("is_duel", "sum"),
        )
        .reset_index()
    )

    player_match_df["pass_completion_pct"] = np.where(
        player_match_df["passes_attempted"] > 0,
        (player_match_df["passes_completed"] / player_match_df["passes_attempted"]) * 100,
        np.nan
    )

    player_match_df["pass_completion_pct"] = player_match_df["pass_completion_pct"].round(2)
    player_match_df["xg"] = player_match_df["xg"].round(4)

    return player_match_df.sort_values(
        ["competition_name", "match_id", "team", "player"]
    ).reset_index(drop=True)


def save_parquet(df: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)


def run_pipeline() -> pd.DataFrame:
    print("Loading cleaned events...")
    events_df = load_events(INPUT_EVENTS_PATH)
    print(f"Events shape: {events_df.shape}")

    print("Loading matches...")
    matches_df = load_matches(INPUT_MATCHES_PATH)
    print(f"Matches shape: {matches_df.shape}")

    print("Adding event-level feature flags...")
    featured_events_df = add_feature_flags(events_df)

    print("Enriching with competition...")
    featured_events_df = enrich_with_competition(featured_events_df, matches_df)

    print("Aggregating to player-match level...")
    player_match_df = build_player_match_stats(featured_events_df)
    print(f"Player match stats shape: {player_match_df.shape}")

    print("Saving player match stats parquet...")
    save_parquet(player_match_df, OUTPUT_PLAYER_MATCH_PATH)

    print("Player match feature pipeline completed successfully.")
    return player_match_df


if __name__ == "__main__":
    player_match_df = run_pipeline()

    print("\nOutput file created:")
    print(OUTPUT_PLAYER_MATCH_PATH)

    print("\nPreview:")
    print(player_match_df.head())