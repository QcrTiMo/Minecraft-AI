import os
import glob
from stable_baselines3.common.callbacks import BaseCallback
import numpy as np

class Checkpoint(BaseCallback):
    """
    在每次总结时，同时保存 .zip (完整检查点) 和 .safetensors (权重) 文件。
    跟踪训练过程中的各项基本数值。
    Score = (10.0 * explained_variance) - (0.1 * value_loss) + (1.0 * entropy_loss) - (1.0 * abs(policy_gradient_loss))
    在训练结束后，找到并保留Score最高的那个模型的 .zip 和 .safetensors 文件，
    并删除所有其他的临时检查点。
    """
    def __init__(self, save_path: str, model_name: str, verbose=1):
        super(Checkpoint, self).__init__(verbose)
        self.save_path = save_path
        self.model_name = model_name
        self.best_score = -np.inf  # 初始化最佳分数为负无穷大
        self.best_model_checkpoint_path = ""
        
        #定义指标权重
        self.weights = {
            'w_explained_variance': 10.0,
            'w_value_loss': 0.1,
            'w_entropy_loss': 1.0,
            'w_policy_loss': 1.0
        }

        os.makedirs(self.save_path, exist_ok=True)

    def _on_step(self) -> bool:
        """这个方法是BaseCallback要求必须实现的。"""
        return True

    def _calculate_score(self, log_dict: dict) -> float:
        """根据日志字典计算综合分数"""
        ev = log_dict.get('train/explained_variance', 0.0)
        v_loss = log_dict.get('train/value_loss', 0.0)
        e_loss = log_dict.get('train/entropy_loss', 0.0)
        p_loss = log_dict.get('train/policy_gradient_loss', 0.0)

        score = (self.weights['w_explained_variance'] * ev -
                 self.weights['w_value_loss'] * v_loss +
                 self.weights['w_entropy_loss'] * e_loss -
                 self.weights['w_policy_loss'] * abs(p_loss))
        return score

    def _on_rollout_end(self) -> None:
        """这个方法在每次rollout收集结束后调用。"""
        log_dict = self.model.logger.name_to_value
        if 'train/loss' in log_dict:
            #计算当前模型的综合分数
            current_score = self._calculate_score(log_dict)
            
            #保存当前的检查点模型，文件名中包含分数
            checkpoint_base_name = f"{self.model_name}_{self.num_timesteps}_steps_score_{current_score:.2f}"
            checkpoint_base_path = os.path.join(self.save_path, checkpoint_base_name)
            
            zip_path = f"{checkpoint_base_path}.zip"
            safetensors_path = f"{checkpoint_base_path}.safetensors"

            self.model.save(zip_path)
            self.model.policy.save(safetensors_path)
            
            if self.verbose > 0:
                print(f"检查点已保存 (Score: {current_score:.2f}): {zip_path}")

            #检查并更新最佳模型
            if current_score > self.best_score:
                self.best_score = current_score
                self.best_model_checkpoint_path = checkpoint_base_path
                if self.verbose > 0:
                    print(f"新的最佳模型, Score: {self.best_score:.2f}, Path: {self.best_model_checkpoint_path}")
    
    def cleanup_and_save_best(self):
        """这个方法应该在训练完全结束后手动调用。"""
        print("\n----------- 训练结束，开始根据 Score 清理检查点 -----------")
        
        all_zip_checkpoints = glob.glob(os.path.join(self.save_path, f"{self.model_name}_*_steps_score_*.zip"))
        
        if not self.best_model_checkpoint_path:
            print("警告: 未找到最佳模型。")
            return

        print(f"最佳模型是: {self.best_model_checkpoint_path} (Score: {self.best_score:.2f})")
        
        final_model_base_path = os.path.join(self.save_path, self.model_name)
        
        for zip_path in all_zip_checkpoints:
            current_base_path = os.path.splitext(zip_path)[0]
            safetensors_path = f"{current_base_path}.safetensors"
            
            if current_base_path == self.best_model_checkpoint_path:
                print(f"正在将最佳模型 .zip 重命名为: {final_model_base_path}.zip")
                os.rename(zip_path, f"{final_model_base_path}.zip")
                if os.path.exists(safetensors_path):
                    print(f"正在将最佳模型 .safetensors 重命名为: {final_model_base_path}.safetensors")
                    os.rename(safetensors_path, f"{final_model_base_path}.safetensors")
            else:
                os.remove(zip_path)
                if os.path.exists(safetensors_path):
                    os.remove(safetensors_path)
        
        print(f"清理完成！最终模型已保存到: {final_model_base_path}.zip / .safetensors")