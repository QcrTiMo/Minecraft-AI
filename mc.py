import minecraft_launcher_lib
import subprocess
import sys
import os
import uuid

script_directory = os.path.dirname(os.path.abspath(__file__))
minecraft_directory = os.path.join(script_directory, '.minecraft')
fabric_version_id = "1.21.8"

#检查路径和版本是否存在
if not os.path.isdir(minecraft_directory):
    print(f"错误：找不到Minecraft目录: {minecraft_directory}")
    print("请确保你的Python脚本和.minecraft文件夹都在'mc-ai'目录下。")
    sys.exit(1)

version_path = os.path.join(minecraft_directory, 'versions', fabric_version_id)
if not os.path.isdir(version_path):
    print(f"错误：找不到指定的版本: {fabric_version_id}")
    print(f"请检查路径 '{version_path}' 是否存在。")
    sys.exit(1)

print(f"将使用Minecraft目录: {minecraft_directory}")
print(f"将启动版本: {fabric_version_id}")

#设置启动选项
player_name = "AI_agent"
player_uuid = str(uuid.uuid4())
access_token = "0"
options = {
    "username": player_name,
    "uuid": player_uuid,
    "token": access_token
}

#获取启动命令
minecraft_command = minecraft_launcher_lib.command.get_minecraft_command(
    version=fabric_version_id,
    minecraft_directory=minecraft_directory,
    options=options
)

#启动游戏
print("正在启动《我的世界》...")
subprocess.run(minecraft_command)
print("游戏已关闭。")