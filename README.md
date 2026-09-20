# 分布智耕：视觉识别与精准喷施验证项目

这是“分布智耕”项目的可复现软件原型。当前目标不是直接做出完整农田机器人，而是先在电脑上跑通一条可以解释、可以复现、可以逐步接硬件的链路：

```text
图片/摄像头 -> YOLO目标检测 -> 目标位置 -> 动作策略 -> 模拟执行器/串口执行器
```

第一版的作业对象建议使用“模拟杂草”或带颜色的标记物，执行动作使用清水微量喷施。不要在没有完成安全测试前使用农药。

## 当前已经包含

- YOLO 数据集目录约定和数据检查脚本；
- YOLO 训练、验证、图片/视频推理脚本；
- 预测框可视化和 JSON 结果输出；
- 将目标位置转换成“左移、右移、对准、喷施”的动作策略；
- 本地 `MockRobot` 模拟器；
- 面向后续树莓派/香橙派的 JSON 串口协议和串口执行器；
- 单元测试、配置文件和硬件接入说明。

## 1. 环境准备

建议使用 Python 3.10 或 3.11。Windows PowerShell 示例：

```powershell
py -3.11 -m venv .venv
\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

如果有 NVIDIA 显卡，请根据 PyTorch 官方说明安装匹配 CUDA 的版本；没有显卡也可以用 CPU 跑小规模验证，只是训练更慢。

## 2. 数据集目录

采用 YOLO Detection 格式：

```text
data/weed/
├── data.yaml
├── images/
│   ├── train/
│   └── val/
└── labels/
    ├── train/
    └── val/
```

每个图片对应一个同名 `.txt` 标签，例如 `images/train/a.jpg` 对应 `labels/train/a.txt`。标签每行格式为：

```text
class_id center_x center_y width height
```

坐标均为 0 到 1 的归一化值。当前示例只设置一个类别 `weed`，以后可以扩展为 `crop`、`weed`、`rock` 等类别。

将自己的图片和标签放入目录后，先执行：

```powershell
python scripts/prepare_dataset.py --root data/weed --class-name weed
```

没有图片时，该命令会提示数据集尚未准备好；这是正常的，仓库不会提交个人图片和训练权重。

## 3. 训练、验证和推理

### 训练

```powershell
python scripts/train.py `
  --data data/weed/data.yaml `
  --model yolo11n.pt `
  --epochs 50 `
  --imgsz 640 `
  --device cpu
```

训练结果默认保存在 `runs/detect/weed/`。第一次运行会自动下载预训练模型，因此需要网络；之后可以使用本地 `.pt` 文件离线运行。

### 验证

```powershell
python scripts/validate.py `
  --data data/weed/data.yaml `
  --model runs/detect/weed/weights/best.pt `
  --device cpu
```

### 图片或视频推理

```powershell
python scripts/predict.py `
  --model runs/detect/weed/weights/best.pt `
  --source path/to/test.jpg `
  --output runs/predict/demo
```

脚本会保存标注图片和 `predictions.json`。JSON 中除了框坐标，还会记录目标中心点的归一化坐标，后续控制程序可以直接使用。

## 4. 先用模拟器验证机械臂逻辑

不买硬件也可以先验证“识别结果如何转成动作”：

```powershell
python scripts/demo_controller.py
```

示例策略是：

- 目标在画面左侧：请求底盘左移；
- 目标在画面右侧：请求底盘右移；
- 目标进入中间区域：停止底盘，机械臂移动到预设喷施姿态；
- 目标置信度不足：不动作；
- 喷施动作默认只持续很短时间，并由模拟执行器打印出来。

这个策略故意不做复杂的三维定位和实时逆运动学，适合面试样机的第一阶段。

## 5. 后续接硬件

推荐先使用电脑运行视觉模型，树莓派/香橙派只负责摄像头采集和执行器控制。串口发送一行 JSON，例如：

```json
{"type":"command","action":"spray","duration_ms":300}
```

后续可以把 `MockRobot` 替换为 `SerialRobot`，不需要重写识别和动作策略。具体接线、安全限位和电源设计见 [`docs/hardware.md`](docs/hardware.md)。

## 6. 测试

```powershell
python -m unittest discover -s tests -v
python -m compileall src scripts tests
```

## 7. GitHub复现建议

提交以下内容：

- 源代码、配置文件、README、测试；
- `requirements.txt`；
- 小尺寸示例图片或公开数据集下载说明；
- 训练命令和评估结果；
- 使用的模型名称、训练轮数、设备信息。

不要提交：

- `.venv/`、缓存、个人照片；
- 大型训练权重；
- 含有个人隐私的田间视频；
- 真实农药配置和未经验证的自动喷施代码。

## 硬件购买建议

当前不建议马上购买昂贵板卡。第一阶段用电脑+USB摄像头跑通软件。需要边缘端时，优先考虑：

1. **树莓派 5 8GB**：资料、社区和 GPIO 生态更成熟，适合后续控制电机、舵机、继电器和摄像头；
2. **香橙派 5 8GB**：算力和价格可能更有吸引力，但需要提前确认系统镜像、摄像头驱动和模型推理环境；
3. **不要把板卡直接接电机**：必须增加电机驱动器、独立电源、降压模块、保险和急停开关。

第一批硬件建议只买：USB摄像头、ESP32或树莓派、2WD小车底盘、带编码器直流减速电机、舵机机械臂、水泵、MOS管模块和独立电源。真实农药喷施暂不采购。
