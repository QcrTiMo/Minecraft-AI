import os
import torch as th
from stable_baselines3 import PPO

def transfer_learn_model(
    old_model_path: str,
    env,
    tensorboard_log: str,
    device: str,
    **ppo_params
):
    """
    执行迁移学习：加载一个旧模型，将其权重迁移到一个新模型中
    """
    print(f"----------- 开始迁移学习 -----------")
    print(f"加载预训练的旧模型自: {old_model_path}")

    # 1. 加载旧模型，获取其权重字典 (旧大脑)
    old_model = PPO.load(old_model_path, device=device)
    old_weights = old_model.policy.state_dict()

    print(f"创建一个适配新环境的全新模型...")
    # 2. 创建一个全新的、适配新环境的模型 (新身体)
    new_model = PPO(
        policy='MlpPolicy',
        env=env,
        tensorboard_log=tensorboard_log,
        device=device,
        **ppo_params
    )
    new_weights = new_model.policy.state_dict()

    print("开始执行权重迁移...")
    # 3. 逐层进行权重迁移 (手术过程)
    for key in new_weights:
        if key in old_weights and new_weights[key].shape == old_weights[key].shape:
            # 如果新旧模型都有这一层，并且形状完全一样 (通常是隐藏层)
            new_weights[key] = old_weights[key]
            print(f"  - 成功迁移层: {key}")
        else:
            # 对于形状不匹配的层 (通常是输入/输出层)，保留新模型的随机初始化权重
            print(f"  - [!] 跳过层 (形状不匹配): {key}")

    # 4. 将融合了旧知识的新权重加载到新模型中
    new_model.policy.load_state_dict(new_weights)

    print("----------- 迁移学习完成！-----------")
    return new_model

def get_or_create_model(model_path: str, env, policy: str = "MlpPolicy", **kwargs):
    """
    检查模型路径是否存在。
    - 如果存在，则加载模型并返回。
    - 如果不存在，则创建一个新的 PPO 模型并返回。
    
    返回:
        model: PPO 模型实例
        is_loaded: 一个布尔值，如果模型是从文件加载的，则为 True
    """
    if os.path.exists(model_path):
        print(f"----------- 从 {model_path} 加载现有模型进行二次训练 -----------")
        try:
            model = PPO.load(model_path, env=env, **kwargs)
            print("模型加载成功！")
            return model, True
        except Exception as e:
            print(f"加载模型失败: {e}。将创建一个新模型。")
            
    print(f"----------- 在 {model_path} 未找到模型，创建一个全新的 PPO 模型 -----------")
    model = PPO(policy, env, verbose=1, **kwargs)
    print("新模型创建成功！")
    return model, False