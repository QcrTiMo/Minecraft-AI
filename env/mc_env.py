import gymnasium as gym
import numpy as np
import asyncio
import websockets
import json
import math
import threading
import queue
import logging
from gymnasium import spaces

from train.reward.go_to_xyz import calculate_reward, is_terminated, is_truncated

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(threadName)s (%(thread)d) - %(message)s')

class MinecraftEnv(gym.Env):
    metadata = {"render_modes": ["human"]}

    def __init__(self, websocket_uri="ws://localhost:3000"):
        super(MinecraftEnv, self).__init__()
        logging.info("MinecraftEnv __init__ 开始。")
        self.websocket_uri = websocket_uri
        
        #动作空间和观察空间
        self.action_space = spaces.Discrete(7)
        self.action_map = {
            0: ("move", {"direction": "forward", "duration": 250}),
            1: ("move", {"direction": "back", "duration": 250}),
            2: ("move", {"direction": "left", "duration": 250}),
            3: ("move", {"direction": "right", "duration": 250}),
            4: ("jump", {}),
            5: ("turn", {"angle_change": -math.radians(15)}),
            6: ("turn", {"angle_change": math.radians(15)}),
        }
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(8,), dtype=np.float32)
        self.action_queue = queue.Queue(maxsize=1)
        self.state_queue = queue.Queue(maxsize=1)

        #状态变量
        self.target_position = None
        self.info = {}
        self.previous_info = {}
        self.steps = 0
        self.is_closed = False

        #new
        self.last_observation = np.zeros(self.observation_space.shape, dtype=np.float32)

        #启动后台通信线程
        self.comm_thread = threading.Thread(target=self._communication_loop, daemon=True)
        self.comm_thread.start()

    def _communication_loop(self):
        """
        这个函数在独立的线程中运行，处理所有异步网络通信。
        """
        async def main_logic():
            try:
                async with websockets.connect(self.websocket_uri) as websocket:
                    print("环境已成功连接到 Mineflayer 服务器。")
                    
                    #启动两个并行的任务,一个用于发送,一个用于接收
                    recv_task = asyncio.create_task(self._receiver(websocket))
                    send_task = asyncio.create_task(self._sender(websocket))
                    
                    #等待任一任务结束
                    done, pending = await asyncio.wait(
                        [recv_task, send_task],
                        return_when=asyncio.FIRST_COMPLETED,
                    )
                    for task in pending:
                        task.cancel()
            except Exception as e:
                print(f"通信线程发生错误: {e}")
            finally:
                print("通信线程已关闭。")
                self.is_closed = True

        asyncio.run(main_logic())

    async def _receiver(self, websocket):
        while not self.is_closed:
            try:
                logging.info("正在等待来自服务器的消息...")
                message = await websocket.recv()
                logging.info(f"成功收到消息: {message[:100]}...")
                state = json.loads(message)
                
                if self.state_queue.full():
                    logging.warning("状态队列已满，正在丢弃旧状态以接收新状态。")
                    self.state_queue.get_nowait()

                self.state_queue.put(state)
                logging.info("新状态已放入队列。")

            except websockets.exceptions.ConnectionClosed as e:
                logging.warning(f"WebSocket 连接已关闭 (代码: {e.code}, 原因: {e.reason})")
                break
            except Exception as e:
                logging.error(f"接收消息时出错: {e}", exc_info=True)
                break

    async def _sender(self, websocket):
        while not self.is_closed:
            try:
                action_name, params = self.action_queue.get(timeout=0.01)
                message = json.dumps({"type": "action", "action": {"name": action_name, "params": params}})
                await websocket.send(message)
                logging.info(f"已发送动作: {action_name}")
                self.action_queue.task_done()
            except queue.Empty:
                await asyncio.sleep(0.01)
            except Exception as e:
                logging.error(f"发送动作时出错: {e}", exc_info=True)
                break

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
        logging.info(">>> 进入 reset() 方法。")
        logging.info("现在，正式开始等待初始状态...")
        try:
            initial_state = self.state_queue.get(timeout=15)
            logging.info("<<< 成功从队列中获取初始状态！reset() 即将完成。")
        except queue.Empty:
            logging.error("<<< 在15秒内未收到初始状态，reset() 失败。")
            raise RuntimeError("在15秒内未收到来自服务器的初始状态，请检查JS服务器是否在连接建立后立即发送状态。")

        bot_pos = initial_state['basic']['position']
        offset = np.random.uniform(-15, 15, size=2)
        self.target_position = {'x': bot_pos['x'] + offset[0], 'y': bot_pos['y'], 'z': bot_pos['z'] + offset[1]}
        print(f"新回合开始! 目标: ({self.target_position['x']:.1f}, {self.target_position['z']:.1f})")

        observation = self._state_to_observation(initial_state)
        self.last_observation = observation
        self.info = {"distance_to_target": observation[3], "steps": 0}
        return observation, self.info

    def step(self, action):
        if self.is_closed:
            return self.last_observation, 0, True, False, self.info
            
        self.action_queue.put(self.action_map.get(action))
        
        try:
            current_state = self.state_queue.get(timeout=5)
            observation = self._state_to_observation(current_state)
            self.last_observation = observation
            
            self.info["distance_to_target"] = observation[3]
            self.info["steps"] += 1

            terminated = is_terminated(self.info)
            truncated = is_truncated(self.info)
            reward = calculate_reward(self.info, self.info, terminated, truncated)
            
            return observation, reward, terminated, truncated, self.info
        except queue.Empty:
            logging.warning("在5秒内未收到服务器状态更新，假设回合截断。")
            return self.last_observation, 0, False, True, self.info

    def close(self):
        if not self.is_closed:
            print("正在关闭环境...")
            self.is_closed = True
            #发送一个关闭信号给JS端
            if self.comm_thread.is_alive():
                self.comm_thread.join(timeout=2)
            print("环境已关闭。")