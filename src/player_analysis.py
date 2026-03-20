from pathlib import Path
import pandas as pd


PASSES_PATH = Path("data/processed/passes.parquet")
SHOTS_PATH = Path("data/processed/shots.parquet")
PRESSURES_PATH = Path("data/processed/pressures.parquet")
RECOVERIES_PATH = Path("data/processed/recoveries.parquet")


def load_passes():
    return pd.read_parquet(PASSES_PATH)


def load_shots():
    return pd.read_parquet(SHOTS_PATH)


def load_pressures():
    return pd.read_parquet(PRESSURES_PATH)


def load_recoveries():
    return pd.read_parquet(RECOVERIES_PATH)


def get_player_event_data(player_name):
    passes = load_passes()
    shots = load_shots()
    pressures = load_pressures()
    recoveries = load_recoveries()

    player_data = {
        "passes": passes[passes["player"] == player_name].copy(),
        "shots": shots[shots["player"] == player_name].copy(),
        "pressures": pressures[pressures["player"] == player_name].copy(),
        "recoveries": recoveries[recoveries["player"] == player_name].copy(),
    }

    return player_data


def build_player_match_summary(player_name):
    player_data = get_player_event_data(player_name)

    passes = player_data["passes"]
    shots = player_data["shots"]
    pressures = player_data["pressures"]
    recoveries = player_data["recoveries"]

    passes_attempted = len(passes)
    passes_completed = int(passes["is_completed"].sum()) if not passes.empty else 0
    completion_pct = round((passes_completed / passes_attempted * 100), 1) if passes_attempted > 0 else 0.0
    progressive_passes = int(passes["is_progressive_pass"].sum()) if not passes.empty else 0
    final_third_passes = int(passes["reaches_final_third"].sum()) if not passes.empty else 0
    box_entries = int(passes["enters_box"].sum()) if not passes.empty else 0

    shots_total = len(shots)
    xg_total = round(shots["shot_statsbomb_xg"].fillna(0).sum(), 3) if not shots.empty else 0.0

    pressures_total = len(pressures)
    recoveries_total = len(recoveries)

    summary = pd.DataFrame([{
        "player": player_name,
        "passes_attempted": passes_attempted,
        "passes_completed": passes_completed,
        "completion_pct": completion_pct,
        "progressive_passes": progressive_passes,
        "final_third_passes": final_third_passes,
        "box_entries": box_entries,
        "shots": shots_total,
        "xg": xg_total,
        "pressures": pressures_total,
        "recoveries": recoveries_total
    }])

    return summary


def save_summary(summary, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary.to_parquet(output_path, index=False)
    print(f"Sauvegardé : {output_path}")


if __name__ == "__main__":
    rodri_name = "Rodrigo Hernández Cascante"
    olmo_name = "Daniel Olmo Carvajal"

    rodri_summary = build_player_match_summary(rodri_name)
    olmo_summary = build_player_match_summary(olmo_name)

    print("Synthèse Rodri :")
    print(rodri_summary)

    print("\nSynthèse Dani Olmo :")
    print(olmo_summary)

    save_summary(rodri_summary, "data/processed/rodri_match_summary.parquet")
    save_summary(olmo_summary, "data/processed/dani_olmo_match_summary.parquet")