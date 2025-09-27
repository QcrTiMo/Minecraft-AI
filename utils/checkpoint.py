import os
import glob
import numpy as np
from stable_baselines3.common.callbacks import BaseCallback

class Checkpoint(BaseCallback):
    """
    在每次rollout结束时，保存一个临时的检查点模型。
    跟踪训练过程中的最低损失 (loss)。
    在训练结束后，找到并保留损失最低的那个检查点模型，重命名为最终模型，
    并删除所有其他的临时检查点。
    """
    def __init__(self, save_path: str, model_name: str, verbose=1):
        super(Checkpoint, self).__init__(verbose)
        self.save_path = save_path
        self.model_name = model_name
        self.best_loss = np.inf  #初始化最佳损失为无穷大
        self.best_model_path = ""
        
        #确保保存路径存在
        os.makedirs(self.save_path, exist_ok=True)
    
    def _on_step(self) -> bool:
        """
        这个方法是BaseCallback要求必须实现的。
        由于我们的逻辑都在_on_rollout_end中，所以这里我们只需要让它返回True继续训练即可
        """
        return True

    def _on_rollout_end(self) -> None:
        """
        这个方法在每次rollout收集结束后调用。
        """
        #从logger获取当前的loss值
        current_loss = self.model.logger.name_to_value.get('train/loss')
        
        #只有在loss存在时才进行操作
        if current_loss is not None:
            #保存当前的检查点模型
            checkpoint_name = f"{self.model_name}_{self.num_timesteps}_steps_loss_{current_loss:.2f}.zip"
            checkpoint_path = os.path.join(self.save_path, checkpoint_name)
            self.model.save(checkpoint_path)
            if self.verbose > 0:
                print(f"检查点已保存到: {checkpoint_path}")

            #检查并更新最佳模型
            if current_loss < self.best_loss:
                self.best_loss = current_loss
                self.best_model_path = checkpoint_path
                if self.verbose > 0:
                    print(f"新的最佳模型! Loss: {self.best_loss:.2f}, Path: {self.best_model_path}")
    
    def cleanup_and_save_best(self):
        """
        这个方法应该在训练完全结束后手动调用。
        """
        print("\n----------- 训练结束，开始清理检查点 -----------")
        
        #找到所有为这个模型保存的检查点文件
        all_checkpoints = glob.glob(os.path.join(self.save_path, f"{self.model_name}_*_steps_loss_*.zip"))
        
        if not self.best_model_path or not os.path.exists(self.best_model_path):
            print("警告: 未找到最佳模型，可能是训练时间太短或未成功保存任何检查点。")
            return

        print(f"最佳模型是: {self.best_model_path} (Loss: {self.best_loss:.2f})")
        
        #最终模型的保存路径
        final_model_path = os.path.join(self.save_path, f"{self.model_name}.zip")
        
        #遍历所有检查点
        for checkpoint_path in all_checkpoints:
            #如果是最佳模型，就重命名为最终名称
            if checkpoint_path == self.best_model_path:
                print(f"正在将最佳模型重命名为: {final_model_path}")
                os.rename(checkpoint_path, final_model_path)
            #如果不是最佳模型，就删除
            else:
                print(f"正在删除临时检查点: {checkpoint_path}")
                os.remove(checkpoint_path)
        
        #如果最佳模型因为某些原因没有在循环中被处理
        #我们需要确保它仍然被正确地保存
        if os.path.exists(self.best_model_path) and not os.path.exists(final_model_path):
            os.rename(self.best_model_path, final_model_path)
        
        print(f"清理完成！最终模型已保存到: {final_model_path}")