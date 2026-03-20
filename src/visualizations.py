from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from mplsoccer import Pitch


EVENTS_PATH = Path("data/processed/events_clean.parquet")
PASSES_PATH = Path("data/processed/passes.parquet")
SHOTS_PATH = Path("data/processed/shots.parquet")
RODRI_SUMMARY_PATH = Path("data/processed/rodri_match_summary.parquet")
DANI_OLMO_SUMMARY_PATH = Path("data/processed/dani_olmo_match_summary.parquet")
FIGURES_DIR = Path("reports/figures")


def load_events():
    return pd.read_parquet(EVENTS_PATH)


def load_passes():
    return pd.read_parquet(PASSES_PATH)


def load_shots():
    return pd.read_parquet(SHOTS_PATH)


def load_rodri_summary():
    return pd.read_parquet(RODRI_SUMMARY_PATH)


def load_dani_olmo_summary():
    return pd.read_parquet(DANI_OLMO_SUMMARY_PATH)


def get_player_actions(events, player_name):
    df = events[events["player"] == player_name].copy()
    df = df.dropna(subset=["x", "y"])
    return df


def get_player_passes(passes, player_name):
    df = passes[passes["player"] == player_name].copy()
    df = df.dropna(subset=["x", "y", "end_x", "end_y"])
    return df


def get_player_shots(shots, player_name):
    df = shots[shots["player"] == player_name].copy()
    df = df.dropna(subset=["x", "y"])
    return df


def plot_player_heatmap(player_actions, player_name, output_path):
    pitch = Pitch(pitch_type="statsbomb", line_zorder=2)
    fig, ax = pitch.draw(figsize=(10, 7))

    pitch.kdeplot(
        player_actions["x"],
        player_actions["y"],
        ax=ax,
        fill=True,
        levels=100,
        thresh=0.05,
        cmap="RdYlBu_r"
    )

    ax.set_title(f"Heatmap d'activité - {player_name}", fontsize=16)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"Figure sauvegardée : {output_path}")


def plot_player_passmap(player_passes, player_name, output_path):
    completed = player_passes[player_passes["is_completed"]].copy()
    progressive_completed = completed[completed["is_progressive_pass"]].copy()

    pitch = Pitch(pitch_type="statsbomb", line_zorder=2)
    fig, ax = pitch.draw(figsize=(10, 7))

    pitch.arrows(
        completed["x"],
        completed["y"],
        completed["end_x"],
        completed["end_y"],
        ax=ax,
        width=1.5,
        headwidth=4,
        headlength=4,
        alpha=0.35
    )

    pitch.arrows(
        progressive_completed["x"],
        progressive_completed["y"],
        progressive_completed["end_x"],
        progressive_completed["end_y"],
        ax=ax,
        width=2.2,
        headwidth=5,
        headlength=5,
        alpha=0.9
    )

    ax.set_title(f"Pass map - {player_name}", fontsize=16)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"Figure sauvegardée : {output_path}")
    print(f"Passes réussies affichées : {completed.shape[0]}")
    print(f"Passes progressives réussies affichées : {progressive_completed.shape[0]}")


def plot_player_summary_card(player_actions, summary_row, player_name, output_path):
    fig = plt.figure(figsize=(14, 7))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.8, 1])

    ax_pitch = fig.add_subplot(gs[0, 0])
    ax_text = fig.add_subplot(gs[0, 1])

    pitch = Pitch(pitch_type="statsbomb", line_zorder=2)
    pitch.draw(ax=ax_pitch)

    pitch.kdeplot(
        player_actions["x"],
        player_actions["y"],
        ax=ax_pitch,
        fill=True,
        levels=100,
        thresh=0.05,
        cmap="RdYlBu_r"
    )

    ax_pitch.set_title(f"{player_name} - Heatmap d'activité", fontsize=16)

    ax_text.axis("off")

    stats_text = (
        f"Joueur : {summary_row['player']}\n\n"
        f"Passes tentées : {int(summary_row['passes_attempted'])}\n"
        f"Passes réussies : {int(summary_row['passes_completed'])}\n"
        f"Taux de réussite : {summary_row['completion_pct']}%\n"
        f"Passes progressives : {int(summary_row['progressive_passes'])}\n"
        f"Passes dernier tiers : {int(summary_row['final_third_passes'])}\n"
        f"Entrées de surface : {int(summary_row['box_entries'])}\n"
        f"Tirs : {int(summary_row['shots'])}\n"
        f"xG : {summary_row['xg']}\n"
        f"Pressions : {int(summary_row['pressures'])}\n"
        f"Récupérations : {int(summary_row['recoveries'])}"
    )

    ax_text.text(
        0.02, 0.95, stats_text,
        va="top", ha="left",
        fontsize=13
    )

    fig.suptitle(f"Fiche de performance individuelle - {player_name}", fontsize=18)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"Figure sauvegardée : {output_path}")


def plot_shot_map(player_shots, player_name, output_path):
    """
    Crée une shot map du joueur avec taille des points proportionnelle à l'xG.
    """
    pitch = Pitch(pitch_type="statsbomb", line_zorder=2)
    fig, ax = pitch.draw(figsize=(10, 7))

    if not player_shots.empty:
        sizes = player_shots["shot_statsbomb_xg"].fillna(0) * 2500 + 80

        pitch.scatter(
            player_shots["x"],
            player_shots["y"],
            s=sizes,
            ax=ax,
            alpha=0.7
        )

    ax.set_title(f"Shot map - {player_name}", fontsize=16)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"Figure sauvegardée : {output_path}")
    print(f"Nombre de tirs affichés : {player_shots.shape[0]}")
    print(f"xG total affiché : {round(player_shots['shot_statsbomb_xg'].fillna(0).sum(), 3)}")


if __name__ == "__main__":
    rodri_name = "Rodrigo Hernández Cascante"
    olmo_name = "Daniel Olmo Carvajal"

    events = load_events()
    passes = load_passes()
    shots = load_shots()

    rodri_summary = load_rodri_summary()
    olmo_summary = load_dani_olmo_summary()

    rodri_actions = get_player_actions(events, rodri_name)
    rodri_passes = get_player_passes(passes, rodri_name)
    rodri_summary_row = rodri_summary.iloc[0]

    olmo_actions = get_player_actions(events, olmo_name)
    olmo_shots = get_player_shots(shots, olmo_name)
    olmo_summary_row = olmo_summary.iloc[0]

    print(f"Nombre d'actions localisées pour {rodri_name} : {rodri_actions.shape[0]}")
    print(f"Nombre de passes pour {rodri_name} : {rodri_passes.shape[0]}")
    print(f"Nombre d'actions localisées pour {olmo_name} : {olmo_actions.shape[0]}")
    print(f"Nombre de tirs pour {olmo_name} : {olmo_shots.shape[0]}")

    heatmap_file = FIGURES_DIR / "rodri_heatmap.png"
    passmap_file = FIGURES_DIR / "rodri_passmap.png"
    summary_card_file = FIGURES_DIR / "rodri_summary_card.png"
    olmo_shotmap_file = FIGURES_DIR / "dani_olmo_shotmap.png"
    olmo_summary_card_file = FIGURES_DIR / "dani_olmo_summary_card.png"

    plot_player_heatmap(rodri_actions, rodri_name, heatmap_file)
    plot_player_passmap(rodri_passes, rodri_name, passmap_file)
    plot_player_summary_card(rodri_actions, rodri_summary_row, rodri_name, summary_card_file)

    plot_shot_map(olmo_shots, olmo_name, olmo_shotmap_file)
    plot_player_summary_card(olmo_actions, olmo_summary_row, olmo_name, olmo_summary_card_file)