import unittest

import pandas as pd

from src.features.player_season_enriched import build_enriched_player_season


class PlayerSeasonEnrichedTestCase(unittest.TestCase):
    def test_build_enriched_player_season_merges_minutes_on_player_team_and_competition(self):
        player_season_df = pd.DataFrame(
            [
                {
                    "player": "Jane Doe",
                    "team": "Paris FC",
                    "competition_name": "Ligue 2",
                    "position": "Right Wing",
                    "position_matches_played": 2,
                    "matches_played": 2,
                    "shots": 4,
                    "goals": 2,
                    "xg": 0.9,
                    "passes_attempted": 43,
                    "passes_completed": 34,
                    "pass_completion_pct": 79.07,
                    "key_passes": 3,
                    "progressive_passes": 7,
                    "carries": 12,
                    "progressive_carries": 5,
                    "passes_into_final_third": 8,
                    "passes_into_box": 4,
                    "touches_in_final_third": 24,
                    "touches_in_box": 9,
                    "recoveries": 5,
                    "interceptions": 2,
                    "duels": 11,
                }
            ]
        )

        player_match_minutes_df = pd.DataFrame(
            [
                {
                    "match_id": 11,
                    "player_name": "Jane Doe",
                    "team_name": "Paris FC",
                    "minutes_played": 90,
                    "is_starter": 1,
                },
                {
                    "match_id": 12,
                    "player_name": "Jane Doe",
                    "team_name": "Paris FC",
                    "minutes_played": 45,
                    "is_starter": 0,
                },
                {
                    "match_id": 21,
                    "player_name": "Jane Doe",
                    "team_name": "Other Club",
                    "minutes_played": 90,
                    "is_starter": 1,
                },
            ]
        )

        matches_df = pd.DataFrame(
            [
                {"match_id": 11, "competition_name": "Ligue 2"},
                {"match_id": 12, "competition_name": "Ligue 2"},
                {"match_id": 21, "competition_name": "Ligue 1"},
            ]
        )

        result = build_enriched_player_season(player_season_df, player_match_minutes_df, matches_df)

        self.assertEqual(result.loc[0, "minutes_played"], 135)
        self.assertEqual(result.loc[0, "starts"], 1)
        self.assertEqual(result.loc[0, "matches_in_minutes_table"], 2)
        self.assertAlmostEqual(result.loc[0, "shots_per90"], 2.67, places=2)
        self.assertEqual(result.loc[0, "meets_minimum_minutes_900"], 0)


if __name__ == "__main__":
    unittest.main()
