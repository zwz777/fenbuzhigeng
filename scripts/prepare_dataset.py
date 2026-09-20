"""检查 YOLO 数据集并生成/更新 data.yaml。"""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def count_images(path: Path) -> int:
    return sum(1 for item in path.iterdir() if item.suffix.lower() in IMAGE_SUFFIXES) if path.exists() else 0


def validate_split(root: Path, split: str) -> tuple[int, int]:
    image_dir = root / "images" / split
    label_dir = root / "labels" / split
    image_count = count_images(image_dir)
    label_count = len(list(label_dir.glob("*.txt"))) if label_dir.exists() else 0
    missing = []
    if image_dir.exists():
        for image in image_dir.iterdir():
            if image.suffix.lower() in IMAGE_SUFFIXES and not (label_dir / f"{image.stem}.txt").exists():
                missing.append(image.name)
    if missing:
        preview = ", ".join(missing[:3])
        raise ValueError(f"{split} 中有图片缺少标签: {preview}")
    return image_count, label_count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("data/weed"))
    parser.add_argument("--class-name", default="weed")
    parser.add_argument("--strict", action="store_true", help="没有图片时返回失败，适合CI")
    args = parser.parse_args()

    root = args.root
    for split in ("train", "val"):
        (root / "images" / split).mkdir(parents=True, exist_ok=True)
        (root / "labels" / split).mkdir(parents=True, exist_ok=True)
    train_images, train_labels = validate_split(root, "train")
    val_images, val_labels = validate_split(root, "val")

    data_file = root / "data.yaml"
    data_file.write_text(
        yaml.safe_dump(
            {"path": ".", "train": "images/train", "val": "images/val", "names": {0: args.class_name}},
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    print(f"数据集配置已写入: {data_file}")
    print(f"train: images={train_images}, labels={train_labels}; val: images={val_images}, labels={val_labels}")
    if args.strict and (train_images == 0 or val_images == 0):
        raise SystemExit("训练集和验证集都需要至少有一张图片")


if __name__ == "__main__":
    main()

