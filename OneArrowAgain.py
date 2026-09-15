import pygame
import sys

from game_logic import is_blocked
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

# 棋盘设置
ROWS = 6
COLS = 6
CELL_SIZE = 70

BOARD_WIDTH = COLS * CELL_SIZE
BOARD_HEIGHT = ROWS * CELL_SIZE
BOARD_X = (WIDTH - BOARD_WIDTH) // 2
BOARD_Y = 160

# 临时关卡数据：行、列、方向
arrows = [
    {"row": 0, "col": 1, "direction": "UP"},
    {"row": 1, "col": 4, "direction": "RIGHT"},
    {"row": 3, "col": 2, "direction": "DOWN"},
    {"row": 4, "col": 0, "direction": "LEFT"},
    {"row": 5, "col": 5, "direction": "RIGHT"},
    {"row": 3, "col": 4, "direction": "LEFT"},
]

current_level = 1
mistakes_left = 3

# 当前被点击的箭头
selected_arrow = None

# 游戏界面状态
START = "start"
PLAYING = "playing"
RESULT = "result"

game_state = START

def get_clicked_arrow(mouse_pos):
    """根据鼠标位置查找被点击的箭头"""
    mouse_x, mouse_y = mouse_pos

    # 判断鼠标是否位于棋盘范围内
    if not (
        BOARD_X <= mouse_x < BOARD_X + BOARD_WIDTH
        and BOARD_Y <= mouse_y < BOARD_Y + BOARD_HEIGHT
    ):
        return None

    # 将鼠标坐标换算成棋盘行列
    col = (mouse_x - BOARD_X) // CELL_SIZE
    row = (mouse_y - BOARD_Y) // CELL_SIZE

    # 查找该格子中是否存在箭头
    for arrow in arrows:
        if arrow["row"] == row and arrow["col"] == col:
            return arrow

    return None


def draw_arrow(arrow):
    """根据行、列和方向绘制箭头"""
    row = arrow["row"]
    col = arrow["col"]
    direction = arrow["direction"]

    center_x = BOARD_X + col * CELL_SIZE + CELL_SIZE // 2
    center_y = BOARD_Y + row * CELL_SIZE + CELL_SIZE // 2

    direction_vectors = {
        "UP": (0, -1),
        "DOWN": (0, 1),
        "LEFT": (-1, 0),
        "RIGHT": (1, 0)
    }

    dx, dy = direction_vectors[direction]

    # 箭杆起点和箭头尖端
    tail_x = center_x - dx * 20
    tail_y = center_y - dy * 20

    tip_x = center_x + dx * 24
    tip_y = center_y + dy * 24

    # 箭头三角形底部的中心
    base_x = center_x + dx * 8
    base_y = center_y + dy * 8

    # 与箭头方向垂直的向量
    perpendicular_x = -dy
    perpendicular_y = dx

    left_x = base_x + perpendicular_x * 11
    left_y = base_y + perpendicular_y * 11

    right_x = base_x - perpendicular_x * 11
    right_y = base_y - perpendicular_y * 11

    # 被选中的箭头显示为橙色
    if arrow is selected_arrow:
        arrow_color = (240, 140, 50)
    else:
        arrow_color = (45, 95, 150)

    pygame.draw.line(
        screen,
        arrow_color,
        (tail_x, tail_y),
        (base_x, base_y),
        7
    )

    pygame.draw.polygon(
        screen,
        arrow_color,
        [
            (tip_x, tip_y),
            (left_x, left_y),
            (right_x, right_y)
        ]
    )


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

    # 显示关卡信息
    level_text = button_font.render(
        f"第 {current_level} 关",
        True,
        (45, 65, 85)
    )
    screen.blit(level_text, (60, 45))

    remaining_text = button_font.render(
        f"剩余箭头：{len(arrows)}",
        True,
        (45, 65, 85)
    )
    screen.blit(remaining_text, (330, 45))

    mistake_text = button_font.render(
        f"剩余失误：{mistakes_left}",
        True,
        (190, 70, 70)
    )
    screen.blit(mistake_text, (630, 45))

    # 绘制棋盘背景
    pygame.draw.rect(
        screen,
        (255, 255, 255),
        (BOARD_X, BOARD_Y, BOARD_WIDTH, BOARD_HEIGHT),
        border_radius=8
    )

    # 绘制棋盘格
    for row in range(ROWS):
        for col in range(COLS):
            cell_rect = pygame.Rect(
                BOARD_X + col * CELL_SIZE,
                BOARD_Y + row * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE
            )

            pygame.draw.rect(
                screen,
                (190, 200, 210),
                cell_rect,
                1
            )

    # 绘制全部箭头
    for arrow in arrows:
        draw_arrow(arrow)


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

                elif game_state == PLAYING:
                    selected_arrow = get_clicked_arrow(event.pos)

                    if selected_arrow is not None:
                        blocked = is_blocked(selected_arrow, arrows)

                        print(
                            "点击箭头：",
                            selected_arrow["row"],
                            selected_arrow["col"],
                            selected_arrow["direction"],
                            "是否阻挡：",
                            blocked
                        )

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