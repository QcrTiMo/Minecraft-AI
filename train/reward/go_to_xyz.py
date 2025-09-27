import numpy as np
import math

TARGET_REACHED_THRESHOLD = 1.0
REACH_TARGET_REWARD = 100        #到达目标给100
ALIVE_PENALTY = -0.1
TRUNCATED_PENALTY = -10

W_DISTANCE = 10.0  #距离奖励的权重
W_ANGLE = 2.0      #朝向奖励的权重

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
    reward = (distance_reward * W_DISTANCE) + (angle_reward * W_ANGLE) + ALIVE_PENALTY
    
    return reward

def is_terminated(info: dict) -> bool:
    """判断任务是否因成功而终止。"""
    return info['distance_to_target'] < TARGET_REACHED_THRESHOLD

def is_truncated(info: dict) -> bool:
    """判断任务是否因失败或超时而截断。"""
    return info['steps'] > 3000
