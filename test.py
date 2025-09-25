import asyncio
import websockets
import json
import random

WEB_SOCKET_URI = "ws://localhost:3000"

async def send_action(websocket, action_name, params=None):
    if params is None:
        params = {}
    
    action_message = {
        "type": "action",
        "action": {
            "name": action_name,
            "params": params
        }
    }
    print(f"发送动作: {action_name}，参数: {params}")
    await websocket.send(json.dumps(action_message))


async def run_agent():
    async with websockets.connect(WEB_SOCKET_URI) as websocket:
        print("已成功连接到 Mineflayer 环境。")
        
        async for message in websocket:
            state_data = json.loads(message)
            if state_data.get('type') == 'state':
                basic_info = state_data.get('basic', {})
                surroundings = state_data.get('surroundings', [])
                print(f"收到状态: 生命值={basic_info.get('health')}, 位置={basic_info.get('position')}")
                bot_pos = basic_info.get('position', {})
                foot_pos = {'x': int(bot_pos.get('x')), 'y': int(bot_pos.get('y')) - 1, 'z': int(bot_pos.get('z'))}
                block_under_feet = "未知"
                for block in surroundings:
                    b_pos = block.get('position', {})
                    if b_pos.get('x') == foot_pos['x'] and b_pos.get('y') == foot_pos['y'] and b_pos.get('z') == foot_pos['z']:
                        block_under_feet = block.get('name')
                        break
                print(f"机器人脚下的方块是: {block_under_feet}")
                
                await asyncio.sleep(1)
                action_name = random.choice(['move', 'look', 'jump'])
                if action_name == 'move':
                    direction = random.choice(['forward', 'back', 'left', 'right'])
                    await send_action(websocket, 'move', {'direction': direction, 'duration': 1000})
                elif action_name == 'look':
                    yaw = random.uniform(-3.14, 3.14)
                    pitch = 0
                    await send_action(websocket, 'look', {'yaw': yaw, 'pitch': pitch})
                elif action_name == 'jump':
                    await send_action(websocket, 'jump')

if __name__ == "__main__":
    try:
        asyncio.run(run_agent())
    except KeyboardInterrupt:
        print("代理已由用户手动停止。")
    except websockets.exceptions.ConnectionClosedError:
        print("与环境的连接已断开。请检查bot.js是否正在运行。")