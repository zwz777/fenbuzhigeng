# 公开数据集接入说明

## 推荐顺序

### 1. AgriWeedsDetection 作为快速验证集

链接：<https://universe.roboflow.com/robotraining/agriweedsdetection_1>

该项目页面显示有 459 张图片、6 个杂草类别，许可证标注为 CC BY 4.0，并支持导出 YOLO 格式。它适合先验证本仓库的训练、验证和推理流程。

在 Roboflow 页面中选择对应数据集版本，点击 Download Dataset，格式选择 YOLOv8/YOLOv11 均可。下载后将图片和标签整理为：

```text
data/weed/
├── images/train
├── images/val
├── labels/train
└── labels/val
```

如果类别是具体杂草名称，不要把 `data.yaml` 误写成只有一个 `weed` 类。可以使用：

```powershell
python scripts/prepare_dataset.py `
  --root data/weed `
  --class-name Bodyak `
  --class-name "carpet weeds" `
  --class-name crabgrass `
  --class-name fleabane `
  --class-name Osot `
  --class-name Shavel
```

第一版控制程序仍可以把这些类别统一视为“需要处理的杂草”，但训练标签中的类别顺序必须与下载数据集的 `data.yaml` 完全一致。

### 2. CornWeed 作为正式实验集

链接：<https://zenodo.org/records/7961764>

该数据集有 3574 张带框标注图片，提供 YOLO 和 COCO 格式，包含 maize、weeds 以及作物行信息，和农业机器人场景更接近。压缩包约 8.7 GB，不建议一开始就下载。

### 3. Chilli Crop-Weed 作为两类别实验集

链接：<https://github.com/sbhaktavatsala/chilli-weed-dataset>

该仓库说明提供 2200 张图片、YOLO 标签和 `crop`/`weed` 两类，适合当前“识别杂草后喷施”的控制逻辑。不过页面同时出现 GPL-2.0 和 README 中的 CC BY 4.0 说明，使用前应以数据集作者的最终许可为准。

## 数据集检查流程

下载后先运行：

```powershell
python scripts/prepare_dataset.py --root data/weed --strict --class-name crop --class-name weed
```

然后检查：

- 每张图片都有同名 `.txt` 标签；
- `class_id` 没有超过类别数量；
- 训练集、验证集和测试集没有来自同一视频的连续帧混入不同集合；
- `data.yaml` 中的类别顺序与标签中的数字一致。

## 许可证与 GitHub 提交

公开数据集的原始图片不要直接提交到本项目 GitHub。仓库只保留：

- 数据集主页链接；
- 下载和转换说明；
- 许可证及引用信息；
- 少量不受限制的示例图片（如果许可允许）。

模型权重、训练结果和个人田间照片也默认不提交，项目中的 `.gitignore` 已经排除了这些大文件和数据目录。

## 最终数据策略

公开数据集用于让软件流程先跑通；真正面向河津黄土高原时，还需要补拍本地数据。建议第一批采集 100–300 张图片，覆盖不同光照、土壤、作物行距、杂草密度和拍摄高度，再用这些图片做微调和最终测试。

