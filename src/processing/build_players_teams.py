# src/processing/build_players_teams.py

from pathlib import Path

import pandas as pd


INPUT_EVENTS_PATH = Path("data/interim/events_clean.parquet")
OUTPUT_PLAYERS_PATH = Path("data/interim/players.parquet")
OUTPUT_TEAMS_PATH = Path("data/interim/teams.parquet")


def load_events(input_path: Path) -> pd.DataFrame:
    """
    Load cleaned events parquet file.
    """
    return pd.read_parquet(input_path)


def build_players_table(events_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a player reference table from events.

    Strategy:
    - keep valid player rows
    - group by player / position / team
    - count events
    - keep the most frequent combination per player
    """
    player_cols = ["player", "position", "team"]

    players_df = (
        events_df[player_cols]
        .dropna(subset=["player"])
        .copy()
    )

    grouped_players = (
        players_df
        .groupby(["player", "position", "team"], dropna=False)
        .size()
        .reset_index(name="event_count")
        .sort_values(["player", "event_count"], ascending=[True, False])
    )

    primary_players = (
        grouped_players
        .drop_duplicates(subset=["player"], keep="first")
        .reset_index(drop=True)
        .sort_values("player")
        .reset_index(drop=True)
    )

    return primary_players


def build_teams_table(events_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a team reference table from events.
    """
    teams_df = (
        events_df[["team"]]
        .dropna(subset=["team"])
        .groupby("team")
        .size()
        .reset_index(name="event_count")
        .sort_values("team")
        .reset_index(drop=True)
    )

    return teams_df


def save_parquet(df: pd.DataFrame, output_path: Path) -> None:
    """
    Save dataframe as parquet.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)


def run_pipeline() -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Run players and teams reference table creation.
    """
    print("Loading cleaned events...")
    events_df = load_events(INPUT_EVENTS_PATH)
    print(f"Events shape: {events_df.shape}")

    print("Building players table...")
    players_df = build_players_table(events_df)
    print(f"Players shape: {players_df.shape}")

    print("Building teams table...")
    teams_df = build_teams_table(events_df)
    print(f"Teams shape: {teams_df.shape}")

    print("Saving players parquet...")
    save_parquet(players_df, OUTPUT_PLAYERS_PATH)

    print("Saving teams parquet...")
    save_parquet(teams_df, OUTPUT_TEAMS_PATH)

    print("Players and teams tables created successfully.")

    return players_df, teams_df


if __name__ == "__main__":
    players_df, teams_df = run_pipeline()

    print("\nPlayers preview:")
    print(players_df.head())

    print("\nTeams preview:")
    print(teams_df.head())