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
STAND_PENALTY = reward_config['stand_penalty']
efficiency_base = reward_config['efficiency_base']
efficiency_step = reward_config['efficiency_step']
bump_penaltys = reward_config['bump_penalty']

def calculate_reward(info: dict, previous_info: dict, terminated: bool, truncated: bool) -> float:
    """
    计算“移动到指定坐标”任务的奖励
    """
    #如果任务因失败而截断，直接返回惩罚
    if truncated:
        print("任务超时，给予巨大负惩罚。")
        return TRUNCATED_PENALTY

    final = 0.0
    
    # 2. 如果任务成功，计算最终的巨额奖励
    if terminated:
        print("目标达成，给予巨大正奖励！")
        # 效率奖金：步数越少，奖励越高
        efficiency = efficiency_base - (info['steps'] * efficiency_step)
        final = REACH_TARGET_REWARD + efficiency

    # 3. 计算当前这一步的过程奖励 (无论是否是最后一步，都会计算)
    # 距离变化奖励
    distance_now = info['distance_to_target']
    distance_before = previous_info['distance_to_target']
    progress_reward = (distance_before - distance_now) * DISTANCE_REWARD

    #朝向奖励
    angle_diff = info['angle_diff_to_target']
    heading_reward = ((math.cos(angle_diff) + 1) / 2) * HEAD_TO_REWARD

    #撞墙惩罚
    bump_penalty = 0.0
    if info.get('action') in [0, 1, 2] and abs(distance_now - distance_before) < 0.05:
        # 如果执行了移动，但位置几乎没变，说明撞墙了
        bump_penalty = bump_penaltys

    #停滞惩罚
    stagnation_penalty = 0.0
    if abs(distance_now - distance_before) < 0.01 and angle_diff > 0.3:
        stagnation_penalty = STAND_PENALTY

    #生存惩罚
    alive_penalty = ALIVE_PENALTY

    #计算基础的过程总奖励
    total_process_reward = (progress_reward + heading_reward + stagnation_penalty + alive_penalty + bump_penalty)
    
    #累加最终奖励
    return total_process_reward + final

def is_terminated(info: dict) -> bool:
    """判断任务是否因成功而终止。"""
    return info['distance_to_target'] < TARGET_REACHED_THRESHOLD

def is_truncated(info: dict) -> bool:
    """判断任务是否因失败或超时而截断。"""
    env_config = load_config()['environment']
    return info['steps'] > env_config['max_steps']
