"""执行器抽象：先用 MockRobot，后续替换为 SerialRobot。"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from typing import Protocol

from .control import Action


@dataclass(frozen=True)
class Command:
    action: str
    duration_ms: int = 0

    def to_json_line(self) -> str:
        payload = {"type": "command", **asdict(self)}
        return json.dumps(payload, ensure_ascii=False) + "\n"


class Robot(Protocol):
    def execute(self, action: Action) -> None:
        ...


class MockRobot:
    """本地模拟器，用于不接硬件时验证控制逻辑。"""

    def __init__(self, spray_duration_ms: int = 300) -> None:
        self.spray_duration_ms = spray_duration_ms
        self.history: list[Action] = []

    def execute(self, action: Action) -> None:
        self.history.append(action)
        print(f"[MOCK] action={action.value}")


class SerialRobot:
    """通过一行一条 JSON 命令连接 ESP32/树莓派控制板。"""

    def __init__(self, port: str, baudrate: int = 115200, timeout_s: float = 1.0) -> None:
        try:
            import serial
        except ImportError as exc:  # pragma: no cover - 仅在真实硬件模式触发
            raise RuntimeError("使用 SerialRobot 前请安装 pyserial") from exc
        self._serial = serial.Serial(port=port, baudrate=baudrate, timeout=timeout_s)

    def execute(self, action: Action) -> None:
        duration_ms = 300 if action == Action.SPRAY else 250
        command = Command(action=action.value, duration_ms=duration_ms)
        self._serial.write(command.to_json_line().encode("utf-8"))
        self._serial.flush()
        time.sleep(duration_ms / 1000)

    def close(self) -> None:
        self._serial.close()

