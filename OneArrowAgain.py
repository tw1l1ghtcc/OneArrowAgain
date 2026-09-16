import pygame
import sys

from game_logic import is_blocked
from levels import LEVELS
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


info_font = pygame.font.SysFont("Microsoft YaHei", 20)
# 开始按钮的位置和大小
start_button = pygame.Rect(
    WIDTH // 2 - 120,
    HEIGHT // 2 + 50,
    240,
    70
)

# 游戏和失败界面的重新开始按钮
restart_button = pygame.Rect(
    WIDTH // 2 - 120,
    610,
    240,
    60
)


# 棋盘设置
ROWS = 6
COLS = 6
CELL_SIZE = 70

BOARD_WIDTH = COLS * CELL_SIZE
BOARD_HEIGHT = ROWS * CELL_SIZE
BOARD_X = (WIDTH - BOARD_WIDTH) // 2
BOARD_Y = 160

# 当前关卡编号从1开始
current_level = 1

# 创建当前关卡的游戏数据副本
arrows = [
    arrow.copy()
    for arrow in LEVELS[current_level - 1]["arrows"]
]

mistakes_left = LEVELS[current_level - 1]["mistakes"]

# 当前被点击的箭头
selected_arrow = None

# 碰撞反馈状态
collision_arrow = None
collision_until = 0

# 游戏界面状态
START = "start"
PLAYING = "playing"
RESULT = "result"

game_state = START

# None表示尚无结果，clear表示通关，failed表示失败
result_kind = None

# 飞出动画状态
FLIGHT_SPEED = 700  # 每秒移动700像素
flying_arrow = None
flight_offset_x = 0.0
flight_offset_y = 0.0


def update_flight(dt):
    """移动箭头，完全离开棋盘后删除"""
    global flying_arrow, flight_offset_x, flight_offset_y
    global game_state, result_kind

    if flying_arrow is None:
        return

    direction_vectors = {
        "UP": (0, -1),
        "DOWN": (0, 1),
        "LEFT": (-1, 0),
        "RIGHT": (1, 0)
    }

    dx, dy = direction_vectors[flying_arrow["direction"]]

    flight_offset_x += dx * FLIGHT_SPEED * dt
    flight_offset_y += dy * FLIGHT_SPEED * dt

    center_x = (
        BOARD_X
        + flying_arrow["col"] * CELL_SIZE
        + CELL_SIZE // 2
        + flight_offset_x
    )
    center_y = (
        BOARD_Y
        + flying_arrow["row"] * CELL_SIZE
        + CELL_SIZE // 2
        + flight_offset_y
    )

    # 留出30像素，确保整个箭头已经离开棋盘
    outside = (
        center_x < BOARD_X - 30
        or center_x > BOARD_X + BOARD_WIDTH + 30
        or center_y < BOARD_Y - 30
        or center_y > BOARD_Y + BOARD_HEIGHT + 30
    )

    if outside:
        arrows.remove(flying_arrow)
        flying_arrow = None
        flight_offset_x = 0.0
        flight_offset_y = 0.0

        # 最后一个箭头飞出后才显示通关
        if not arrows:
            result_kind = "clear"
            game_state = RESULT



def restart_level():
    """从关卡数据中恢复当前关卡"""
    global arrows, mistakes_left, selected_arrow
    global collision_arrow, collision_until, game_state
    global result_kind
    global flying_arrow, flight_offset_x, flight_offset_y

    level = LEVELS[current_level - 1]

    arrows = [arrow.copy() for arrow in level["arrows"]]
    mistakes_left = level["mistakes"]
    selected_arrow = None
    collision_arrow = None
    collision_until = 0
    result_kind = None

    # 清除尚未结束的动画
    flying_arrow = None
    flight_offset_x = 0.0
    flight_offset_y = 0.0

    game_state = PLAYING


def draw_restart_button(label="重新开始"):
    """绘制重新开始按钮"""
    if restart_button.collidepoint(pygame.mouse.get_pos()):
        color = (90, 170, 245)
    else:
        color = (70, 150, 230)

    pygame.draw.rect(
        screen,
        color,
        restart_button,
        border_radius=12
    )

    text = button_font.render(
        label,
        True,
        (255, 255, 255)
    )
    screen.blit(
        text,
        text.get_rect(center=restart_button.center)
    )


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


def draw_arrow(arrow, offset_x=0, offset_y=0):
    """根据行、列和方向绘制箭头"""
    row = arrow["row"]
    col = arrow["col"]
    direction = arrow["direction"]

    center_x = int(
        BOARD_X + col * CELL_SIZE + CELL_SIZE // 2 + offset_x
    )
    center_y = int(
        BOARD_Y + row * CELL_SIZE + CELL_SIZE // 2 + offset_y
    )

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

    # 碰撞时短暂显示红色
    current_time = pygame.time.get_ticks()

    if arrow is collision_arrow and current_time < collision_until:
        arrow_color = (220, 70, 70)
    elif arrow is selected_arrow:
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
    """绘制卡片式游戏界面"""
    screen.fill((239, 244, 250))

    # 左上角游戏名称
    heading = info_font.render(
        "一箭又一箭",
        True,
        (45, 65, 90)
    )
    screen.blit(heading, (40, 16))

    # 顶部状态卡片
    cards = [
        ("当前关卡", f"{current_level} / {len(LEVELS)}", (65, 115, 205)),
        ("剩余箭头", str(len(arrows)), (45, 135, 115)),
        ("剩余失误", str(mistakes_left), (205, 80, 85)),
    ]

    card_width = 190
    card_gap = 20
    total_width = card_width * 3 + card_gap * 2
    first_x = (WIDTH - total_width) // 2

    for index, (label, value, value_color) in enumerate(cards):
        card_x = first_x + index * (card_width + card_gap)
        card_rect = pygame.Rect(card_x, 55, card_width, 70)

        # 卡片阴影
        pygame.draw.rect(
            screen,
            (220, 228, 239),
            card_rect.move(0, 4),
            border_radius=14
        )

        pygame.draw.rect(
            screen,
            (255, 255, 255),
            card_rect,
            border_radius=14
        )

        label_image = info_font.render(
            label,
            True,
            (110, 125, 145)
        )
        screen.blit(label_image, (card_x + 16, 62))

        value_image = button_font.render(
            value,
            True,
            value_color
        )
        screen.blit(value_image, (card_x + 16, 86))

    # 棋盘外框
    board_card = pygame.Rect(
        BOARD_X - 10,
        BOARD_Y - 10,
        BOARD_WIDTH + 20,
        BOARD_HEIGHT + 20
    )

    pygame.draw.rect(
        screen,
        (215, 225, 237),
        board_card.move(0, 5),
        border_radius=20
    )

    pygame.draw.rect(
        screen,
        (255, 255, 255),
        board_card,
        border_radius=20
    )

    mouse_pos = pygame.mouse.get_pos()

    # 绘制圆角格子
    for row in range(ROWS):
        for col in range(COLS):
            cell_rect = pygame.Rect(
                BOARD_X + col * CELL_SIZE,
                BOARD_Y + row * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE
            )

            if (row + col) % 2 == 0:
                cell_color = (242, 247, 253)
            else:
                cell_color = (232, 240, 250)

            # 动画期间不显示格子悬停反馈
            if flying_arrow is None:
                if cell_rect.collidepoint(mouse_pos):
                    cell_color = (209, 229, 252)

            pygame.draw.rect(
                screen,
                cell_color,
                cell_rect.inflate(-8, -8),
                border_radius=12
            )

    # 保留原有箭头和动画绘制
    for arrow in arrows:
        if arrow is flying_arrow:
            draw_arrow(arrow, flight_offset_x, flight_offset_y)
        else:
            draw_arrow(arrow)

    draw_restart_button()

def draw_result_screen():
    """根据结果显示失败、本关通关或全部通关"""
    screen.fill((230, 240, 235))

    if result_kind == "failed":
        title_text = "挑战失败"
        message_text = "失误次数已耗尽，重新挑战吧！"
        button_text = "重新开始"
        title_color = (190, 70, 70)

    elif current_level == len(LEVELS):
        title_text = "全部通关！"
        message_text = "你已经清除了所有关卡的箭头"
        button_text = "从第一关再玩"
        title_color = (45, 150, 95)

    else:
        title_text = f"第 {current_level} 关通关"
        message_text = "做得不错，继续挑战下一关吧！"
        button_text = "下一关"
        title_color = (45, 150, 95)

    title = title_font.render(
        title_text,
        True,
        title_color
    )
    screen.blit(
        title,
        title.get_rect(center=(WIDTH // 2, 250))
    )

    message = button_font.render(
        message_text,
        True,
        (45, 65, 85)
    )
    screen.blit(
        message,
        message.get_rect(center=(WIDTH // 2, 350))
    )

    draw_restart_button(button_text)


running = True

while running:
    dt = min(clock.tick(FPS) / 1000.0, 0.05)


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            continue

        # 只处理鼠标左键按下事件
        if event.type != pygame.MOUSEBUTTONDOWN:
            continue

        if event.button != 1:
            continue

        if game_state == START:
            if start_button.collidepoint(event.pos):
                restart_level()

        elif game_state == PLAYING:
            # 点击重新开始按钮
            if restart_button.collidepoint(event.pos):
                restart_level()
                continue

            # 动画期间只允许重新开始
            if flying_arrow is not None:
                continue

            selected_arrow = get_clicked_arrow(event.pos)

            # 点击空白处时不进行箭头处理
            if selected_arrow is None:
                continue

            blocked = is_blocked(selected_arrow, arrows)

            if blocked:
                mistakes_left = max(0, mistakes_left - 1)
                collision_arrow = selected_arrow
                collision_until = pygame.time.get_ticks() + 500

                if mistakes_left == 0:
                    result_kind = "failed"
                    game_state = RESULT
            else:
                # 开始飞出动画，暂时不删除箭头
                flying_arrow = selected_arrow
                flight_offset_x = 0.0
                flight_offset_y = 0.0

            selected_arrow = None

        elif game_state == RESULT:
            if restart_button.collidepoint(event.pos):
                if result_kind == "clear":
                    if current_level < len(LEVELS):
                        current_level += 1
                    else:
                        # 全部通关后从第一关重新玩
                        current_level = 1

                restart_level()

    # 更新成功箭头的飞出动画
    if game_state == PLAYING:
        update_flight(dt)

    # 根据当前状态绘制不同界面
    if game_state == START:
        draw_start_screen()
    elif game_state == PLAYING:
        draw_game_screen()
    elif game_state == RESULT:
        draw_result_screen()

    pygame.display.flip()

pygame.quit()
sys.exit()