import asyncio
import websockets
import json

WEB_SOCKET_URI = "ws://localhost:3000"

async def send_action(websocket, action_name, params=None):
    """一个辅助函数，用于发送格式化的动作指令。"""
    if params is None:
        params = {}
    
    action_message = {
        "type": "action",
        "action": {
            "name": action_name,
            **params
        }
    }
    await websocket.send(json.dumps(action_message))
    print(f"Sent action: {action_message}")

async def run_test():
    """
    连接到 WebSocket 服务器并执行一系列预设的测试动作。
    """
    async with websockets.connect(WEB_SOCKET_URI) as websocket:
        print("连接成功！开始执行测试脚本...")
        await asyncio.sleep(1)
        await send_action(websocket, "chat", {"message": "大家好，我是测试机器人！"})
        await asyncio.sleep(2) 

        #向前移动
        print("执行动作：向前移动")
        await send_action(websocket, "move_forward")
        await asyncio.sleep(2)

        #跳跃
        print("执行动作：跳跃")
        await send_action(websocket, "jump")
        await asyncio.sleep(2)

        #发送结束消息
        await send_action(websocket, "chat", {"message": "测试脚本执行完毕。"})
        print("测试完成，关闭连接。")


if __name__ == "__main__":
    try:
        asyncio.run(run_test())
    except ConnectionRefusedError:
        print("[错误] 连接被拒绝。请确认 mineflayer_env.js 脚本正在运行。")
    except Exception as e:
        print(f"发生了一个错误: {e}")