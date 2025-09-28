# Minecraft-AI: 基于 Mineflayer 和 PyTorch 的 Minecraft AI 训练框架

这是一个用于在《我的世界》(Minecraft) 中训练智能 AI 的强化学习框架。本项目利用 Node.js 端的 [**Mineflayer**](https://github.com/PrismarineJS/mineflayer) 库与游戏进行底层交互，并通过 WebSocket 将其封装成一个标准的、可供 Python 端调用的 **Gymnasium** 环境。AI 的训练基于 **PyTorch** 和 **Stable Baselines3** 库。

整个框架的核心特性是**自动化**和**模块化**：
*   **代码内嵌服务器:** 无需手动开启 Minecraft 客户端或服务器，代码会自动创建一个内存服务器。
*   **程序化世界生成:** 可以为不同的训练任务动态生成指定的世界（如平地、障碍场）。
*   **浏览器实时可视化:** 可以在浏览器中实时观察 AI 的第一人称视角。
*   **清晰的模块分离:** 环境、智能体、训练任务、奖励函数等模块高度解耦，易于扩展。

## 核心技术

*   **环境端 (JavaScript):**
    *   [Node.js](https://nodejs.org/) - 运行时环境
    *   [Mineflayer](https://github.com/PrismarineJS/mineflayer) - Minecraft 机器人（客户端）API
    *   [Flying Squid](https://github.com/PrismarineJS/flying-squid) - Minecraft 服务器实现
    *   [Prismarine Viewer](https://github.com/PrismarineJS/prismarine-viewer) - 浏览器可视化工具
    *   [ws](https://github.com/websockets/ws) - WebSocket 通信库
*   **智能体端 (Python):**
    *   [Python](https://www.python.org/)
    *   [PyTorch](https://pytorch.org/) - 深度学习框架
    *   [Stable Baselines3](https://github.com/DLR-RM/stable-baselines3) - 强化学习算法库
    *   [Gymnasium](https://gymnasium.farama.org/) - AI 训练环境 API 标准
    *   [websockets](https://websockets.readthedocs.io/en/stable/) - WebSocket 通信库
    *   [matplotlib](https://matplotlib.org/) - 训练曲线绘图库

## 项目结构

```
Minecraft-AI/
├── actions/              # (JS) AI 在游戏中的原子动作定义 (移动, 跳跃, 转向等)
├── agent/                # (PY) AI 智能体的定义
│   ├── model.py          #   - 定义神经网络的结构
│   └── ppo_agent.py      #   - PPO 算法的封装和管理器
├── env/                  # (PY) Gymnasium 环境的封装
│   └── mc_env.py         #   - 将 JS 环境包装成标准的 Gym 接口
├── logs/                 # (Output) 存放训练日志和学习曲线图
├── models/               # (Output) 存放训练好的模型文件 (.zip, .safetensors)
├── node_modules/         # (JS) Node.js 依赖
├── server/               # (JS) 存放所有服务器相关的模块
│   ├── mcServer.js       #   - 负责启动和管理 Minecraft 服务器
│   └── webSocketServer.js#   - 负责启动和管理 WebSocket 通信服务器
├── train/                # (PY) 训练任务的核心逻辑
│   ├── callbacks/        #   - 存放自定义的回调函数 (如绘图)
│   ├── navigation/       #   - 具体的训练任务脚本 (如寻路)
│   └── reward/           #   - 存放不同任务的奖励函数
├── training_background/  # (JS) 程序化生成训练世界的脚本
├── utils/                # (JS) 存放通用辅助工具函数
│   └── worldLoader.js    #   - 负责加载指定的 Minecraft 世界生成脚本
├── viewer/               # (JS) 存放可视化界面相关的模块
│   └── viewer.js         #   - 负责启动 Prismarine Viewer 网页可视化界面
├── .gitignore
├── bot.js                # (JS) 机器人主配置，负责创建和连接 Mineflayer 实例
├── config.js             # (JS) 存放项目的全局配置文件 (如端口号)
├── package.json
├── README.md             # 本文档
├── requirements.txt      # (PY) Python 依赖列表
└── start.js              # (JS) 项目的主入口：按顺序启动所有服务
```

## 环境搭建

**1. 克隆本项目 (如果需要)**
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
node start.js [world_name]
```
*   `[world_name]` 是一个可选参数，它对应 `training_background` 文件夹下的脚本文件名（无需 `.js` 后缀）。
*   如果**不提供** `world_name`，将默认加载 `flat_world`。

**可用世界示例：**
*   **基础寻路训练 (平坦世界):**
    ```bash
    node start.js
    ```
当终端显示 "可视化界面已启动..." 时，环境已准备就绪。你可以在浏览器中打开 **`http://localhost:3001`** 来实时观看 AI 的视角。

**第二步：启动 AI 训练**

打开**另一个**新的终端，确保**已激活 Python 虚拟环境**，然后运行具体的训练脚本：
```bash
python -m train.navigation.go_to_xyz
```
训练将立即开始，你会在终端看到 `stable-baselines3` 输出的训练日志，同时浏览器中的 AI 会开始自主行动。

**第三步：查看训练结果**

训练结束后：
*   训练好的模型将保存在 `models/` 文件夹中。
*   记录了学习过程的**奖励曲线图**和 TensorBoard 日志将保存在 `logs/` 文件夹中。

## 下一步计划

*   **丰富观察空间:** 在 `env/mc_env.py` 中向 AI 提供关于周围方块的信息，让它能真正“看到”障碍物。
*   **设计新任务:** 在 `train/` 目录下创建新的任务，例如“砍树”(`get_wood`)，并为其在 `train/reward/` 中设计新的奖励函数。
*   **课程学习:** 编写一个主脚本，让 AI 自动地先在简单环境 (`flat_world`) 中训练一定步数，然后自动加载模型，在更复杂的环境 (`hard_obstacles`) 中继续训练。







