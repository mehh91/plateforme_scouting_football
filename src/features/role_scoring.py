# src/features/role_scoring.py

from pathlib import Path

import pandas as pd

from src.utils.role_definitions import ROLE_DEFINITIONS
from src.utils.position_groups import assign_position_group

INPUT_PATH = Path("data/processed/player_scouting_profile.parquet")
OUTPUT_PATH = Path("data/processed/player_role_scores.parquet")
ROLE_GROUP_MISMATCH_PENALTY = 1.0


def load_data(input_path: Path) -> pd.DataFrame:
    return pd.read_parquet(input_path)


def compute_role_score(df: pd.DataFrame, weights: dict) -> pd.Series:
    score = 0
    for dim, w in weights.items():
        if dim in df.columns:
            score += df[dim] * w
    return score


def apply_role_context_penalty(
    score: pd.Series,
    position_groups: pd.Series,
    target_groups: list[str],
    penalty: float,
) -> pd.Series:
    adjusted_score = score.copy()
    is_target_group = position_groups.isin(target_groups)
    adjusted_score.loc[~is_target_group] = adjusted_score.loc[~is_target_group] - penalty
    return adjusted_score


def run_pipeline() -> pd.DataFrame:
    print("Loading scouting profile...")
    df = load_data(INPUT_PATH)
    print(f"Input shape: {df.shape}")

    df["position_group"] = df["position"].apply(assign_position_group)

    for role_name, role_definition in ROLE_DEFINITIONS.items():
        weights = role_definition["weights"]
        raw_score = compute_role_score(df, weights)
        contextualized_score = apply_role_context_penalty(
            score=raw_score,
            position_groups=df["position_group"],
            target_groups=role_definition["target_groups"],
            penalty=ROLE_GROUP_MISMATCH_PENALTY,
        )
        df[f"{role_name}_score"] = contextualized_score.round(4)

    print("Saving role scores...")
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUTPUT_PATH, index=False)

    print("Role scoring pipeline completed successfully.")
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
        "progressive_midfielder_score",
        "creative_winger_score",
        "ball_playing_center_back_score",
        "progressive_fullback_score",
    ]

    print("\nPreview:")
    print(df[preview_cols].head())
