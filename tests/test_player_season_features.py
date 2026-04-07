import unittest

import pandas as pd

from src.features.player_season_features import build_player_season_stats


class PlayerSeasonFeaturesTestCase(unittest.TestCase):
    def test_build_player_season_stats_returns_one_row_per_player_team_competition(self):
        player_match_df = pd.DataFrame(
            [
                {
                    "match_id": 1,
                    "player": "Jane Doe",
                    "team": "Paris FC",
                    "competition_name": "Ligue 2",
                    "position": "Right Wing",
                    "shots": 2,
                    "goals": 1,
                    "xg": 0.4,
                    "passes_attempted": 20,
                    "passes_completed": 15,
                    "key_passes": 2,
                    "progressive_passes": 4,
                    "carries": 6,
                    "progressive_carries": 3,
                    "passes_into_final_third": 5,
                    "passes_into_box": 2,
                    "touches_in_final_third": 12,
                    "touches_in_box": 4,
                    "recoveries": 3,
                    "interceptions": 1,
                    "duels": 5,
                },
                {
                    "match_id": 2,
                    "player": "Jane Doe",
                    "team": "Paris FC",
                    "competition_name": "Ligue 2",
                    "position": "Right Wing",
                    "shots": 1,
                    "goals": 0,
                    "xg": 0.2,
                    "passes_attempted": 18,
                    "passes_completed": 14,
                    "key_passes": 1,
                    "progressive_passes": 3,
                    "carries": 5,
                    "progressive_carries": 2,
                    "passes_into_final_third": 3,
                    "passes_into_box": 1,
                    "touches_in_final_third": 10,
                    "touches_in_box": 3,
                    "recoveries": 2,
                    "interceptions": 1,
                    "duels": 4,
                },
                {
                    "match_id": 2,
                    "player": "Jane Doe",
                    "team": "Paris FC",
                    "competition_name": "Ligue 2",
                    "position": "Striker",
                    "shots": 1,
                    "goals": 1,
                    "xg": 0.3,
                    "passes_attempted": 5,
                    "passes_completed": 4,
                    "key_passes": 0,
                    "progressive_passes": 0,
                    "carries": 1,
                    "progressive_carries": 0,
                    "passes_into_final_third": 0,
                    "passes_into_box": 1,
                    "touches_in_final_third": 2,
                    "touches_in_box": 2,
                    "recoveries": 0,
                    "interceptions": 0,
                    "duels": 2,
                },
            ]
        )

        result = build_player_season_stats(player_match_df)

        self.assertEqual(len(result), 1)
        self.assertEqual(result.loc[0, "matches_played"], 2)
        self.assertEqual(result.loc[0, "position"], "Right Wing")
        self.assertEqual(result.loc[0, "position_matches_played"], 2)
        self.assertEqual(result.loc[0, "shots"], 4)
        self.assertEqual(result.loc[0, "goals"], 2)
        self.assertAlmostEqual(result.loc[0, "pass_completion_pct"], 76.74, places=2)


if __name__ == "__main__":
    unittest.main()
