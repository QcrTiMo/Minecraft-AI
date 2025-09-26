import numpy as np

TARGET_REACHED_THRESHOLD = 1.0
REACH_TARGET_REWARD = 100        #到达目标给100
ALIVE_PENALTY = -0.1

def calculate_reward(info: dict, previous_info: dict, terminated: bool, truncated: bool) -> float:
    """
    计算“移动到指定坐标”任务的奖励。
    """
    #如果是到达终点结束
    if terminated:
        return REACH_TARGET_REWARD
    #如果是因为其他原因结束
    if truncated:
        return -10
    
    #靠近目标,值为正；远离目标，值为负
    distance_reward = previous_info['distance_to_target'] - info['distance_to_target']

    #组合奖励
    #distance_reward鼓励AI朝着正确的方向前进
    #ALIVE_PENALTY鼓励AI尽快完成任务
    reward = distance_reward * 10 + ALIVE_PENALTY
    return reward

def is_terminated(info: dict) -> bool:
    """
    判断任务是否因成功而终止。
    """
    return info['distance_to_target'] < TARGET_REACHED_THRESHOLD

def is_truncated(info: dict) -> bool:
    """
    判断任务是否因失败或超时而截断。
    """
    #如果任务超过500步还没完成，就判为超时
    return info['steps'] > 500
