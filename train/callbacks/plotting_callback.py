import os
import matplotlib.pyplot as plt
import numpy as np
from stable_baselines3.common.callbacks import BaseCallback

try:
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
    plt.rcParams['axes.unicode_minus'] = False
except Exception as e:
    print(f"设置中文字体失败，图表中的中文可能无法正常显示: {e}")

class PlottingCallback(BaseCallback):
    """
    一个集成的绘图回调函数，用于在训练结束后生成一张包含所有关键指标的综合图表。
    """
    def __init__(self, logs_dir: str, model_name: str, verbose: int = 1):
        super(PlottingCallback, self).__init__(verbose)
        self.logs_dir = logs_dir
        self.model_name = model_name
        self.episode_timesteps = []
        self.episode_rewards = []
        self.rollout_timesteps = []
        self.rollout_metrics = {
            'ep_rew_mean': [],
            'ep_len_mean': []
        }
        
        self.train_metrics = {
            'loss': [],
            'value_loss': [],
            'policy_gradient_loss': [],
            'entropy_loss': [],
            'explained_variance': [],
            'approx_kl': [],
            'clip_fraction': []
        }

    def _on_step(self) -> bool:
        """在每个环境步骤后调用，用于捕获单次回合结束时的奖励。"""
        if 'infos' in self.locals and len(self.locals['infos']) > 0:
            info = self.locals['infos'][0]
            if 'episode' in info:
                self.episode_timesteps.append(self.num_timesteps)
                self.episode_rewards.append(info['episode']['r'])
        return True

    def _on_rollout_end(self) -> None:
        """在每次rollout收集数据结束后调用。"""
        log_dict = self.model.logger.name_to_value
        self.rollout_timesteps.append(self.num_timesteps)


        for key in self.rollout_metrics.keys():
            self.rollout_metrics[key].append(log_dict.get(full_key, np.nan))
        for key in self.train_metrics.keys():
            full_key = f'train/{key}'
            self.train_metrics[key].append(log_dict.get(full_key, np.nan))

    def plot_and_save(self):
        """在训练结束后，调用此方法来绘制并保存所有图表。"""
        print("\n----------- 训练结束，开始生成综合训练图表 -----------")
        os.makedirs(self.logs_dir, exist_ok=True)
        
        save_path = os.path.join(self.logs_dir, f"{self.model_name}_综合训练图表.png")
        
        plots_to_draw = []
        
        if any(np.isfinite(self.rollout_metrics['ep_rew_mean'])):
            plots_to_draw.append(('⭐ 平均回合奖励 (ep_rew_mean)', self.rollout_timesteps, self.rollout_metrics['ep_rew_mean']))
        if any(np.isfinite(self.rollout_metrics['ep_len_mean'])):
            plots_to_draw.append(('平均回合长度 (ep_len_mean)', self.rollout_timesteps, self.rollout_metrics['ep_len_mean']))
        if self.episode_rewards:
            plots_to_draw.append(('原始回合奖励 (Raw Reward)', self.episode_timesteps, self.episode_rewards))
        
        # 添加其他PPO训练指标
        for key, values in self.train_metrics.items():
            if any(np.isfinite(values)):
                plots_to_draw.append((f'训练指标: {key}', self.rollout_timesteps, values))

        if not plots_to_draw:
            print("警告: 没有收集到足够的数据来绘制任何图表。")
            return
        num_plots = len(plots_to_draw)
        cols = 2
        rows = (num_plots + cols - 1) // cols
        
        fig, axs = plt.subplots(rows, cols, figsize=(16, 5 * rows))
        fig.suptitle(f'{self.model_name} 综合训练图表', fontsize=20)
        axs = axs.flatten()

        for i, (title, timesteps, data) in enumerate(plots_to_draw):
            axs[i].plot(timesteps, data)
            axs[i].set_title(title, fontsize=12)
            axs[i].set_xlabel('时间步数 (Timesteps)')
            axs[i].grid(True)
        for i in range(num_plots, len(axs)):
            axs[i].set_visible(False)
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.savefig(save_path)
        plt.close(fig)
        print(f"✅ 综合训练图表已保存到: {save_path}")