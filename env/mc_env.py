import gymnasium as gym
import numpy as np
import asyncio
import websockets
import json
import math
from gymnasium import spaces
from train.reward.go_to_xyz import calculate_reward, is_terminated, is_truncated

class MinecraftEnv(gym.Env):
    """
    一个与 Mineflayer 机器人通信的 Gymnasium 环境，用于强化学习。
    """
    metadata = {"render_modes": ["human"]}

    def __init__(self, config, websocket_uri="ws://localhost:3000"):
        super(MinecraftEnv, self).__init__()
        self.config = config
        self.websocket_uri = websocket_uri
        self.websocket = None
        
        try:
            self.loop = asyncio.get_running_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

        #动作空间：5个离散动作 (前进, 左移, 右移, 左转, 右转)
        self.action_space = spaces.Discrete(5)
        self.action_map = {
            0: ("move", {"direction": "forward", "duration": 250}),
            1: ("move", {"direction": "left", "duration": 250}),
            2: ("move", {"direction": "right", "duration": 250}),
            3: ("turn", {"angle_change": -math.radians(15)}),
            4: ("turn", {"angle_change": math.radians(15)}),
        }

        #观测空间：[相对位置(x,y,z), 距离, cos(自身朝向), sin(自身朝向), cos(目标朝向), sin(目标朝向)]
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(8,), dtype=np.float32)

        #环境状态变量
        self.current_state = None
        self.target_position = None
        self.info = {}
        self.previous_info = {}
        self.steps = 0
        self.episode_reward = 0.0

    async def _connect(self):
        """确保 WebSocket 连接是活跃的。"""
        if self.websocket is None or self.websocket.close:
            try:
                self.websocket = await websockets.connect(self.websocket_uri)
                print("环境已成功连接到 Mineflayer 服务器。")
            except ConnectionRefusedError:
                print("错误：连接被拒绝。请确保 Mineflayer 服务器正在运行。")
                raise

    async def _send_action(self, action_name, args={}):
        """向服务器发送一个动作指令。"""
        if args is None:
            args = {}
        message = json.dumps({"type": "action", "action": {"name": action_name, "args": args}})
        await self.websocket.send(message)

    async def _get_next_state(self):
        """从服务器接收下一个状态。"""
        try:
            message = await asyncio.wait_for(self.websocket.recv(), timeout=10.0)
            return json.loads(message)
        except asyncio.TimeoutError:
            print("警告: 10秒内未收到服务器状态，可能已卡死。")
            return None
        except websockets.exceptions.ConnectionClosed:
            print("警告：WebSocket 连接已关闭。")
            self.websocket = None
            return None

    def _state_to_observation(self, state):
        """将原始状态字典转换为NumPy观测数组。"""
        bot_pos = state['basic']['position']
        bot_yaw = state['basic']['yaw']
        
        rel_pos = np.array([
            self.target_position['x'] - bot_pos['x'],
            self.target_position['y'] - bot_pos['y'],
            self.target_position['z'] - bot_pos['z'],
        ])
        
        distance = np.linalg.norm(rel_pos)
        yaw_to_target = math.atan2(-rel_pos[0], -rel_pos[2])
        
        observation = np.array([
            rel_pos[0], rel_pos[1], rel_pos[2],
            distance,
            math.cos(bot_yaw), math.sin(bot_yaw),
            math.cos(yaw_to_target), math.sin(yaw_to_target)
        ], dtype=np.float32)
        
        angle_diff = bot_yaw - yaw_to_target
        angle_diff = (angle_diff + np.pi) % (2 * np.pi) - np.pi
        return observation, angle_diff

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.loop.run_until_complete(self._connect())
        
        print("\n--- 新回合开始 ---")
        print("正在重置机器人位置...")
        self.loop.run_until_complete(self._send_action("tp"))
        self.loop.run_until_complete(self._send_action("look", {"yaw": 0, "pitch": 0}))
        
        initial_state = self.loop.run_until_complete(self._get_next_state())

        if initial_state is None:
            raise RuntimeError("在 reset() 期间未能从服务器获取初始状态。请检查服务器状态。")

        #随机化目标点
        origin_point = {'x': 0, 'y': -60, 'z': 0}
        offset_range = self.config['environment']['reset_offset']
        offset_x = self.np_random.uniform(offset_range[0], offset_range[1])
        offset_z = self.np_random.uniform(offset_range[0], offset_range[1])
        self.target_position = {
            'x': origin_point['x'] + offset_x,
            'y': origin_point['y'],
            'z': origin_point['z'] + offset_z
        }
        print(f"新目标已设定: ({self.target_position['x']:.1f}, {self.target_position['z']:.1f})")

        #重置内部状态
        self.steps = 0
        self.episode_reward = 0.0
        self.current_state = initial_state
        observation, angle_diff = self._state_to_observation(initial_state)

        self.info = {
            "distance_to_target": observation[3],
            "steps": self.steps,
            "angle_diff_to_target": abs(angle_diff)
        }
        self.previous_info = self.info.copy()
        
        return observation, self.info

    def step(self, action):
        action_name, args = self.action_map.get(action)
        self.loop.run_until_complete(self._send_action(action_name, args))
        self.current_state = self.loop.run_until_complete(self._get_next_state())

        if self.current_state is None:
            print("通信超时或连接断开，将提前终止此回合。")
            dummy_observation = np.zeros(self.observation_space.shape, dtype=np.float32)
            timeout_penalty = -100.0
            return dummy_observation, timeout_penalty, False, True, {"error": "communication_timeout"}

        self.steps += 1
        observation, angle_diff = self._state_to_observation(self.current_state)
        
        self.previous_info = self.info.copy()
        self.info = {
            "distance_to_target": observation[3],
            "steps": self.steps,
            "angle_diff_to_target": abs(angle_diff)
        }
        
        terminated = is_terminated(self.info)
        truncated = is_truncated(self.info)
        reward = calculate_reward(self.info, self.previous_info, terminated, truncated)
        
        self.episode_reward += reward

        if terminated:
            print(f"--- ✔ 任务成功! --- 步数: {self.info['steps']}, 距离: {self.info['distance_to_target']:.2f}, 总奖励: {self.episode_reward:.2f}")
        if truncated and not terminated:
            print(f"--- ✖ 超时失败! --- 步数: {self.info['steps']}, 距离: {self.info['distance_to_target']:.2f}, 总奖励: {self.episode_reward:.2f}")
        
        if terminated or truncated:
            self.info['episode'] = {
                'r': self.episode_reward,
                'l': self.steps
            }
        
        return observation, reward, terminated, truncated, self.info

    def close(self):
        """关闭环境，清理资源。"""
        if self.websocket and not self.websocket.close:
            try:
                self.loop.run_until_complete(self.websocket.close())
                print("WebSocket 连接已成功关闭。")
            except Exception as e:
                print(f"尝试关闭 WebSocket 时发生错误: {e}")
        self.websocket = None