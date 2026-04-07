import pandas as pd
from statsbombpy import sb
from pathlib import Path


def load_competitions():
    """
    Load all available competitions from StatsBomb Open Data.
    """

    competitions = sb.competitions()

    return competitions


def save_competitions(df: pd.DataFrame, output_path: Path):
    """
    Save competitions dataframe to CSV.
    """

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)


if __name__ == "__main__":
    # Define output path
    output_file = Path("data/raw/competitions.csv")

    # Load data
    competitions_df = load_competitions()

    # Save data
    save_competitions(competitions_df, output_file)

    print("Competitions data saved successfully.")