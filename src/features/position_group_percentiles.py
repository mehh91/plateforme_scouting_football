# src/features/position_group_percentiles.py

from pathlib import Path
import pandas as pd

from src.utils.player_profiles import select_primary_player_rows
from src.utils.position_groups import POSITION_GROUPS


INPUT_PATH = Path("data/processed/player_role_scores.parquet")
OUTPUT_PATH = Path("data/processed/player_group_percentiles.parquet")

MINIMUM_MINUTES = 900

GROUP_METRICS = {
    "Défenseurs centraux": [
        "pass_completion_pct",
        "progressive_passes_per90",
        "recoveries_per90",
        "interceptions_per90",
        "duels_per90",
    ],
    "Latéraux": [
        "progressive_passes_per90",
        "progressive_carries_per90",
        "passes_into_final_third_per90",
        "passes_into_box_per90",
        "recoveries_per90",
    ],
    "Milieux défensifs": [
        "pass_completion_pct",
        "progressive_passes_per90",
        "recoveries_per90",
        "interceptions_per90",
        "duels_per90",
    ],
    "Milieux centraux": [
        "progressive_passes_per90",
        "progressive_carries_per90",
        "key_passes_per90",
        "pass_completion_pct",
        "recoveries_per90",
    ],
    "Milieux offensifs": [
        "key_passes_per90",
        "progressive_passes_per90",
        "progressive_carries_per90",
        "shots_per90",
        "xg_per90",
    ],
    "Ailiers": [
        "key_passes_per90",
        "progressive_passes_per90",
        "progressive_carries_per90",
        "touches_in_box_per90",
        "xg_per90",
    ],
    "Attaquants": [
        "shots_per90",
        "xg_per90",
        "touches_in_box_per90",
        "goals_per90",
        "key_passes_per90",
    ],
    "Gardiens": [
        "pass_completion_pct",
    ],
}

GROUP_METRIC_LABELS = {
    "pass_completion_pct": "Réussite de passe",
    "progressive_passes_per90": "Passes progressives / 90",
    "progressive_carries_per90": "Conduites progressives / 90",
    "passes_into_final_third_per90": "Passes vers dernier tiers / 90",
    "passes_into_box_per90": "Passes dans la surface / 90",
    "recoveries_per90": "Récupérations / 90",
    "interceptions_per90": "Interceptions / 90",
    "duels_per90": "Duels / 90",
    "key_passes_per90": "Passes clés / 90",
    "shots_per90": "Tirs / 90",
    "xg_per90": "xG / 90",
    "touches_in_box_per90": "Touches dans la surface / 90",
    "goals_per90": "Buts / 90",
}


def load_data(input_path: Path) -> pd.DataFrame:
    return pd.read_parquet(input_path)


def assign_position_group(position: str) -> str | None:
    if pd.isna(position):
        return None

    for group_name, positions in POSITION_GROUPS.items():
        if position in positions:
            return group_name

    return None


def compute_percentile(series: pd.Series) -> pd.Series:
    """
    Percentile rank from 0 to 100.
    NaN are ignored by rank and remain NaN after assignment.
    """
    return series.rank(pct=True) * 100

def build_group_percentiles(df: pd.DataFrame) -> pd.DataFrame:
    dff = df.copy()

    dff["position_group"] = dff["position"].apply(assign_position_group)
    dff = dff[dff["position_group"].notna()].copy()
    dff = dff[dff["minutes_played"] >= MINIMUM_MINUTES].copy()

    # Une ligne principale par joueur / club / championnat
    dff = select_primary_player_rows(dff)

    frames = []

    for group_name, metrics in GROUP_METRICS.items():
        group_df = dff[dff["position_group"] == group_name].copy()

        if group_df.empty:
            continue

        available_metrics = [m for m in metrics if m in group_df.columns]
        if not available_metrics:
            continue

        for metric in available_metrics:
            pct_col = f"{metric}_pct"
            group_df[pct_col] = compute_percentile(group_df[metric]).round(2)

        keep_cols = [
            "player",
            "team",
            "competition_name",
            "position",
            "position_group",
            "minutes_played",
            "matches_played",
            "starts",
        ] + available_metrics + [f"{m}_pct" for m in available_metrics]

        frames.append(group_df[keep_cols].copy())

    if not frames:
        return pd.DataFrame()

    result = pd.concat(frames, ignore_index=True)
    result = result.sort_values(
        ["position_group", "competition_name", "team", "player"]
    ).reset_index(drop=True)

    return result


def run_pipeline() -> pd.DataFrame:
    print("Loading player role scores...")
    df = load_data(INPUT_PATH)
    print(f"Input shape: {df.shape}")

    print("Building position-group percentiles...")
    result = build_group_percentiles(df)
    print(f"Output shape: {result.shape}")

    print("Saving parquet...")
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    result.to_parquet(OUTPUT_PATH, index=False)

    print("Position group percentile pipeline completed successfully.")
    return result


if __name__ == "__main__":
    result = run_pipeline()

    print("\nOutput file created:")
    print(OUTPUT_PATH)

    print("\nPreview:")
    print(result.head())
