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

# 开始界面的字体
title_font = pygame.font.SysFont("Microsoft YaHei", 56)
button_font = pygame.font.SysFont("Microsoft YaHei", 30)

# 开始按钮的位置和大小
start_button = pygame.Rect(
    WIDTH // 2 - 120,
    HEIGHT // 2 + 50,
    240,
    70
)

# 游戏界面状态
START = "start"
PLAYING = "playing"
RESULT = "result"

game_state = START


def draw_start_screen():
    """绘制开始界面"""
    screen.fill((238, 244, 248))

    # 绘制游戏标题
    title_text = title_font.render(
        "一箭又一箭",
        True,
        (45, 65, 85)
    )
    title_rect = title_text.get_rect(
        center=(WIDTH // 2, 220)
    )
    screen.blit(title_text, title_rect)

    # 鼠标放在按钮上时改变颜色
    mouse_pos = pygame.mouse.get_pos()

    if start_button.collidepoint(mouse_pos):
        button_color = (90, 170, 245)
    else:
        button_color = (70, 150, 230)

    # 绘制开始按钮
    pygame.draw.rect(
        screen,
        button_color,
        start_button,
        border_radius=15
    )

    # 绘制按钮文字
    button_text = button_font.render(
        "开始游戏",
        True,
        (255, 255, 255)
    )
    button_text_rect = button_text.get_rect(
        center=start_button.center
    )
    screen.blit(button_text, button_text_rect)


def draw_game_screen():
    """绘制游戏界面"""
    screen.fill((245, 242, 235))


def draw_result_screen():
    """绘制通关或失败界面"""
    screen.fill((230, 240, 235))


running = True

while running:
    # 处理鼠标、键盘和关闭窗口事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # 鼠标左键点击
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if game_state == START:
                    if start_button.collidepoint(event.pos):
                        game_state = PLAYING

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