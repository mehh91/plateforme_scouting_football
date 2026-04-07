# src/ingestion/load_events.py

import pandas as pd
from statsbombpy import sb
from pathlib import Path


def load_matches(input_path: Path) -> pd.DataFrame:
    """
    Load matches from local CSV file.
    """
    return pd.read_csv(input_path)


def get_match_ids(matches_df: pd.DataFrame) -> list[int]:
    """
    Extract unique match IDs from matches dataframe.
    """
    match_ids = matches_df["match_id"].dropna().unique().tolist()
    return match_ids


def load_events_for_match(match_id: int) -> pd.DataFrame:
    """
    Load events for a single match.
    """
    events_df = sb.events(match_id=match_id)
    events_df["match_id"] = match_id
    return events_df


def load_all_events(match_ids: list[int]) -> pd.DataFrame:
    """
    Load events for all matches and concatenate them into one dataframe.
    """
    all_events = []
    failed_matches = []

    total_matches = len(match_ids)

    for i, match_id in enumerate(match_ids, start=1):
        try:
            print(f"[{i}/{total_matches}] Loading events for match_id={match_id}...")

            events_df = load_events_for_match(match_id)
            all_events.append(events_df)

        except Exception as e:
            print(f"Error while loading match_id={match_id}: {e}")
            failed_matches.append(match_id)

    if not all_events:
        raise ValueError("No events were loaded successfully.")

    combined_events_df = pd.concat(all_events, ignore_index=True)

    print("\nEvent loading completed.")
    print(f"Successfully loaded matches: {len(all_events)}")
    print(f"Failed matches: {len(failed_matches)}")

    if failed_matches:
        print("List of failed match_ids:")
        print(failed_matches)

    return combined_events_df


def save_events(df: pd.DataFrame, output_path: Path) -> None:
    """
    Save events dataframe to CSV.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)


if __name__ == "__main__":
    matches_file = Path("data/raw/matches.csv")
    output_file = Path("data/raw/events.csv")

    matches_df = load_matches(matches_file)
    match_ids = get_match_ids(matches_df)

    events_df = load_all_events(match_ids)
    save_events(events_df, output_file)

    print("\nEvents data saved successfully.")
    print(f"Total number of event rows: {len(events_df)}")
    print(f"Total number of columns: {events_df.shape[1]}")