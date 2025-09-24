import socket
import json
import time

HOST = '127.0.0.1'
PORT = 8080

def main():
    print("尝试连接到 Minecraft 模组...")
    #使用with语句可以确保socket在结束后被正确关闭
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
            print("连接成功！")
        except ConnectionRefusedError:
            print("连接失败。请确保 Minecraft 和模组已经运行。")
            return
        #创建一个循环来持续发送和接收数据
        try:
            while True:
                #从用户输入获取指令
                command = input("输入指令 (例如 'move forward' 或 'attack') > ")
                if command.lower() == 'exit':
                    break
                s.sendall(f"{command}\n".encode('utf-8'))

                #接收来自模组的状态信息
                data = s.recv(1024)
                if not data:
                    print("与服务器的连接已断开。")
                    break
                response_str = data.decode('utf-8')
                #假设服务器可能一次发送多个JSON对象，简单处理一下
                response_json = json.loads(response_str.strip())

                print(f"从 Minecraft 收到: {response_json}")

        except KeyboardInterrupt:
            print("\n正在关闭连接...")
        finally:
            print("连接已关闭。")

if __name__ == '__main__':
    main()