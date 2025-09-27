import os
from stable_baselines3 import PPO

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