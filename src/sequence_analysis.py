from pathlib import Path
import pandas as pd


EVENTS_PATH = Path("data/processed/events_clean.parquet")


def load_events():
    return pd.read_parquet(EVENTS_PATH)


def get_team_events(events, team_name):
    """
    Filtre les événements d'une équipe.
    """
    return events[events["team"] == team_name].copy()


def get_team_shot_possessions(events, team_name):
    """
    Retourne les possessions de l'équipe qui se terminent par au moins un tir.
    """
    team_events = get_team_events(events, team_name)

    shot_possessions = team_events.loc[
        team_events["type"] == "Shot", "possession"
    ].dropna().unique()

    possessions_df = team_events[team_events["possession"].isin(shot_possessions)].copy()
    return possessions_df


def build_shot_sequence_summary(events, team_name):
    """
    Construit une synthèse des possessions de l'équipe menant à un tir.
    """
    shot_sequences = get_team_shot_possessions(events, team_name)

    summary_rows = []

    for possession_id, possession_df in shot_sequences.groupby("possession"):
        possession_df = possession_df.sort_values(["period", "minute", "second", "index"])

        shots_in_possession = possession_df[possession_df["type"] == "Shot"].copy()
        if shots_in_possession.empty:
            continue

        last_shot = shots_in_possession.iloc[-1]

        summary_rows.append({
            "possession": possession_id,
            "team": team_name,
            "start_minute": possession_df.iloc[0]["minute"],
            "end_minute": possession_df.iloc[-1]["minute"],
            "num_actions": len(possession_df),
            "shooter": last_shot["player"],
            "shot_xg": round(float(last_shot["shot_statsbomb_xg"]) if pd.notna(last_shot["shot_statsbomb_xg"]) else 0.0, 3),
            "play_pattern": last_shot["play_pattern"]
        })

    summary = pd.DataFrame(summary_rows)
    summary = summary.sort_values(["shot_xg", "num_actions"], ascending=False).reset_index(drop=True)

    return summary


if __name__ == "__main__":
    events = load_events()
    spain_shot_sequences = build_shot_sequence_summary(events, "Spain")

    print("Dimensions des séquences menant à un tir :")
    print(spain_shot_sequences.shape)

    print("\nTop 15 séquences Espagne menant à un tir :")
    print(spain_shot_sequences.head(15))