import os

from train.common.env import MinecraftEnv
from agent.ppo_agent import PPOAgent
from train.common.plotting_callback import PlottingCallback


TOTAL_TIMESTEPS = 25000
MODEL_NAME = "ppo_go_to_xyz_v1"
MODELS_DIR = "models"
LOGS_DIR = "logs"


if __name__ == "__main__":
    #准备文件夹和环境
    os.makedirs(MODELS_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)
    env = MinecraftEnv()

    #创建PPO智能体
    agent = PPOAgent(
        env=env,
        model_name=MODEL_NAME,
        models_dir=MODELS_DIR,
        logs_dir=LOGS_DIR
    )

    #创建绘图
    plotting_callback = PlottingCallback(check_freq=1024, logs_dir=LOGS_DIR, model_name=MODEL_NAME)

    #开始训练
    try:
        agent.learn(total_timesteps=TOTAL_TIMESTEPS, callback=plotting_callback)
    except Exception as e:
        print(f"训练过程中发生错误: {e}")
    finally:
        env.close()

    #保存模型和图表
    agent.save()
    plotting_callback.plot_and_save()

    print("\n所有流程执行完毕！")