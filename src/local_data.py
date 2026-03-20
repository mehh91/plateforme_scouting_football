from pathlib import Path
import pandas as pd


RAW_MATCH_DIR = Path("data/raw/spain_vs_germany_3942226")


def load_local_events():
    """
    Charge les événements du match depuis le dossier local raw.
    """
    events_path = RAW_MATCH_DIR / "events.csv"
    return pd.read_csv(events_path)


def load_local_lineups():
    """
    Charge les compositions locales et les retourne sous forme de dictionnaire.
    """
    spain_path = RAW_MATCH_DIR / "lineup_spain.csv"
    germany_path = RAW_MATCH_DIR / "lineup_germany.csv"

    lineups = {
        "Spain": pd.read_csv(spain_path),
        "Germany": pd.read_csv(germany_path)
    }
    return lineups


if __name__ == "__main__":
    events = load_local_events()
    lineups = load_local_lineups()

    print("Dimensions des events locaux :")
    print(events.shape)

    print("\nColonnes des events locaux :")
    print(events.columns.tolist()[:10])

    print("\nDimensions lineup Spain :")
    print(lineups["Spain"].shape)

    print("\nDimensions lineup Germany :")
    print(lineups["Germany"].shape)