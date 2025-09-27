import os
import matplotlib.pyplot as plt
import numpy as np
from stable_baselines3.common.callbacks import BaseCallback

class PlottingCallback(BaseCallback):
    def __init__(self, check_freq: int, logs_dir: str, model_name: str, verbose=1):
        super(PlottingCallback, self).__init__(verbose)
        self.check_freq = check_freq
        self.logs_dir = logs_dir
        self.model_name = model_name
        self.timesteps = []
        self.rewards = []

    def _on_step(self) -> bool:
        if 'infos' in self.locals and len(self.locals['infos']) > 0:
            info = self.locals['infos'][0]
            if 'episode' in info:
                ep_reward = info['episode']['r']
                #记录当前的时间步和这个回合的总奖励
                self.timesteps.append(self.num_timesteps)
                self.rewards.append(ep_reward)
        
        return True

    def plot_and_save(self):
        os.makedirs(self.logs_dir, exist_ok=True)
        save_path = os.path.join(self.logs_dir, f"{self.model_name}_学习曲线.png")

        if not self.timesteps or not self.rewards:
            print("警告: 没有收集到足够的数据来绘制图表。")
            return
            
        plt.figure(figsize=(12, 6))
        plt.plot(self.timesteps, self.rewards)
        plt.title(f'{self.model_name} 学习曲线 (每回合奖励)')
        plt.xlabel('时间步数 (Timesteps)')
        plt.ylabel('该回合总奖励 (Total Reward)')
        plt.grid(True)
        # 使用 tight_layout 优化边距
        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()
        print(f"学习曲线图已保存到: {save_path}")