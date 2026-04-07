# src/ingestion/load_lineups.py

from pathlib import Path

import pandas as pd
from statsbombpy import sb


INPUT_MATCHES_PATH = Path("data/raw/matches.csv")
OUTPUT_LINEUPS_PATH = Path("data/raw/lineups.csv")


def load_matches(input_path: Path) -> pd.DataFrame:
    """
    Load matches CSV to retrieve match_ids.
    """
    return pd.read_csv(input_path)


def load_lineups_for_match(match_id: int) -> pd.DataFrame:
    """
    Load lineups for a single match.
    """
    try:
        lineups = sb.lineups(match_id=match_id)

        all_lineups = []

        for team_name, df in lineups.items():
            df = df.copy()
            df["team_name"] = team_name
            df["match_id"] = match_id
            all_lineups.append(df)

        return pd.concat(all_lineups, ignore_index=True)

    except Exception as e:
        print(f"Error loading lineups for match {match_id}: {e}")
        return pd.DataFrame()


def load_all_lineups(matches_df: pd.DataFrame) -> pd.DataFrame:
    """
    Load lineups for all matches.
    """
    match_ids = matches_df["match_id"].unique()

    all_lineups = []

    print(f"Total matches to process: {len(match_ids)}")

    for i, match_id in enumerate(match_ids):
        if i % 50 == 0:
            print(f"Processing match {i+1}/{len(match_ids)}")

        df = load_lineups_for_match(match_id)

        if not df.empty:
            all_lineups.append(df)

    lineups_df = pd.concat(all_lineups, ignore_index=True)

    return lineups_df


def save_lineups(df: pd.DataFrame, output_path: Path) -> None:
    """
    Save lineups to CSV.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)


def run_pipeline() -> pd.DataFrame:
    """
    Full pipeline to load all lineups.
    """
    print("Loading matches...")
    matches_df = load_matches(INPUT_MATCHES_PATH)
    print(f"Matches shape: {matches_df.shape}")

    print("Loading all lineups...")
    lineups_df = load_all_lineups(matches_df)
    print(f"Lineups shape: {lineups_df.shape}")

    print("Saving lineups...")
    save_lineups(lineups_df, OUTPUT_LINEUPS_PATH)

    print("Lineups loading completed successfully.")
    return lineups_df


if __name__ == "__main__":
    lineups_df = run_pipeline()

    print("\nOutput file created:")
    print(OUTPUT_LINEUPS_PATH)

    print("\nPreview:")
    print(lineups_df.head())