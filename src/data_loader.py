from pathlib import Path
from statsbombpy import sb


def load_competitions():
    """
    Charge la liste des compétitions disponibles via StatsBomb open data.
    """
    return sb.competitions()


def get_euro_2024(competitions):
    """
    Filtre la compétition Euro 2024.
    """
    euro_2024 = competitions[
        (competitions["competition_name"].str.contains("Euro", case=False, na=False)) &
        (competitions["season_name"].astype(str).str.contains("2024", na=False))
    ]
    return euro_2024


def load_matches(competition_id, season_id):
    """
    Charge les matchs d'une compétition / saison.
    """
    return sb.matches(competition_id=competition_id, season_id=season_id)


def get_match_by_teams(matches, home_team, away_team):
    """
    Récupère un match précis à partir du nom des équipes.
    """
    target_match = matches[
        (matches["home_team"] == home_team) &
        (matches["away_team"] == away_team)
    ]
    return target_match


def load_events(match_id):
    """
    Charge les événements détaillés d'un match.
    """
    return sb.events(match_id=match_id)


def load_lineups(match_id):
    """
    Charge les compositions d'un match.
    """
    return sb.lineups(match_id=match_id)


def save_raw_data(events, lineups, output_dir):
    """
    Sauvegarde les données brutes en local.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    events_path = output_path / "events.csv"
    events.to_csv(events_path, index=False)

    for team_name, lineup_df in lineups.items():
        safe_team_name = team_name.lower().replace(" ", "_")
        lineup_path = output_path / f"lineup_{safe_team_name}.csv"
        lineup_df.to_csv(lineup_path, index=False)

    print(f"\nDonnées brutes sauvegardées dans : {output_path.resolve()}")


if __name__ == "__main__":
    competitions = load_competitions()
    euro_2024 = get_euro_2024(competitions)

    if euro_2024.empty:
        print("Aucune compétition Euro 2024 trouvée.")
    else:
        competition_id = int(euro_2024.iloc[0]["competition_id"])
        season_id = int(euro_2024.iloc[0]["season_id"])

        matches = load_matches(competition_id, season_id)
        target_match = get_match_by_teams(matches, "Spain", "Germany")

        if target_match.empty:
            print("Match Spain vs Germany introuvable.")
        else:
            match_id = int(target_match.iloc[0]["match_id"])
            print(f"Match trouvé : Spain vs Germany | match_id = {match_id}")

            events = load_events(match_id)
            lineups = load_lineups(match_id)

            print("\nDimensions des events :")
            print(events.shape)

            output_dir = "data/raw/spain_vs_germany_3942226"
            save_raw_data(events, lineups, output_dir)