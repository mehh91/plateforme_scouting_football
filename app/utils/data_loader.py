from pathlib import Path
from functools import lru_cache

import pandas as pd

from src.utils.player_profiles import add_player_key, select_primary_player_rows


BASE_PROCESSED = Path("data/processed")

PLAYER_ROLE_SCORES_PATH = BASE_PROCESSED / "player_role_scores.parquet"
PLAYER_SIMILARITY_PATH = BASE_PROCESSED / "player_similarity.parquet"
PLAYER_GROUP_PERCENTILES_PATH = BASE_PROCESSED / "player_group_percentiles.parquet"


@lru_cache(maxsize=1)
def load_player_role_scores() -> pd.DataFrame:
    return pd.read_parquet(PLAYER_ROLE_SCORES_PATH)


@lru_cache(maxsize=1)
def load_primary_player_role_scores() -> pd.DataFrame:
    df = load_player_role_scores()
    df = select_primary_player_rows(df)
    df = add_player_key(df)
    return df


@lru_cache(maxsize=1)
def load_player_similarity() -> pd.DataFrame:
    df = pd.read_parquet(PLAYER_SIMILARITY_PATH)

    if "player_key" not in df.columns:
        df = add_player_key(
            df,
            output_col="player_key",
            player_col="player",
            team_col="player_team",
            competition_col="player_competition",
        )

    if "similar_player_key" not in df.columns:
        df = add_player_key(
            df,
            output_col="similar_player_key",
            player_col="similar_player",
            team_col="similar_player_team",
            competition_col="similar_player_competition",
        )

    return df


@lru_cache(maxsize=1)
def load_player_group_percentiles() -> pd.DataFrame:
    return pd.read_parquet(PLAYER_GROUP_PERCENTILES_PATH)
