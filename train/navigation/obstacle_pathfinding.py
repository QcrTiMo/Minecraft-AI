import os
from env.mc_env import MinecraftEnv
from stable_baselines3.common.vec_env import DummyVecEnv
from utils.model_manager import transfer_learn_model
from utils.config import load_config
from utils.checkpoint import create_callback_list
from typing import Callable

config = load_config()

training_config = load_config()['training']
ppo_params = training_config.get('ppo_params', {})
TOTAL_TIMESTEPS = training_config['total_timesteps']
MODEL_NAME = training_config['model_name']
OLD_MODEL_PATH = training_config['old_model_path']
MODELS_DIR = training_config['models_dir']
MODELS_HISTORY_DIR = training_config['models_history_dir']
LOGS_DIR = training_config['logs_dir']

def linear_schedule(initial_value: float) -> Callable[[float], float]:
    def func(progress_remaining: float) -> float:
        return progress_remaining * initial_value
    return func

if __name__ == "__main__":
    os.makedirs(MODELS_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    vec_env = DummyVecEnv([lambda: MinecraftEnv(config=config)])
    eval_env = DummyVecEnv([lambda: MinecraftEnv(config=config)])
    
    model_path = os.path.join(MODELS_DIR, f"{MODEL_NAME}.zip")
    
    agent = transfer_learn_model(
        old_model_path=OLD_MODEL_PATH,
        env=vec_env,
        tensorboard_log=os.path.join(LOGS_DIR, "tensorboard"),
        device=training_config['device'],
        learning_rate=linear_schedule(training_config['learning_rate']),
        **ppo_params
    )

    callback_list = create_callback_list(
        config=config,
        eval_env=eval_env,
        model_name=MODEL_NAME,
        models_dir=MODELS_DIR,
        models_history_dir = MODELS_HISTORY_DIR,
        logs_dir=LOGS_DIR
    )

    try:
        agent.learn(
        total_timesteps=TOTAL_TIMESTEPS,
        callback=callback_list,
        reset_num_timesteps=False,   #你也可以选择True:重置训练步数
        tb_log_name=MODEL_NAME
    )
    except Exception as e:
        print(f"训练过程中发生错误: {e}")
    finally:
        vec_env.close()
        eval_env.close()

    print("\n----------- 训练结束 -----------")
    best_model_path = os.path.join(MODELS_DIR, 'best_model', 'best_model.zip')
    if os.path.exists(best_model_path):
        print(f"训练过程中最好的模型已自动保存到: {best_model_path}")
    else:
        print("警告: 未找到最佳模型。请检查评估回调的设置和日志。")

    print(f"定期的备份模型保存在: {MODELS_HISTORY_DIR} 目录下")
    print("所有流程执行完毕！")