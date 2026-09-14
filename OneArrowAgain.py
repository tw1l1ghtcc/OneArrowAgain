import pygame
import sys
# 初始化 Pygame
pygame.init()

# 窗口设置
WIDTH = 900
HEIGHT = 700
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("一箭又一箭")

clock = pygame.time.Clock()

# 游戏界面状态
START = "start"
PLAYING = "playing"
RESULT = "result"

game_state = START


def draw_start_screen():
    """绘制开始界面"""
    screen.fill((238, 244, 248))


def draw_game_screen():
    """绘制游戏界面"""
    screen.fill((245, 242, 235))


def draw_result_screen():
    """绘制通关或失败界面"""
    screen.fill((230, 240, 235))


running = True

while running:
    # 处理鼠标、键盘和关闭窗口等事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 根据当前状态绘制不同界面
    if game_state == START:
        draw_start_screen()
    elif game_state == PLAYING:
        draw_game_screen()
    elif game_state == RESULT:
        draw_result_screen()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()