# src/ingestion/load_matches.py

import pandas as pd
from statsbombpy import sb
from pathlib import Path


TARGET_COMPETITIONS = [
    {"competition_id": 2, "season_id": 27, "competition_name": "Premier League"},
    {"competition_id": 7, "season_id": 27, "competition_name": "Ligue 1"},
    {"competition_id": 9, "season_id": 27, "competition_name": "1. Bundesliga"},
    {"competition_id": 11, "season_id": 27, "competition_name": "La Liga"},
    {"competition_id": 12, "season_id": 27, "competition_name": "Serie A"},
]


def load_matches_for_competition(competition_id: int, season_id: int) -> pd.DataFrame:
    """
    Load matches for one competition and one season from StatsBomb.
    """
    matches_df = sb.matches(competition_id=competition_id, season_id=season_id)
    return matches_df


def add_competition_metadata(df: pd.DataFrame, competition: dict) -> pd.DataFrame:
    """
    Add competition metadata columns to the matches dataframe.
    """
    df = df.copy()
    df["competition_id"] = competition["competition_id"]
    df["season_id"] = competition["season_id"]
    df["competition_name"] = competition["competition_name"]
    return df


def load_all_matches(competitions: list[dict]) -> pd.DataFrame:
    """
    Load and concatenate matches for all target competitions.
    """
    all_matches = []

    for competition in competitions:
        competition_id = competition["competition_id"]
        season_id = competition["season_id"]
        competition_name = competition["competition_name"]

        print(
            f"Loading matches for {competition_name} "
            f"(competition_id={competition_id}, season_id={season_id})..."
        )

        matches_df = load_matches_for_competition(
            competition_id=competition_id,
            season_id=season_id
        )

        matches_df = add_competition_metadata(matches_df, competition)
        all_matches.append(matches_df)

    combined_matches_df = pd.concat(all_matches, ignore_index=True)

    return combined_matches_df


def save_matches(df: pd.DataFrame, output_path: Path) -> None:
    """
    Save matches dataframe to CSV.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)


if __name__ == "__main__":
    output_file = Path("data/raw/matches.csv")

    matches_df = load_all_matches(TARGET_COMPETITIONS)
    save_matches(matches_df, output_file)

    print("\nMatches data saved successfully.")
    print(f"Total number of matches: {len(matches_df)}")
    print("\nMatches by competition:")
    print(matches_df["competition_name"].value_counts())