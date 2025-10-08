# Minecraft-AI: 基于 Mineflayer 和 PyTorch 的 Minecraft AI 训练框架

![Status](https://img.shields.io/badge/Status-In%20Development-orange) ![Warning](https://img.shields.io/badge/Warning-Do%20Not%20Pull-red)

> [!WARNING]
> **本项目正在密集开发中，当前为主干开发分支，请勿直接拉取使用。**
>
> 目前的版本仅用于开发和测试，训练脚本和配置随时可能变更或删除，不保证任何可用性。请等待正式的 Release 版本发布。
> 正式 Release 位于 [**Minecraft-Agent**](https://github.com/QcrTiMo/Minecraft-Agent) 仓库。


这是一个用于在《我的世界》(Minecraft) 中训练智能 AI 的强化学习框架。本项目利用 Node.js 端的 [**Mineflayer**](https://github.com/PrismarineJS/mineflayer) 库与游戏进行底层交互，并通过 WebSocket 将其封装成一个标准的、可供 Python 端调用的 **Gymnasium** 环境。AI 的训练基于 **PyTorch** 和 **Stable Baselines3** 库。

整个框架的核心特性是**自动化**、**模块化**和**持续学习**：
*   **真实服务器:** 只需修改配置，即可让 AI 连接到外部的真实 Minecraft 服务器（如 Paper/Spigot）进行训练和应用。
*   **统一配置管理:** 所有超参数（训练步数、学习率、奖励函数权重、端口等）均在 `config.yaml` 文件中集中管理。
*   **自动化持续学习:** 训练脚本会自动检测并加载已有的模型，在其基础上继续训练，实现课程学习和持续改进。
*   **智能检查点机制:** 训练过程中会自动保存表现最佳的模型，防止因意外中断或后期训练发散而丢失成果。

## 核心技术

*   **环境端 (JavaScript):**
    *   [Node.js](https://nodejs.org/) - 运行时环境
    *   [Mineflayer](https://github.com/PrismarineJS/mineflayer) - Minecraft 机器人（客户端）API
    *   [Flying Squid](https://github.com/PrismarineJS/flying-squid) - Minecraft 服务器实现
    *   [Prismarine Viewer](https://github.com/PrismarineJS/prismarine-viewer) - 浏览器可视化工具
    *   [ws](https://github.com/websockets/ws) - WebSocket 通信库
    *   [js-yaml](https://github.com/nodeca/js-yaml) - YAML 配置文件解析器
*   **智能体端 (Python):**
    *   [Python](https://www.python.org/)
    *   [PyTorch](https://pytorch.org/) - 深度学习框架
    *   [Stable Baselines3](https://github.com/DLR-RM/stable-baselines3) - 强化学习算法库
    *   [Gymnasium](https://gymnasium.farama.org/) - AI 训练环境 API 标准
    *   [websockets](https://websockets.readthedocs.io/en/stable/) - WebSocket 通信库
    *   [matplotlib](https://matplotlib.org/) - 训练曲线绘图库
    *   [PyYAML](https://pyyaml.org/) - YAML 配置文件解析器

## 项目结构

```
Minecraft-AI/
├── actions/                 # (JS) AI 在游戏中的原子动作定义
├── agent/                   # (PY) AI 智能体 (PPO 算法封装)
├── env/                     # (PY) Gymnasium 环境封装
├── logs/                    # (Output) 存放 TensorBoard 日志和学习曲线图
├── models/                  # (Output) 存放训练好的模型文件
├── node_modules/            # (JS) Node.js 依赖
├── server/                  # (JS) 服务器相关模块
├── train/                   # (PY) 训练任务的核心逻辑
│ ├── callbacks/             # - 自定义绘图回调
│ ├── navigation/            # - 具体的训练任务脚本
│ └── reward/                # - 任务的奖励函数
├── utils/                   # (Shared) 通用辅助工具
│ ├── checkpoint_callback.py # (PY) 智能模型检查点回调
│ ├── config.py              # (PY) Python 端 YAML 配置加载器
│ ├── config.js              # (JS) JavaScript 端 YAML 配置加载器
│ └── model.py               # (PY) 自动化模型加载/创建管理器
├── .gitignore
├── bot.js                   # (JS) 机器人主配置
├── config.yaml              # (Config) 全局配置文件，所有超参数在此设置
├── package.json
├── README.md                # 本文档
├── requirements.txt         # (PY) Python 依赖列表
└── start.js                 # (JS) 项目主入口：启动服务器、机器人和通信
```

## 环境搭建

**1. 克隆本项目**
```bash
git clone https://github.com/QcrTiMo/Minecraft-AI.git
cd Minecraft-AI
```

**2. 安装 Node.js 依赖**
确保你已安装 [Node.js](https://nodejs.org/) (推荐 v18 或更高版本)。然后在项目根目录运行：
```bash
npm install flying-squid@1.11.0 mineflayer@4.33.0 prismarine-viewer@1.33.0 vec3@0.1.10 ws@8.18.3 canvas@3.2.0 js-yaml@4.1.0
```

**3. 创建并激活 Python 虚拟环境**
```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境 (Windows)
.venv\Scripts\activate

# 激活虚拟环境 (macOS / Linux)
source .venv/bin/activate
```

**4. 安装 Python 依赖**
确保虚拟环境已激活，然后运行：
```bash
pip install -r requirements.txt
```

 **常见问题**
> 训练开始前先运行 `python check_gpu.py` 查看pytorch是否支持GPU加速,
> 若 `CUDA is available` 为 **False**,则在终端激活环境下输入

```bash
# Window
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu128

# Linux
pip3 install torch torchvision
```
以确保安装的torch支持GPU,此问题将在未来一键脚本中解决.


## 如何开始训练

训练过程分为两步：首先启动 Node.js 环境端，然后启动 Python 训练脚本。

**第一步：启动 Minecraft 环境**

打开一个终端，在项目根目录 `Minecraft-AI` 下运行：
```bash
node start.js
```

**第二步：启动 AI 训练**

打开**另一个**新的终端，确保**已激活 Python 虚拟环境**，然后运行具体的训练脚本：
```bash
python -m train.navigation.go_to_xyz
```
训练将立即开始，你会在终端看到 `stable-baselines3` 输出的训练日志.

**第三步：查看训练结果**

训练结束后：
*   训练好的模型将保存在 `models/` 文件夹中。
*   记录了学习过程的**曲线图**和 TensorBoard 日志将保存在 `logs/` 文件夹中。

## 下一步计划

*   **丰富观察空间:** 在 `env/mc_env.py` 中向 AI 提供关于周围方块的信息，让它能真正“看到”障碍物。
*   **设计新任务:** 在 `train/` 目录下创建新的任务，例如“砍树”(`get_wood`)，并为其在 `train/reward/` 中设计新的奖励函数。








