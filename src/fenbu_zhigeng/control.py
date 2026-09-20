"""把视觉检测结果转换成可执行的低风险动作。"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Action(str, Enum):
    """第一版执行器支持的有限动作集合。"""

    HOLD = "hold"
    MOVE_LEFT = "move_left"
    MOVE_RIGHT = "move_right"
    ALIGN = "align"
    SPRAY = "spray"


@dataclass(frozen=True)
class Detection:
    """检测结果的最小控制字段。坐标采用 0 到 1 的归一化值。"""

    class_name: str
    confidence: float
    center_x: float
    center_y: float


@dataclass(frozen=True)
class TargetPolicy:
    """将目标中心点映射为动作。

    这是演示阶段的二维策略，不代表最终田间机器人定位算法。
    """

    target_class: str = "weed"
    min_confidence: float = 0.55
    center_band: float = 0.12

    def decide(self, detection: Detection | None) -> Action:
        if detection is None:
            return Action.HOLD
        if detection.class_name != self.target_class:
            return Action.HOLD
        if not 0.0 <= detection.confidence <= 1.0:
            raise ValueError("confidence 必须位于 0 到 1 之间")
        if not 0.0 <= detection.center_x <= 1.0:
            raise ValueError("center_x 必须位于 0 到 1 之间")
        if detection.confidence < self.min_confidence:
            return Action.HOLD

        left = 0.5 - self.center_band
        right = 0.5 + self.center_band
        if detection.center_x < left:
            return Action.MOVE_LEFT
        if detection.center_x > right:
            return Action.MOVE_RIGHT
        return Action.SPRAY

