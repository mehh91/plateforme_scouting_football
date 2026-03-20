from pathlib import Path
import numpy as np
import pandas as pd


PROCESSED_EVENTS_PATH = Path("data/processed/events_clean.parquet")


def load_processed_events():
    """
    Charge les événements prétraités depuis le fichier parquet.
    """
    return pd.read_parquet(PROCESSED_EVENTS_PATH)


def get_passes(events):
    return events[events["type"] == "Pass"].copy()


def get_shots(events):
    return events[events["type"] == "Shot"].copy()


def get_pressures(events):
    return events[events["type"] == "Pressure"].copy()


def get_recoveries(events):
    return events[events["type"] == "Ball Recovery"].copy()


def add_pass_features(passes):
    """
    Ajoute des indicateurs métier à la table des passes.
    """
    df = passes.copy()

    # Passe réussie : pass_outcome manquant = completed
    df["is_completed"] = df["pass_outcome"].isna()

    # Longueur de passe en numérique
    if "pass_length" in df.columns:
        df["pass_length_numeric"] = pd.to_numeric(df["pass_length"], errors="coerce")
    else:
        df["pass_length_numeric"] = np.sqrt((df["end_x"] - df["x"])**2 + (df["end_y"] - df["y"])**2)

    # Distance au centre du but adverse (approximation simple)
    start_distance_to_goal = np.sqrt((120 - df["x"])**2 + (40 - df["y"])**2)
    end_distance_to_goal = np.sqrt((120 - df["end_x"])**2 + (40 - df["end_y"])**2)

    # Passe progressive : réduction de distance > 10
    df["is_progressive_pass"] = (start_distance_to_goal - end_distance_to_goal) > 10

    # Atteint le dernier tiers
    df["reaches_final_third"] = df["end_x"] >= 80

    # Entre dans la surface
    df["enters_box"] = (df["end_x"] >= 102) & (df["end_y"].between(18, 62))

    return df


def save_dataframe(df, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)
    print(f"Sauvegardé : {output_path}")


def build_event_subsets():
    """
    Construit les sous-ensembles principaux d'événements.
    """
    events = load_processed_events()

    passes = add_pass_features(get_passes(events))
    shots = get_shots(events)
    pressures = get_pressures(events)
    recoveries = get_recoveries(events)

    return {
        "passes": passes,
        "shots": shots,
        "pressures": pressures,
        "recoveries": recoveries
    }


if __name__ == "__main__":
    subsets = build_event_subsets()

    passes = subsets["passes"]

    print(f"\nPASSES : {passes.shape}")
    print(f"Passes réussies : {passes['is_completed'].sum()}")
    print(f"Passes progressives : {passes['is_progressive_pass'].sum()}")
    print(f"Passes vers dernier tiers : {passes['reaches_final_third'].sum()}")
    print(f"Passes dans la surface : {passes['enters_box'].sum()}")

    print(f"\nSHOTS : {subsets['shots'].shape}")
    print(f"PRESSURES : {subsets['pressures'].shape}")
    print(f"RECOVERIES : {subsets['recoveries'].shape}")

    save_dataframe(subsets["passes"], "data/processed/passes.parquet")
    save_dataframe(subsets["shots"], "data/processed/shots.parquet")
    save_dataframe(subsets["pressures"], "data/processed/pressures.parquet")
    save_dataframe(subsets["recoveries"], "data/processed/recoveries.parquet")