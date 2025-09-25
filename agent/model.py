import torch.nn as nn

#定义一个神经网络架构配置
MLP_POLICY_KWARGS = dict(
    net_arch=dict(
        pi=[128, 128],
        vf=[128, 128]
    ),
    activation_fn=nn.ReLU
)