"""不接硬件时，演示检测结果到动作的完整控制链路。"""

from __future__ import annotations

from fenbu_zhigeng import Detection, MockRobot, TargetPolicy


def main() -> None:
    policy = TargetPolicy(target_class="weed", min_confidence=0.55, center_band=0.12)
    robot = MockRobot(spray_duration_ms=300)
    samples = [
        Detection("weed", 0.91, 0.20, 0.50),
        Detection("weed", 0.88, 0.50, 0.52),
        Detection("weed", 0.94, 0.82, 0.49),
        Detection("weed", 0.31, 0.50, 0.50),
        Detection("rock", 0.99, 0.50, 0.50),
    ]
    for detection in samples:
        action = policy.decide(detection)
        print(f"detection={detection} -> {action.value}")
        robot.execute(action)


if __name__ == "__main__":
    main()

