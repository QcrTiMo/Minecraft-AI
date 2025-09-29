import os
import glob
from stable_baselines3.common.callbacks import BaseCallback
import numpy as np

class Checkpoint(BaseCallback):
    """
    一个集成了高频反馈和性能驱动的检查点回调。
    """
    def __init__(self, save_path: str, model_name: str, verbose: int = 1):
        super(Checkpoint, self).__init__(verbose)
        self.save_path = save_path
        self.model_name = model_name
        self.last_known_mean_reward = -np.inf
        self.best_mean_reward = -np.inf
        self.best_model_checkpoint_path = ""

        os.makedirs(self.save_path, exist_ok=True)

    def _on_step(self) -> bool:
        return True

    def _on_rollout_end(self) -> None:
        """在每次模型更新后调用"""
        log_dict = self.model.logger.name_to_value
        if 'rollout/ep_rew_mean' in log_dict:
            self.last_known_mean_reward = log_dict['rollout/ep_rew_mean']
        if 'train/loss' in log_dict:
            if self.last_known_mean_reward == -np.inf:
                if self.verbose > 0:
                    print("检查点: 正在等待第一个完整回合结束以获取有效的平均奖励...")
                return
            current_reward_for_eval = self.last_known_mean_reward
            checkpoint_base_name = f"{self.model_name}_{self.num_timesteps}_steps_reward_{current_reward_for_eval:.2f}"
            checkpoint_base_path = os.path.join(self.save_path, checkpoint_base_name)
            zip_path = f"{checkpoint_base_path}.zip"
            
            self.model.save(zip_path)
            
            if self.verbose > 0:
                print(f"检查点已保存 (最新平均奖励: {current_reward_for_eval:.2f}): {zip_path}")

            #检查并更新历史最佳模型
            if current_reward_for_eval > self.best_mean_reward:
                self.best_mean_reward = current_reward_for_eval
                self.best_model_checkpoint_path = checkpoint_base_path
                if self.verbose > 0:
                    print(f"新的最佳模型! 平均奖励: {self.best_mean_reward:.2f}, 路径: {self.best_model_checkpoint_path}")
    
    def cleanup_and_save_best(self):
        """在训练完全结束后手动调用，清理并保留最佳模型。"""
        print("\n----------- 训练结束，开始根据平均奖励清理检查点 -----------")
        
        all_zip_checkpoints = glob.glob(os.path.join(self.save_path, f"{self.model_name}_*_steps_reward_*.zip"))
        
        if not self.best_model_checkpoint_path or not os.path.exists(f"{self.best_model_checkpoint_path}.zip"):
            print("警告: 未找到有效的最佳模型检查点，清理程序将跳过。")
            return

        print(f"最佳模型是: {os.path.basename(self.best_model_checkpoint_path)} (平均奖励: {self.best_mean_reward:.2f})")
        final_model_base_path = os.path.join(self.save_path, self.model_name)
        
        for zip_path in all_zip_checkpoints:
            current_base_path = os.path.splitext(zip_path)[0]
            if current_base_path == self.best_model_checkpoint_path:
                print(f"正在将最佳模型 .zip 重命名为: {final_model_base_path}.zip")
                os.replace(zip_path, f"{final_model_base_path}.zip")
            else:
                os.remove(zip_path)
        
        print(f"清理完成！最终模型已保存到: {final_model_base_path}.zip")