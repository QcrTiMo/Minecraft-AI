import gymnasium as gym
import numpy as np
import asyncio
import websockets
import json
import math
from gymnasium import spaces

from train.reward.go_to_xyz import calculate_reward, is_terminated, is_truncated

class MinecraftEnv(gym.Env):
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

        #动作空间
        self.action_space = spaces.Discrete(6)
        self.action_map = {
            0: ("move", {"direction": "forward", "duration": 250}),
            1: ("move", {"direction": "back", "duration": 250}),
            2: ("move", {"direction": "left", "duration": 250}),
            3: ("move", {"direction": "right", "duration": 250}),
            4: ("turn", {"angle_change": -math.radians(15)}),
            5: ("turn", {"angle_change": math.radians(15)}),
            #6: ("jump",)
        }

        #观察空间
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(8,), dtype=np.float32)

        #状态变量
        self.current_state = None
        self.target_position = None
        self.info = {}
        self.previous_info = {}
        self.steps = 0

    async def _connect(self):
        if self.websocket is None or self.websocket.close:
            self.websocket = await websockets.connect(self.websocket_uri)
            print("环境已成功连接到 Mineflayer 服务器。")

    async def _send_action(self, action_name, params):
        message = json.dumps({"type": "action", "action": {"name": action_name, "params": params}})
        await self.websocket.send(message)

    async def _get_next_state(self):
        #增加超时以防止无限等待
        try:
            message = await asyncio.wait_for(self.websocket.recv(), timeout=10.0)
            return json.loads(message)
        except asyncio.TimeoutError:
            print("警告: 10秒内未收到服务器状态，可能已卡死。返回None。")
            return None

    def _state_to_observation(self, state):
        bot_pos = state['basic']['position']
        bot_yaw = state['basic']['yaw']
        
        rel_pos = np.array([
            self.target_position['x'] - bot_pos['x'],
            self.target_position['y'] - bot_pos['y'],
            self.target_position['z'] - bot_pos['z'],
        ])
        
        distance = np.linalg.norm(rel_pos)
        yaw_to_target = math.atan2(-rel_pos[0], -rel_pos[2])
        
        return np.array([
            rel_pos[0], rel_pos[1], rel_pos[2],
            distance,
            math.cos(bot_yaw), math.sin(bot_yaw),
            math.cos(yaw_to_target), math.sin(yaw_to_target)
        ], dtype=np.float32)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.loop.run_until_complete(self._connect())
        print("新回合...")
        self.loop.run_until_complete(self._send_action("look", {"yaw": 0, "pitch": 0}))
        initial_state = self.loop.run_until_complete(self._get_next_state())

        if initial_state is None:
            raise RuntimeError("在 reset() 期间未能从服务器获取初始状态。")

        bot_pos = initial_state['basic']['position']
        
        #减小初始难度
        offset = np.random.uniform(-20, 20, size=2)
        self.target_position = {
            'x': bot_pos['x'] + offset[0], 'y': bot_pos['y'], 'z': bot_pos['z'] + offset[1]
        }
        print(f"新回合开始! 目标: ({self.target_position['x']:.1f}, {self.target_position['z']:.1f})")

        self.steps = 0
        self.current_state = initial_state
        observation = self._state_to_observation(initial_state)

        self.info = {"distance_to_target": observation[3], "steps": self.steps}
        self.previous_info = self.info.copy()
        
        return observation, self.info

    def step(self, action):
        #发送动作并获取新状态
        action_name, params = self.action_map.get(action)
        self.loop.run_until_complete(self._send_action(action_name, params))
        
        self.current_state = self.loop.run_until_complete(self._get_next_state())

        if self.current_state is None:
            print("通信超时，强制重置环境。")
            observation, self.info = self.reset()
            return observation, -10, False, True, self.info

        #更新状态和信息
        self.steps += 1
        observation = self._state_to_observation(self.current_state)
        self.previous_info = self.info.copy()
        self.info = {"distance_to_target": observation[3], "steps": self.steps}
        
        #判断回合是否结束
        terminated = is_terminated(self.info)
        truncated = is_truncated(self.info)
        
        #计算奖励
        reward = calculate_reward(self.info, self.previous_info, terminated, truncated)
        if truncated:
            print(f"回合因步数超过上限 ({self.info['steps']} 步) 而被截断。正在强制重置...")
            observation, self.info = self.reset()
        
        #返回结果
        return observation, reward, terminated, truncated, self.info

    def close(self):
        if self.websocket and not self.websocket.close:
            try:
                self.loop.run_until_complete(self.websocket.close())
                print("WebSocket 连接已关闭。")
            except Exception as e:
                print(f"尝试关闭 WebSocket 时发生错误: {e}")
        self.websocket = None