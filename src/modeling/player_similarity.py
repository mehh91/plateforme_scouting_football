# src/modeling/player_similarity.py

from pathlib import Path

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler

from src.utils.player_profiles import add_player_key, select_primary_player_rows
from src.utils.role_definitions import ROLE_DEFINITIONS


INPUT_PATH = Path("data/processed/player_role_scores.parquet")
OUTPUT_PATH = Path("data/processed/player_similarity.parquet")


SIMILARITY_FEATURES = [
    "ball_progression",
    "chance_creation",
    "final_third_impact",
    "defensive_activity",
    "ball_security",
] + [f"{role_name}_score" for role_name in ROLE_DEFINITIONS]

MINIMUM_MINUTES = 900
TOP_N = 10


def load_data(input_path: Path) -> pd.DataFrame:
    return pd.read_parquet(input_path)


def filter_players(df: pd.DataFrame, minimum_minutes: int) -> pd.DataFrame:
    return df[df["minutes_played"] >= minimum_minutes].copy().reset_index(drop=True)

def prepare_feature_matrix(df: pd.DataFrame, feature_columns: list[str]):
    available_features = [col for col in feature_columns if col in df.columns]

    feature_df = df[available_features].copy()

    # Fill NaN with column median, then fallback to 0
    feature_df = feature_df.fillna(feature_df.median(numeric_only=True))
    feature_df = feature_df.fillna(0)

    scaler = StandardScaler()
    X = scaler.fit_transform(feature_df)

    return X, available_features


def compute_similarity_table(df: pd.DataFrame, X, top_n: int) -> pd.DataFrame:
    similarity_matrix = cosine_similarity(X)

    records = []

    for i, player_name in enumerate(df["player"]):
        similarities = similarity_matrix[i]

        player_sim_df = pd.DataFrame({
            "similarity_index": range(len(similarities)),
            "similarity_score": similarities
        })

        # Remove self
        player_sim_df = player_sim_df[player_sim_df["similarity_index"] != i]

        # Keep top N
        player_sim_df = player_sim_df.sort_values(
            "similarity_score",
            ascending=False
        ).head(top_n)

        for _, row in player_sim_df.iterrows():
            j = int(row["similarity_index"])

            records.append({
                "player": df.loc[i, "player"],
                "player_key": df.loc[i, "player_key"],
                "player_team": df.loc[i, "team"],
                "player_competition": df.loc[i, "competition_name"] if "competition_name" in df.columns else None,
                "player_position": df.loc[i, "position"],
                "player_minutes": df.loc[i, "minutes_played"],
                "similar_player": df.loc[j, "player"],
                "similar_player_key": df.loc[j, "player_key"],
                "similar_player_team": df.loc[j, "team"],
                "similar_player_competition": df.loc[j, "competition_name"] if "competition_name" in df.columns else None,
                "similar_player_position": df.loc[j, "position"],
                "similar_player_minutes": df.loc[j, "minutes_played"],
                "similarity_score": round(float(row["similarity_score"]), 4),
            })

    similarity_df = pd.DataFrame(records)

    return similarity_df.sort_values(
        ["player", "similarity_score"],
        ascending=[True, False]
    ).reset_index(drop=True)


def run_pipeline() -> pd.DataFrame:
    print("Loading player role scores...")
    df = load_data(INPUT_PATH)
    print(f"Input shape: {df.shape}")

    print(f"Filtering players with at least {MINIMUM_MINUTES} minutes...")
    df = filter_players(df, MINIMUM_MINUTES)
    print(f"Shape after minutes filter: {df.shape}")

    print("Deduplicating players by primary seasonal row...")
    df = select_primary_player_rows(df)
    print(f"Shape after deduplication: {df.shape}")

    df = add_player_key(df)

    print("Preparing feature matrix...")
    X, used_features = prepare_feature_matrix(df, SIMILARITY_FEATURES)
    print(f"Number of features used: {len(used_features)}")
    print(f"Features used: {used_features}")

    print("Computing similarity table...")
    similarity_df = compute_similarity_table(df, X, TOP_N)
    print(f"Similarity table shape: {similarity_df.shape}")

    print("Saving similarity parquet...")
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    similarity_df.to_parquet(OUTPUT_PATH, index=False)

    print("Player similarity pipeline completed successfully.")
    return similarity_df


if __name__ == "__main__":
    similarity_df = run_pipeline()

    print("\nOutput file created:")
    print(OUTPUT_PATH)

    print("\nPreview:")
    print(similarity_df.head(20))
