import unittest

import pandas as pd

from src.features.role_scoring import apply_role_context_penalty


class RoleScoringTestCase(unittest.TestCase):
    def test_apply_role_context_penalty_penalizes_out_of_role_groups(self):
        score = pd.Series([1.2, 1.2, 0.8])
        position_groups = pd.Series(["Ailiers", "Milieux centraux", "Défenseurs centraux"])
        target_groups = ["Ailiers", "Milieux offensifs"]

        result = apply_role_context_penalty(
            score=score,
            position_groups=position_groups,
            target_groups=target_groups,
            penalty=1.0,
        )

        self.assertAlmostEqual(result.iloc[0], 1.2, places=6)
        self.assertAlmostEqual(result.iloc[1], 0.2, places=6)
        self.assertAlmostEqual(result.iloc[2], -0.2, places=6)


if __name__ == "__main__":
    unittest.main()
