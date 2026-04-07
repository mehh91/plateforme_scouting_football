import unittest

import pandas as pd

from src.utils.player_profiles import add_player_key, select_primary_player_rows


class PlayerProfilesTestCase(unittest.TestCase):
    def test_add_player_key_builds_stable_identity(self):
        df = pd.DataFrame(
            [
                {
                    "player": "Jane Doe",
                    "team": "Paris FC",
                    "competition_name": "Ligue 2",
                }
            ]
        )

        result = add_player_key(df)

        self.assertEqual(result.loc[0, "player_key"], "Jane Doe||Paris FC||Ligue 2")

    def test_select_primary_player_rows_prefers_position_match_volume(self):
        df = pd.DataFrame(
            [
                {
                    "player": "Jane Doe",
                    "team": "Paris FC",
                    "competition_name": "Ligue 2",
                    "position": "Right Wing",
                    "position_matches_played": 18,
                    "matches_played": 24,
                    "minutes_played": 2000,
                },
                {
                    "player": "Jane Doe",
                    "team": "Paris FC",
                    "competition_name": "Ligue 2",
                    "position": "Striker",
                    "position_matches_played": 6,
                    "matches_played": 24,
                    "minutes_played": 2000,
                },
            ]
        )

        result = select_primary_player_rows(df)

        self.assertEqual(len(result), 1)
        self.assertEqual(result.loc[0, "position"], "Right Wing")


if __name__ == "__main__":
    unittest.main()
