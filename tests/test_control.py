from __future__ import annotations

import unittest

from fenbu_zhigeng import Action, Detection, MockRobot, TargetPolicy


class TargetPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.policy = TargetPolicy(target_class="weed", min_confidence=0.55, center_band=0.12)

    def test_left_target_moves_left(self) -> None:
        self.assertEqual(self.policy.decide(Detection("weed", 0.9, 0.2, 0.5)), Action.MOVE_LEFT)

    def test_right_target_moves_right(self) -> None:
        self.assertEqual(self.policy.decide(Detection("weed", 0.9, 0.8, 0.5)), Action.MOVE_RIGHT)

    def test_center_target_sprays(self) -> None:
        self.assertEqual(self.policy.decide(Detection("weed", 0.9, 0.5, 0.5)), Action.SPRAY)

    def test_low_confidence_holds(self) -> None:
        self.assertEqual(self.policy.decide(Detection("weed", 0.2, 0.5, 0.5)), Action.HOLD)

    def test_other_class_holds(self) -> None:
        self.assertEqual(self.policy.decide(Detection("rock", 0.9, 0.5, 0.5)), Action.HOLD)

    def test_mock_robot_records_commands(self) -> None:
        robot = MockRobot()
        robot.execute(Action.SPRAY)
        self.assertEqual(robot.history, [Action.SPRAY])


if __name__ == "__main__":
    unittest.main()

