# src/features/football_dimensions.py

from pathlib import Path

import pandas as pd
from sklearn.preprocessing import StandardScaler


INPUT_PATH = Path("data/processed/player_season_enriched.parquet")
OUTPUT_PATH = Path("data/processed/player_scouting_profile.parquet")


DIMENSION_FEATURES = {
    "ball_progression": [
        "progressive_passes_per90",
        "progressive_carries_per90",
        "passes_into_final_third_per90",
    ],
    "chance_creation": [
        "key_passes_per90",
        "passes_into_box_per90",
    ],
    "final_third_impact": [
        "shots_per90",
        "xg_per90",
        "touches_in_final_third_per90",
        "touches_in_box_per90",
    ],
    "defensive_activity": [
        "recoveries_per90",
        "interceptions_per90",
        "duels_per90",
    ],
    "ball_security": [
        "pass_completion_pct",
    ],
}


def load_data(input_path: Path) -> pd.DataFrame:
    """
    Load enriched player season table.
    """
    return pd.read_parquet(input_path)


def add_standardized_features(df: pd.DataFrame, feature_groups: dict) -> pd.DataFrame:
    """
    Standardize all dimension input features and append z-score columns.
    """
    df = df.copy()

    all_features = sorted({
        feature
        for features in feature_groups.values()
        for feature in features
        if feature in df.columns
    })

    scaler = StandardScaler()
    scaled_values = scaler.fit_transform(df[all_features])

    scaled_df = pd.DataFrame(
        scaled_values,
        columns=[f"{col}_z" for col in all_features],
        index=df.index
    )

    df = pd.concat([df, scaled_df], axis=1)

    return df


def add_dimensions(df: pd.DataFrame, feature_groups: dict) -> pd.DataFrame:
    """
    Compute football dimensions as the mean of standardized features.
    """
    df = df.copy()

    for dimension_name, features in feature_groups.items():
        z_cols = [f"{feature}_z" for feature in features if f"{feature}_z" in df.columns]
        df[dimension_name] = df[z_cols].mean(axis=1).round(4)

    return df


def run_pipeline() -> pd.DataFrame:
    """
    Build scouting profile table with football dimensions.
    """
    print("Loading enriched player season data...")
    df = load_data(INPUT_PATH)
    print(f"Input shape: {df.shape}")

    print("Adding standardized features...")
    df = add_standardized_features(df, DIMENSION_FEATURES)

    print("Computing football dimensions...")
    df = add_dimensions(df, DIMENSION_FEATURES)
    print(f"Output shape: {df.shape}")

    print("Saving scouting profile parquet...")
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUTPUT_PATH, index=False)

    print("Football dimensions pipeline completed successfully.")
    return df


if __name__ == "__main__":
    df = run_pipeline()

    print("\nOutput file created:")
    print(OUTPUT_PATH)

    preview_cols = [
        "player",
        "team",
        "position",
        "minutes_played",
        "meets_minimum_minutes_900",
        "ball_progression",
        "chance_creation",
        "final_third_impact",
        "defensive_activity",
        "ball_security",
    ]

    available_preview_cols = [col for col in preview_cols if col in df.columns]

    print("\nPreview:")
    print(df[available_preview_cols].head())