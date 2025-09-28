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
    def __init__(self, logs_dir: str, model_name: str, verbose=1):
        super(PlottingCallback, self).__init__(verbose)
        self.logs_dir = logs_dir
        self.model_name = model_name
        
        #用于存储回合奖励数据
        self.episode_timesteps = []
        self.episode_rewards = []
        
        #用于存储详细的训练指标
        self.train_timesteps = []
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
        """
        这个方法在每个环境步骤后调用，我们用它来捕获回合结束的奖励。
        """
        if 'infos' in self.locals and len(self.locals['infos']) > 0:
            info = self.locals['infos'][0]
            if 'episode' in info:
                self.episode_timesteps.append(self.num_timesteps)
                self.episode_rewards.append(info['episode']['r'])
        return True

    def _on_rollout_end(self) -> None:
        """
        这个方法在每次rollout收集结束 (模型即将更新) 后调用。
        这是获取 train/* 指标的最佳时机。
        """
        log_dict = self.model.logger.name_to_value
        is_valid_log = False
        for key in self.train_metrics.keys():
            full_key = f'train/{key}'
            if full_key in log_dict:
                self.train_metrics[key].append(log_dict[full_key])
                is_valid_log = True
        if is_valid_log:
            self.train_timesteps.append(self.num_timesteps)


    def plot_and_save(self):
        """
        在训练结束后，调用此方法来绘制并保存所有图表。
        """
        os.makedirs(self.logs_dir, exist_ok=True)
        
        #绘制奖励曲线
        self._plot_rewards()
        
        #绘制详细训练指标
        self._plot_train_metrics()

    def _plot_rewards(self):
        save_path = os.path.join(self.logs_dir, f"{self.model_name}_奖励曲线.png")
        if not self.episode_timesteps:
            print("警告: 没有收集到足够的回合数据来绘制奖励曲线。")
            return
        plt.figure(figsize=(12, 6))
        plt.plot(self.episode_timesteps, self.episode_rewards)
        plt.title(f'{self.model_name} 奖励曲线 (每回合总奖励)')
        plt.xlabel('时间步数 (Timesteps)')
        plt.ylabel('该回合总奖励 (Total Reward)')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()
        print(f"奖励曲线图已保存到: {save_path}")

    def _plot_train_metrics(self):
        save_path = os.path.join(self.logs_dir, f"{self.model_name}_训练指标.png")
        if not self.train_timesteps:
            print("警告: 没有收集到足够的训练指标数据来绘制图表。")
            return
            
        #创建一个包含多个子图的大图
        fig, axs = plt.subplots(4, 2, figsize=(15, 16))
        fig.suptitle(f'{self.model_name} 详细训练指标', fontsize=16)
        axs = axs.flatten()

        for i, (key, values) in enumerate(self.train_metrics.items()):
            if values:
                axs[i].plot(self.train_timesteps, values)
                axs[i].set_title(key)
                axs[i].set_xlabel('时间步数 (Timesteps)')
                axs[i].grid(True)
        
        #调整子图布局
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.savefig(save_path)
        plt.close()
        print(f"详细训练指标图已保存到: {save_path}")