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
PROXIMITY_THRESHOLD = reward_config['PROXIMITY_THRESHOLD']
W_PROXIMITY_PENALTY = reward_config['W_PROXIMITY_PENALTY']

def calculate_reward(info: dict, previous_info: dict, terminated: bool, truncated: bool) -> float:
    """
    计算“移动到指定坐标”任务的奖励。
    """
    #如果是因成功而终止
    if terminated:
        return REACH_TARGET_REWARD
    #如果是因超时而截断
    if truncated:
        return TRUNCATED_PENALTY
    
    distance_reward = previous_info['distance_to_target'] - info['distance_to_target']
    angle_diff = info['angle_diff_to_target']
    angle_reward = math.cos(angle_diff)

    proximity_penalty = 0.0
    if info['distance_to_target'] < PROXIMITY_THRESHOLD:
        #惩罚值与离目标的距离成反比：越近，惩罚越大
        #这会迫使AI尽快完成最后一步，而不是在附近徘徊
        proximity_penalty = - (1.0 / max(info['distance_to_target'], 0.1)) * W_PROXIMITY_PENALTY

    reward = (distance_reward * W_DISTANCE) + (angle_reward * W_ANGLE) + ALIVE_PENALTY + proximity_penalty
    return reward

def is_terminated(info: dict) -> bool:
    """判断任务是否因成功而终止。"""
    return info['distance_to_target'] < TARGET_REACHED_THRESHOLD

def is_truncated(info: dict) -> bool:
    """判断任务是否因失败或超时而截断。"""
    env_config = load_config()['environment']
    return info['steps'] > env_config['max_steps']
