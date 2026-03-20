import ast
from pathlib import Path

import numpy as np
import pandas as pd

from src.local_data import load_local_events


def parse_location(value):
    """
    Transforme une valeur de type location en liste Python exploitable.
    Gère les cas où la valeur est déjà une liste, une chaîne de caractères, ou manquante.
    """
    if isinstance(value, list):
        return value

    if pd.isna(value):
        return np.nan

    if isinstance(value, str):
        try:
            parsed = ast.literal_eval(value)
            return parsed
        except (ValueError, SyntaxError):
            return np.nan

    return np.nan


def extract_xy(value):
    """
    Extrait x et y depuis une liste [x, y, ...].
    Retourne (np.nan, np.nan) si la structure est invalide.
    """
    value = parse_location(value)

    if isinstance(value, list) and len(value) >= 2:
        return value[0], value[1]

    return np.nan, np.nan


def add_coordinate_columns(events):
    """
    Ajoute des colonnes de coordonnées à partir des colonnes de localisation.
    """
    df = events.copy()

    df[["x", "y"]] = df["location"].apply(lambda v: pd.Series(extract_xy(v)))
    df[["end_x", "end_y"]] = df["pass_end_location"].apply(lambda v: pd.Series(extract_xy(v)))
    df[["carry_end_x", "carry_end_y"]] = df["carry_end_location"].apply(lambda v: pd.Series(extract_xy(v)))
    df[["shot_end_x", "shot_end_y"]] = df["shot_end_location"].apply(lambda v: pd.Series(extract_xy(v)))

    return df


def save_processed_events(events, output_path="data/processed/events_clean.parquet"):
    """
    Sauvegarde les événements nettoyés au format parquet.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    events.to_parquet(output_path, index=False)
    print(f"\nFichier sauvegardé : {output_path.resolve()}")


def preprocess_events():
    """
    Pipeline simple de prétraitement des événements.
    """
    events = load_local_events()
    events = add_coordinate_columns(events)
    return events


if __name__ == "__main__":
    events = preprocess_events()

    print("Dimensions après prétraitement :")
    print(events.shape)

    print("\nNombre de valeurs non nulles :")
    for col in ["x", "y", "end_x", "end_y", "carry_end_x", "carry_end_y", "shot_end_x", "shot_end_y"]:
        print(f"{col}: {events[col].notna().sum()}")

    save_processed_events(events)