import gym
import minerl
import pygame
import numpy as np
import logging
import traceback
WINDOW_WIDTH = 854
WINDOW_HEIGHT = 480
#pygame开关
ENABLE_PYGAME_RENDERER = False

logging.basicConfig(level=logging.INFO)

class PygameRenderer:
    """
    一个用于将MineRL观察数据显示在Pygame窗口中的渲染器类。
    """
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.screen = None
        self.clock = None
        self.is_initialized = False

    def _initialize(self):
        """私有方法，用于初始化Pygame。"""
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("我的世界AI")
        self.clock = pygame.time.Clock()
        self.is_initialized = True
        logging.info("Pygame渲染器初始化成功！")

    def render_frame(self, obs, fps=20):
        """
        渲染单帧游戏画面。
        如果Pygame还未初始化，这个方法会自动调用初始化方法。
        """
        if not self.is_initialized:
            self._initialize()

        #从观察数据中提取玩家视角的图像 (pov = Point of View)
        pov_frame = obs['pov']
        
        #Pygame需要的数据格式是 (宽, 高, 颜色通道)
        #MineRL提供的是 (高, 宽, 颜色通道)，我们需要交换维度
        pov_frame_transposed = np.transpose(pov_frame, (1, 0, 2))

        #将图像数据转换为Pygame可以处理的Surface对象并缩放
        surface = pygame.surfarray.make_surface(pov_frame_transposed)
        scaled_surface = pygame.transform.scale(surface, (self.width, self.height))
        self.screen.blit(scaled_surface, (0, 0))

        #更新整个显示屏
        pygame.display.flip()

        #控制帧率
        self.clock.tick(fps)

    def handle_events(self):
        if not self.is_initialized:
            return False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
        return False

    def close(self):
        """关闭Pygame窗口并退出。"""
        if self.is_initialized:
            pygame.quit()
            logging.info("Pygame渲染器已关闭。")
def main():
    env = None
    renderer = None
    if ENABLE_PYGAME_RENDERER:
        renderer = PygameRenderer(WINDOW_WIDTH, WINDOW_HEIGHT)

    try:
        logging.info("正在创建MineRL环境，初次加载资源可能需要较长时间...")
        env = gym.make('MineRLNavigateDense-v0')
        logging.info("环境创建成功！")
        
        obs = env.reset()
        logging.info("环境重置成功，AI开始行动！")

        done = False
        while not done:
            env.render()
            #让AI执行随机动作
            action = env.action_space.sample()
            obs, reward, done, info = env.step(action)
            #如果渲染器被启用，就调用它的方法来显示画面和处理事件
            if renderer:
                renderer.render_frame(obs)
                #如果用户点击了关闭按钮，我们就结束循环
                if renderer.handle_events():
                    done = True
            


    except Exception as e:
        logging.error("在执行过程中发生了错误！")
        traceback.print_exc()
    finally:
        if env is not None:
            logging.info("正在关闭MineRL环境...")
            env.close()
        if renderer:
            renderer.close()
        
        logging.info("程序执行完毕。")

if __name__ == '__main__':
    main()