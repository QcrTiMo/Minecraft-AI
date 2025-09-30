import numpy as np
import math
from utils.config import load_config

reward_config = load_config()['reward']
env_config = load_config()['environment']

TARGET_REACHED_THRESHOLD = reward_config['target_reached_threshold']
REACH_TARGET_REWARD = reward_config['reach_target_reward']
TRUNCATED_PENALTY = reward_config['truncated_penalty']
ALIVE_PENALTY = reward_config['alive_penalty']
DISTANCE_REWARD = reward_config['distance_reward']
HEAD_TO_REWARD = reward_config['head_to_reward']
STAND_PENALTY = reward_config.get('stand_penalty', -0.1)

def calculate_reward(info: dict, previous_info: dict, terminated: bool, truncated: bool) -> float:
    """
    计算“移动到指定坐标”任务的奖励
    """
    if terminated:
        print("目标达成，给予巨大正奖励！")
        return REACH_TARGET_REWARD
    if truncated:
        print("任务超时，给予巨大负惩罚。")
        return TRUNCATED_PENALTY

    #距离变化奖励
    #这个奖励直接告诉AI“靠近目标是好的”
    distance_now = info['distance_to_target']
    distance_before = previous_info['distance_to_target']
    progress_reward = (distance_before - distance_now) * DISTANCE_REWARD

    #朝向奖励
    #使用余弦函数，朝向目标时奖励为正，背向为负
    angle_diff = info['angle_diff_to_target']
    #将奖励范围从[-1, 1]调整到[0, 1]，仅在朝向正确时给予奖励，避免惩罚过重
    heading_reward = ((math.cos(angle_diff) + 1) / 2) * HEAD_TO_REWARD

    stagnation_penalty = 0.0
    if abs(distance_now - distance_before) < 0.01 and angle_diff > 0.3:
        stagnation_penalty = STAND_PENALTY

    alive_penalty = ALIVE_PENALTY
    total_reward = (progress_reward + heading_reward + stagnation_penalty + alive_penalty)
    
    return total_reward

def is_terminated(info: dict) -> bool:
    """判断任务是否因成功而终止。"""
    return info['distance_to_target'] < TARGET_REACHED_THRESHOLD

def is_truncated(info: dict) -> bool:
    """判断任务是否因失败或超时而截断。"""
    env_config = load_config()['environment']
    return info['steps'] > env_config['max_steps']
