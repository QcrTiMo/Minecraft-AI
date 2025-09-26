import os
from stable_baselines3 import PPO
from safetensors.torch import save_file

from agent.model import MLP_POLICY_KWARGS

class PPOAgent:
    """
    一个封装了Stable_Baselines3 PPO模型的智能体类。
    """
    def __init__(self, env, model_name, models_dir, logs_dir):
        self.env = env
        self.model_name = model_name
        self.models_dir = models_dir
        self.logs_dir = logs_dir
        
        #实例化PPO模型
        self.model = PPO(
            "MlpPolicy",
            self.env,
            policy_kwargs=MLP_POLICY_KWARGS,
            verbose=1,
            device='auto',
            tensorboard_log=os.path.join(self.logs_dir, "tensorboard")
        )

    def learn(self, total_timesteps, callback):
        """
        开始训练模型。
        """
        print(f"----------- 开始训练 {self.model_name} -----------")
        self.model.learn(
            total_timesteps=total_timesteps,
            reset_num_timesteps=False,
            callback=callback
        )
        print(f"----------- 训练结束 -----------")

    def save(self):
        """
        将训练好的模型保存到磁盘。
        """
        zip_path = os.path.join(self.models_dir, f"{self.model_name}.zip")
        safetensors_path = os.path.join(self.models_dir, f"{self.model_name}.safetensors")

        self.model.save(zip_path)
        print(f"完整模型已保存到: {zip_path}")

        policy_state_dict = self.model.policy.to("cpu").state_dict()
        save_file(policy_state_dict, safetensors_path)
        print(f"模型权重已安全保存到: {safetensors_path}")

    @staticmethod
    def load(env, model_name, models_dir):
        """
        加载一个已经训练好的模型。
        """
        zip_path = os.path.join(models_dir, f"{model_name}.zip")
        if os.path.exists(zip_path):
            print(f"正在从 {zip_path} 加载预训练模型...")
            return PPO.load(zip_path, env=env)
        else:
            print(f"错误: 找不到预训练模型 {zip_path}")
            return None