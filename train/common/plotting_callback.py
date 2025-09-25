import os
import matplotlib.pyplot as plt
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
        if self.num_timesteps % self.check_freq == 0:
            reward = self.logger.get_value('rollout/ep_rew_mean')
            if reward is not None:
                self.timesteps.append(self.num_timesteps)
                self.rewards.append(reward)
        return True

    def plot_and_save(self):
        save_path = os.path.join(self.logs_dir, f"{self.model_name}_学习曲线.png")
        if not self.timesteps or not self.rewards:
            print("警告: 没有收集到足够的数据来绘制图表。")
            return
        plt.figure(figsize=(12, 6))
        plt.plot(self.timesteps, self.rewards)
        plt.title(f'{self.model_name} 学习曲线')
        plt.xlabel('时间步数')
        plt.ylabel('平均奖励')
        plt.grid(True)
        plt.savefig(save_path)
        plt.close()
        print(f"学习曲线图已保存到: {save_path}")