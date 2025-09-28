import os

from env.mc_env import MinecraftEnv
from train.callbacks.plotting_callback import PlottingCallback
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import CallbackList
from utils.model_manager import get_or_create_model
from utils.checkpoint import Checkpoint
from typing import Callable


TOTAL_TIMESTEPS = 200000     #100000约等于3小时,200000也可以,如果时间允许
MODEL_NAME = "model"
MODELS_DIR = "models"
LOGS_DIR = "logs"


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

    env = MinecraftEnv()
    vec_env = DummyVecEnv([lambda: env])

    model_path = os.path.join(MODELS_DIR, f"{MODEL_NAME}.zip")

    #创建PPO智能体
    agent, is_loaded = get_or_create_model(
        model_path=model_path,
        env=vec_env,
        tensorboard_log=os.path.join(LOGS_DIR, "tensorboard"),
        device='cpu',
        learning_rate=linear_schedule(0.0003)
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