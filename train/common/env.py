import gymnasium as gym
import numpy as np
import asyncio
import websockets
import json
import math
from gymnasium import spaces

from train.common.reward.go_to_xyz import calculate_reward, is_terminated, is_truncated

class MinecraftEnv(gym.Env):
    """
    一个符合Gymnasium API的自定义Minecraft环境封装器.
    """
    metadata = {"render_modes": ["human"]}


    def __init__(self, websocket_uri="ws://localhost:3000"):
        super(MinecraftEnv, self).__init__()
        self.websocket_uri = websocket_uri
        self.websocket = None
        try:
            self.loop = asyncio.get_running_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

        #定义动作空间
        self.action_space = spaces.Discrete(7)
        self.action_map = {
            0: ("move", {"direction": "forward", "duration": 250}),
            1: ("move", {"direction": "back", "duration": 250}),
            2: ("move", {"direction": "left", "duration": 250}),
            3: ("move", {"direction": "right", "duration": 250}),
            4: ("jump", {}),
            5: ("turn", {"angle_change": math.radians(15)}),
            6: ("turn", {"angle_change": math.radians(15)}),
        }

        #定义观察空间
        #[相对X, 相对Y, 相对Z, 相对距离, cos(机器人朝向), sin(机器人朝向), cos(目标朝向), sin(目标朝向)]
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(8,), dtype=np.float32)

        #内部状态
        self.current_state = None
        self.target_position = None
        self.info = {}
        self.previous_info = {}
        self.steps = 0

    async def _connect(self):
        """建立WebSocket链接"""
        if self.websocket is None or not self.websocket.open:
            self.websocket = await websockets.connect(self.websocket_uri)
            print("环境已经成功连接到Mineflayer服务器")

    async def _send_action(self, action_name, params):
        """向JS环境发送动作指令"""
        message = json.dumps({"type": "action", "action": {"name": action_name, "params": params}})
        await self.websocket.send(message)

    async def _get_next_state(self):
        """等待并接受下一个状态"""
        message = await self.websocket.recv()
        return json.loads(message)
    
    def _state_to_observation(self, state):
        """将原始状态JSON转换为AI能理解的NumPy向量"""
        bot_pos = state['basic']['position']
        bot_yaw = state['basic']['yaw']

        #计算到目标的相对向量
        rel_pos = np.array([
            self.target_position['x'] - bot_pos['x'],
            self.target_position['y'] - bot_pos['y'],
            self.target_position['z'] - bot_pos['z'],
        ])

        distance = np.linalg.norm(rel_pos)

        #计算到目标所需要的朝向角
        yaw_to_target = math.atan2(-rel_pos[0], -rel_pos[2])

        return np.array([
            rel_pos[0], rel_pos[1], rel_pos[2],
            distance,
            math.cos(bot_yaw), math.sin(bot_yaw),
            math.cos(yaw_to_target), math.sin(yaw_to_target)
        ], dtype=np.float32)
    
    def reset(self, seed=None, options=None):
        """重置环境到一个新的回合。"""
        super().reset(seed=seed)

        self.loop.run_until_complete(self._connect())

        #为这个回合设定一个新的随机目标
        #这里需要与JS通信来获取初始位置
        #通过发送一个“空”动作来获取机器人的初始位置
        self.loop.run_until_complete(self._send_action("look", {"yaw": 0, "pitch": 0})) 
        initial_state = self.loop.run_until_complete(self._get_next_state())
        bot_pos = initial_state['basic']['position']
        
        #设置新目标
        offset = np.random.uniform(-15, 15, size=2)
        self.target_position = {
            'x': bot_pos['x'] + offset[0],
            'y': bot_pos['y'], #保持Y轴不变，简化为平面寻路
            'z': bot_pos['z'] + offset[2]
        }
        print(f"新目标: ({self.target_position['x']:.1f}, {self.target_position['z']:.1f})")

        self.steps = 0
        self.current_state = initial_state
        observation = self._state_to_observation(initial_state)

        #更新info
        self.info = {
            "到目标距离": observation[3],
            "步数": self.steps
        }
        self.previous_info = self.info.copy()

        return observation, self.info
    
    def step(self, action):
        """执行一步工作"""
        #发送动作
        action_name, params = self.action_map.get(action, ("move", {})) #默认不移动
        self.loop.run_until_complete(self._send_action(action_name, params))
        
        #获取新状态
        self.current_state = self.loop.run_until_complete(self._get_next_state())
        self.steps += 1
        
        #计算新观察值和info
        observation = self._state_to_observation(self.current_state)
        self.previous_info = self.info.copy()
        self.info = {
            "distance_to_target": observation[3],
            "steps": self.steps
        }
        
        #判断任务是否结束
        terminated = is_terminated(self.info)
        truncated = is_truncated(self.info)
        
        #计算奖励
        reward = calculate_reward(self.info, self.previous_info, terminated, truncated)
        
        return observation, reward, terminated, truncated, self.info

    def close(self):
        """关闭环境，清理资源。"""
        self.loop.run_until_complete(self.websocket.close())
        print("环境连接已关闭。")
