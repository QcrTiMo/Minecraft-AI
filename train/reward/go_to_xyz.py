import numpy as np
import math
from utils.config import load_config

reward_config = load_config()['reward']

TARGET_REACHED_THRESHOLD = reward_config['target_reached_threshold']
REACH_TARGET_REWARD = reward_config['reach_target_reward']
TRUNCATED_PENALTY = reward_config['truncated_penalty']
ALIVE_PENALTY = reward_config['alive_penalty']
W_DISTANCE = reward_config['w_distance']
W_ANGLE = reward_config['w_angle']

def calculate_reward(info: dict, previous_info: dict, terminated: bool, truncated: bool) -> float:
    """
    计算“移动到指定坐标”任务的奖励（修改版）。
    """
    if terminated:
        return REACH_TARGET_REWARD
    if truncated:
        return TRUNCATED_PENALTY
    distance_reward = previous_info['distance_to_target'] - info['distance_to_target']
    angle_diff = info['angle_diff_to_target']
    angle_reward = math.cos(angle_diff)
    reward = (distance_reward * W_DISTANCE) + (angle_reward * W_ANGLE) + ALIVE_PENALTY
    return reward

def is_terminated(info: dict) -> bool:
    """判断任务是否因成功而终止。"""
    return info['distance_to_target'] < TARGET_REACHED_THRESHOLD

def is_truncated(info: dict) -> bool:
    """判断任务是否因失败或超时而截断。"""
    env_config = load_config()['environment']
    return info['steps'] > env_config['max_steps']
