import os

from env.mc_env import MinecraftEnv
from train.callbacks.plotting_callback import PlottingCallback
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import CallbackList
from utils.model_manager import get_or_create_model
from utils.checkpoint import Checkpoint
from utils.config import load_config
from typing import Callable

config = load_config()
training_config = config['training']
ppo_params = training_config.get('ppo_params', {})

TOTAL_TIMESTEPS = training_config['total_timesteps']
MODEL_NAME = training_config['model_name']
MODELS_DIR = training_config['models_dir']
LOGS_DIR = training_config['logs_dir']


def linear_schedule(initial_value: float) -> Callable[[float], float]:
    """
    创建一个线性衰减的学习率schedule。
    """
    def func(progress_remaining: float) -> float:
        return progress_remaining * initial_value
    return func


if __name__ == "__main__":
    #准备文件夹和环境
    os.makedirs(MODELS_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)

    vec_env = DummyVecEnv([lambda: MinecraftEnv(config=config)])

    model_path = os.path.join(MODELS_DIR, f"{MODEL_NAME}.zip")

    #创建PPO智能体
    agent, is_loaded = get_or_create_model(
        model_path=model_path,
        env=vec_env,
        tensorboard_log=os.path.join(LOGS_DIR, "tensorboard"),
        device=training_config['device'],
        learning_rate=linear_schedule(training_config['learning_rate']),
        **ppo_params
    )

    #创建绘图
    plotting_callback = PlottingCallback(logs_dir=LOGS_DIR, model_name=MODEL_NAME)
    checkpoint_callback = Checkpoint(save_path=MODELS_DIR, model_name=MODEL_NAME)
    callback_list = CallbackList([plotting_callback, checkpoint_callback])


    #开始训练
    try:
        agent.learn(
            total_timesteps=TOTAL_TIMESTEPS,
            callback=callback_list,
            reset_num_timesteps=not is_loaded,
            tb_log_name=MODEL_NAME
        )
    except Exception as e:
        print(f"训练过程中发生错误: {e}")
    finally:
        vec_env.close()

    #保存模型和图表
    plotting_callback.plot_and_save()
    checkpoint_callback.cleanup_and_save_best()

    print("\n所有流程执行完毕！")