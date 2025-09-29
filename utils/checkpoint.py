import os
import glob
from stable_baselines3.common.callbacks import BaseCallback
import numpy as np

class Checkpoint(BaseCallback):
    """
    一个检查点回调函数，用于根据任务的实际表现来保存最佳模型。
    """
    def __init__(self, save_path: str, model_name: str, verbose: int = 1):
        super(Checkpoint, self).__init__(verbose)
        self.save_path = save_path
        self.model_name = model_name
        self.best_mean_reward = -np.inf
        self.best_model_checkpoint_path = ""

        os.makedirs(self.save_path, exist_ok=True)

    def _on_step(self) -> bool:
        """这个方法是BaseCallback要求必须实现的，我们在这里不需要做任何事。"""
        return True

    def _on_rollout_end(self) -> None:
        """
        这个方法在每次rollout数据收集结束后被SB3自动调用。
        这是我们检查模型表现并保存检查点的最佳时机。
        """
        log_dict = self.model.logger.name_to_value
        if 'rollout/ep_rew_mean' in log_dict:
            current_mean_reward = log_dict['rollout/ep_rew_mean']
            checkpoint_base_name = f"{self.model_name}_{self.num_timesteps}_steps_reward_{current_mean_reward:.2f}"
            checkpoint_base_path = os.path.join(self.save_path, checkpoint_base_name)
            
            zip_path = f"{checkpoint_base_path}.zip"
            safetensors_path = f"{checkpoint_base_path}.safetensors"
            self.model.save(zip_path)
            self.model.policy.save(safetensors_path)
            
            if self.verbose > 0:
                print(f"检查点已保存 (Mean Reward: {current_mean_reward:.2f}): {zip_path}")
            if current_mean_reward > self.best_mean_reward:
                self.best_mean_reward = current_mean_reward
                self.best_model_checkpoint_path = checkpoint_base_path
                if self.verbose > 0:
                    print(f"新的最佳模型! 平均奖励: {self.best_mean_reward:.2f}, 路径: {self.best_model_checkpoint_path}")
    
    def cleanup_and_save_best(self):
        """
        这个方法应该在 .learn() 调用结束后手动执行。
        它会清理掉所有不是最佳模型的临时文件。
        """
        print("\n----------- 训练结束，开始根据平均奖励清理检查点 -----------")
        
        if not self.best_model_checkpoint_path or not os.path.exists(f"{self.best_model_checkpoint_path}.zip"):
            print("警告: 未找到有效的最佳模型检查点，无法进行清理。请检查训练过程中是否至少完成了一个回合。")
            final_model_path = os.path.join(self.save_path, f"{self.model_name}.zip")
            if os.path.exists(final_model_path):
                print(f"保留原始模型: {final_model_path}")
            return

        print(f"最佳模型是: {os.path.basename(self.best_model_checkpoint_path)} (平均奖励: {self.best_mean_reward:.2f})")
        final_model_base_path = os.path.join(self.save_path, self.model_name)
        all_zip_checkpoints = glob.glob(os.path.join(self.save_path, f"{self.model_name}_*_steps_reward_*.zip"))
        
        for zip_path in all_zip_checkpoints:
            current_base_path = os.path.splitext(zip_path)[0]
            if current_base_path == self.best_model_checkpoint_path:
                print(f"正在将最佳模型 .zip 重命名为: {final_model_base_path}.zip")
                os.replace(zip_path, f"{final_model_base_path}.zip")
                safetensors_path = f"{current_base_path}.safetensors"
                if os.path.exists(safetensors_path):
                    print(f"正在将最佳模型 .safetensors 重命名为: {final_model_base_path}.safetensors")
                    os.replace(safetensors_path, f"{final_model_base_path}.safetensors")
            else:
                os.remove(zip_path)
                safetensors_path = f"{current_base_path}.safetensors"
                if os.path.exists(safetensors_path):
                    os.remove(safetensors_path)
        
        print(f"清理完成！最终模型已保存到: {final_model_base_path}.zip")