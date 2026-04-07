from __future__ import annotations

from typing import Iterable

import pandas as pd

from app.utils.labels import DIMENSION_DESCRIPTIONS, DIMENSION_LABELS, ROLE_DESCRIPTIONS, ROLE_LABELS


DIMENSION_COLUMNS = list(DIMENSION_LABELS.keys())


def get_role_score_columns(df: pd.DataFrame) -> list[str]:
    return [col for col in ROLE_LABELS if col in df.columns]


def build_role_score_map(player_row: pd.Series) -> dict[str, float]:
    role_scores = {}
    for column, label in ROLE_LABELS.items():
        if column in player_row.index:
            role_scores[label] = float(player_row[column])
    return role_scores


def get_top_roles(player_row: pd.Series, top_n: int = 3) -> list[tuple[str, float]]:
    role_scores = build_role_score_map(player_row)
    return sorted(role_scores.items(), key=lambda item: item[1], reverse=True)[:top_n]


def get_top_dimensions(player_row: pd.Series, top_n: int = 2) -> list[tuple[str, float]]:
    scores = []
    for column, label in DIMENSION_LABELS.items():
        if column in player_row.index:
            scores.append((label, float(player_row[column])))
    return sorted(scores, key=lambda item: item[1], reverse=True)[:top_n]


def get_watch_dimensions(player_row: pd.Series, top_n: int = 2) -> list[tuple[str, float]]:
    scores = []
    for column, label in DIMENSION_LABELS.items():
        if column in player_row.index:
            scores.append((label, float(player_row[column])))
    return sorted(scores, key=lambda item: item[1])[:top_n]


def build_profile_summary(player_row: pd.Series) -> str:
    top_roles = get_top_roles(player_row, top_n=2)
    top_dimensions = get_top_dimensions(player_row, top_n=2)

    if not top_roles or not top_dimensions:
        return "Profil disponible, mais le résumé automatique reste limité par les données."

    role_1, role_1_score = top_roles[0]
    dimension_1, _ = top_dimensions[0]
    dimension_2, _ = top_dimensions[1] if len(top_dimensions) > 1 else top_dimensions[0]

    reliability_note = (
        "échantillon solide"
        if int(player_row.get("meets_minimum_minutes_900", 0)) == 1
        else "échantillon à consolider"
    )

    return (
        f"{player_row['player']} ressort comme un profil de {role_1.lower()} "
        f"avec un score de {role_1_score:.3f}. Ses meilleurs marqueurs sont "
        f"{dimension_1.lower()} et {dimension_2.lower()}, pour un {reliability_note}."
    )


def build_shortlist_rationale(player_row: pd.Series, selected_role: str) -> str:
    role_label = ROLE_LABELS.get(selected_role, selected_role)
    top_dimensions = get_top_dimensions(player_row, top_n=2)
    dimension_labels = [label.lower() for label, _ in top_dimensions]

    if len(dimension_labels) == 1:
        dimension_text = dimension_labels[0]
    else:
        dimension_text = " et ".join(dimension_labels)

    return (
        f"Bon fit pour {role_label.lower()} grâce à {dimension_text}."
        if dimension_text
        else f"Bon fit pour {role_label.lower()}."
    )


def build_metric_snapshot(player_row: pd.Series, metrics: Iterable[str]) -> list[tuple[str, float]]:
    snapshot = []
    for metric in metrics:
        if metric in player_row.index and pd.notna(player_row[metric]):
            snapshot.append((metric, float(player_row[metric])))
    return snapshot


def role_methodology_rows() -> list[dict[str, str]]:
    rows = []
    for score_column, label in ROLE_LABELS.items():
        rows.append(
            {
                "role_score": score_column,
                "label": label,
                "description": ROLE_DESCRIPTIONS[score_column],
            }
        )
    return rows


def dimension_methodology_rows() -> list[dict[str, str]]:
    rows = []
    for column, label in DIMENSION_LABELS.items():
        rows.append(
            {
                "column": column,
                "label": label,
                "description": DIMENSION_DESCRIPTIONS[column],
            }
        )
    return rows
