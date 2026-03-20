from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from mplsoccer import Pitch


PASSES_PATH = Path("data/processed/passes.parquet")
FIGURES_DIR = Path("reports/figures")


def load_passes():
    return pd.read_parquet(PASSES_PATH)


def get_team_passes(passes, team_name):
    """
    Filtre les passes d'une équipe.
    """
    return passes[passes["team"] == team_name].copy()


def get_completed_team_passes(team_passes):
    """
    Garde uniquement les passes réussies avec receveur connu.
    """
    df = team_passes[
        (team_passes["is_completed"]) &
        (team_passes["pass_recipient"].notna()) &
        (team_passes["player"].notna())
    ].copy()
    return df


def get_progressive_team_passes(team_passes):
    """
    Garde uniquement les passes progressives réussies.
    """
    df = team_passes[
        (team_passes["is_completed"]) &
        (team_passes["is_progressive_pass"])
    ].copy()
    df = df.dropna(subset=["x", "y", "end_x", "end_y"])
    return df


def build_pass_network_data(team_passes):
    """
    Construit les données nécessaires au réseau de passes.
    """
    completed = get_completed_team_passes(team_passes)

    avg_positions = (
        completed.groupby("player")
        .agg(
            avg_x=("x", "mean"),
            avg_y=("y", "mean"),
            passes_played=("id", "count")
        )
        .reset_index()
    )

    receptions = (
        completed.groupby("pass_recipient")
        .agg(
            passes_received=("id", "count")
        )
        .reset_index()
        .rename(columns={"pass_recipient": "player"})
    )

    avg_positions = avg_positions.merge(receptions, on="player", how="left")
    avg_positions["passes_received"] = avg_positions["passes_received"].fillna(0).astype(int)
    avg_positions["total_involvement"] = avg_positions["passes_played"] + avg_positions["passes_received"]

    pass_links = (
        completed.groupby(["player", "pass_recipient"])
        .size()
        .reset_index(name="pass_count")
        .sort_values("pass_count", ascending=False)
        .reset_index(drop=True)
    )

    return avg_positions, pass_links


def plot_pass_network(avg_positions, pass_links, team_name, output_path, min_pass_count=6):
    """
    Trace le réseau de passes d'une équipe.
    """
    pitch = Pitch(pitch_type="statsbomb", line_zorder=2)
    fig, ax = pitch.draw(figsize=(12, 8))

    links_filtered = pass_links[pass_links["pass_count"] >= min_pass_count].copy()

    for _, row in links_filtered.iterrows():
        passer = row["player"]
        receiver = row["pass_recipient"]
        pass_count = row["pass_count"]

        passer_pos = avg_positions[avg_positions["player"] == passer]
        receiver_pos = avg_positions[avg_positions["player"] == receiver]

        if passer_pos.empty or receiver_pos.empty:
            continue

        x1, y1 = passer_pos.iloc[0][["avg_x", "avg_y"]]
        x2, y2 = receiver_pos.iloc[0][["avg_x", "avg_y"]]

        pitch.lines(
            x1, y1, x2, y2,
            lw=pass_count * 0.4,
            ax=ax,
            alpha=0.5
        )

    pitch.scatter(
        avg_positions["avg_x"],
        avg_positions["avg_y"],
        s=avg_positions["total_involvement"] * 12,
        ax=ax,
        alpha=0.9
    )

    for _, row in avg_positions.iterrows():
        ax.text(
            row["avg_x"],
            row["avg_y"],
            row["player"].split()[0],
            ha="center",
            va="center",
            fontsize=8
        )

    ax.set_title(f"Réseau de passes - {team_name}", fontsize=16)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"Figure sauvegardée : {output_path}")
    print(f"Nombre de joueurs affichés : {avg_positions.shape[0]}")
    print(f"Nombre de liens affichés : {links_filtered.shape[0]}")


def plot_progressive_pass_map(progressive_passes, team_name, output_path):
    """
    Trace la carte des passes progressives réussies de l'équipe.
    """
    pitch = Pitch(pitch_type="statsbomb", line_zorder=2)
    fig, ax = pitch.draw(figsize=(12, 8))

    pitch.arrows(
        progressive_passes["x"],
        progressive_passes["y"],
        progressive_passes["end_x"],
        progressive_passes["end_y"],
        ax=ax,
        width=1.8,
        headwidth=4,
        headlength=4,
        alpha=0.6
    )

    ax.set_title(f"Passes progressives - {team_name}", fontsize=16)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"Figure sauvegardée : {output_path}")
    print(f"Nombre de passes progressives affichées : {progressive_passes.shape[0]}")


if __name__ == "__main__":
    passes = load_passes()
    spain_passes = get_team_passes(passes, "Spain")

    avg_positions, pass_links = build_pass_network_data(spain_passes)
    progressive_passes = get_progressive_team_passes(spain_passes)

    print("Dimensions avg_positions :")
    print(avg_positions.shape)

    print("\nTop 10 positions moyennes / implication :")
    print(avg_positions.sort_values("total_involvement", ascending=False).head(10))

    print("\nTop 15 liens de passes :")
    print(pass_links.head(15))

    print("\nTop 10 joueurs en passes progressives :")
    print(
        progressive_passes.groupby("player")
        .size()
        .reset_index(name="progressive_passes")
        .sort_values("progressive_passes", ascending=False)
        .head(10)
    )

    network_file = FIGURES_DIR / "spain_pass_network.png"
    progression_file = FIGURES_DIR / "spain_progressive_passes.png"

    plot_pass_network(avg_positions, pass_links, "Spain", network_file, min_pass_count=6)
    plot_progressive_pass_map(progressive_passes, "Spain", progression_file)