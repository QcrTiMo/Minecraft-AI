import os
import glob
from stable_baselines3.common.callbacks import BaseCallback
import numpy as np

class CheckpointCallback(BaseCallback):
    """
    在每次总结时，同时保存 .zip (完整检查点) 和 .safetensors (权重) 文件。
    跟踪训练过程中的最低损失 (loss)。
    在训练结束后，找到并保留损失最低的那个模型的 .zip 和 .safetensors 文件，
    并删除所有其他的临时检查点。
    """
    def __init__(self, save_path: str, model_name: str, verbose=1):
        super(CheckpointCallback, self).__init__(verbose)
        self.save_path = save_path
        self.model_name = model_name
        self.best_loss = np.inf
        self.best_model_checkpoint_path = ""
        
        os.makedirs(self.save_path, exist_ok=True)

    def _on_step(self) -> bool:
        """这个方法是BaseCallback要求必须实现的。"""
        return True

    def _on_rollout_end(self) -> None:
        """这个方法在每次rollout收集结束后调用。"""
        current_loss = self.model.logger.name_to_value.get('train/loss')
        
        if current_loss is not None:
            checkpoint_base_name = f"{self.model_name}_{self.num_timesteps}_steps_loss_{current_loss:.2f}"
            checkpoint_base_path = os.path.join(self.save_path, checkpoint_base_name)
            zip_path = f"{checkpoint_base_path}.zip"
            safetensors_path = f"{checkpoint_base_path}.safetensors"
            self.model.save(zip_path)
            self.model.policy.save(safetensors_path)
            
            if self.verbose > 0:
                print(f"检查点已保存: {zip_path} 和 {safetensors_path}")

            #检查并更新最佳模型
            if current_loss < self.best_loss:
                self.best_loss = current_loss
                self.best_model_checkpoint_path = checkpoint_base_path
                if self.verbose > 0:
                    print(f"新的最佳模型, Loss: {self.best_loss:.2f}, Path: {self.best_model_checkpoint_path}")
    
    def cleanup_and_save_best(self):
        """这个方法应该在训练完全结束后手动调用。"""
        print("\n----------- 训练结束，开始清理检查点 -----------")
        
        all_zip_checkpoints = glob.glob(os.path.join(self.save_path, f"{self.model_name}_*_steps_loss_*.zip"))
        
        if not self.best_model_checkpoint_path:
            print("警告: 未找到最佳模型，可能是训练时间太短或未成功保存任何检查点。")
            return

        print(f"最佳模型是: {self.best_model_checkpoint_path} (Loss: {self.best_loss:.2f})")
        
        #最终模型的保存路径
        final_model_base_path = os.path.join(self.save_path, self.model_name)
        
        #遍历所有 .zip检查点
        for zip_path in all_zip_checkpoints:
            #获取当前检查点的基本路径
            current_base_path = os.path.splitext(zip_path)[0]
            safetensors_path = f"{current_base_path}.safetensors"
            
            #如果是最佳模型，就重命名
            if current_base_path == self.best_model_checkpoint_path:
                print(f"正在将最佳模型 .zip 重命名为: {final_model_base_path}.zip")
                os.rename(zip_path, f"{final_model_base_path}.zip")
                
                if os.path.exists(safetensors_path):
                    print(f"正在将最佳模型 .safetensors 重命名为: {final_model_base_path}.safetensors")
                    os.rename(safetensors_path, f"{final_model_base_path}.safetensors")
            else:
                print(f"正在删除临时检查点: {zip_path}")
                os.remove(zip_path)
                
                if os.path.exists(safetensors_path):
                    print(f"正在删除临时检查点: {safetensors_path}")
                    os.remove(safetensors_path)
        
        print(f"清理完成！最终模型已保存到: {final_model_base_path}.zip / .safetensors")