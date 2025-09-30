import os
from stable_baselines3.common.callbacks import CallbackList, CheckpointCallback, EvalCallback
from train.callbacks.plotting_callback import PlottingCallback

def create_callback_list(config: dict, eval_env, model_name: str, models_dir: str, models_history_dir: str,logs_dir: str):
    """
    根据配置创建并返回一个包含所有必要回调的 CallbackList。
    """

    training_config = config['training']

    plotting_callback = PlottingCallback(logs_dir=logs_dir, model_name=model_name)

    # save_freq: 每隔多少步保存一次
    checkpoint_callback = CheckpointCallback(
        save_freq=training_config['save_freq'],
        save_path=models_history_dir,
        name_prefix=model_name,
        save_replay_buffer=True,
        save_vecnormalize=True,
    )

    # eval_freq: 每隔多少步评估一次
    # best_model_save_path: 自动保存迄今为止表现最好的模型
    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path=os.path.join(models_dir, 'best_model'),
        log_path=os.path.join(logs_dir, 'eval'),
        eval_freq=training_config['eval_freq'],
        n_eval_episodes=training_config['n_eval_episodes'],
        deterministic=True,
        render=False
    )
    return CallbackList([plotting_callback, checkpoint_callback, eval_callback])