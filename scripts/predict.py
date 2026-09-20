"""对图片、目录或视频执行 YOLO 推理，并导出可供控制程序读取的 JSON。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2


def result_to_detections(result) -> list[dict]:
    names = result.names
    detections: list[dict] = []
    if result.boxes is None:
        return detections
    for box in result.boxes:
        xyxy = [float(value) for value in box.xyxy[0].tolist()]
        confidence = float(box.conf[0].item())
        class_id = int(box.cls[0].item())
        height, width = result.orig_shape
        center_x = ((xyxy[0] + xyxy[2]) / 2) / width
        center_y = ((xyxy[1] + xyxy[3]) / 2) / height
        detections.append(
            {
                "class_id": class_id,
                "class_name": names[class_id],
                "confidence": round(confidence, 6),
                "xyxy": [round(value, 2) for value in xyxy],
                "center": {"x": round(center_x, 6), "y": round(center_y, 6)},
            }
        )
    return detections


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--source", required=True, help="图片、目录、视频路径或摄像头编号")
    parser.add_argument("--output", type=Path, default=Path("runs/predict/demo"))
    parser.add_argument("--conf", type=float, default=0.55)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args()

    from ultralytics import YOLO

    args.output.mkdir(parents=True, exist_ok=True)
    source: str | int = int(args.source) if args.source.isdigit() else args.source
    model = YOLO(args.model)
    results = model.predict(source=source, conf=args.conf, imgsz=args.imgsz, device=args.device, stream=True, save=False)
    records = []
    for index, result in enumerate(results):
        detections = result_to_detections(result)
        plotted = result.plot()
        image_file = args.output / f"frame_{index:05d}.jpg"
        cv2.imwrite(str(image_file), plotted)
        records.append({"source": str(result.path), "image": str(image_file), "detections": detections})
    (args.output / "predictions.json").write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"推理结果已保存到: {args.output}")


if __name__ == "__main__":
    main()

