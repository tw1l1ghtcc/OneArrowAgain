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
    535,
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
    """根据界面结果绘制不同颜色的按钮"""
    hovered = restart_button.collidepoint(pygame.mouse.get_pos())

    if game_state == RESULT and result_kind == "failed":
        color = (225, 100, 115) if hovered else (205, 80, 95)
    elif game_state == RESULT:
        color = (60, 175, 135) if hovered else (40, 150, 110)
    else:
        color = (90, 155, 240) if hovered else (65, 130, 225)

    pygame.draw.rect(
        screen, (200, 213, 229),
        restart_button.move(0, 5),
        border_radius=15
    )

    pygame.draw.rect(
        screen, color, restart_button,
        border_radius=15
    )

    draw_centered_text(
        label, button_font, (255, 255, 255),
        restart_button.center
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

def draw_centered_text(text, font, color, center):
    """以指定位置为中心绘制文字"""
    text_image = font.render(text, True, color)
    screen.blit(
        text_image,
        text_image.get_rect(center=center)
    )


def draw_panel(rect):
    """绘制带阴影的白色圆角卡片"""
    pygame.draw.rect(
        screen, (215, 224, 236),
        rect.move(0, 5),
        border_radius=22
    )
    pygame.draw.rect(
        screen, (255, 255, 255),
        rect,
        border_radius=22
    )


def draw_scene_background(theme="blue"):
    """绘制渐变背景和装饰图形"""
    palettes = {
        "blue": (
            (246, 249, 255),
            (226, 237, 253),
            (202, 220, 244)
        ),
        "success": (
            (245, 252, 248),
            (225, 244, 235),
            (194, 226, 211)
        ),
        "failed": (
            (255, 248, 249),
            (250, 231, 236),
            (236, 204, 213)
        )
    }

    top_color, bottom_color, ornament_color = palettes[theme]

    # 每4像素绘制一条色带，形成渐变
    for y in range(0, HEIGHT, 4):
        ratio = y / (HEIGHT - 1)
        color = tuple(
            int(top_color[i] * (1 - ratio) + bottom_color[i] * ratio)
            for i in range(3)
        )
        pygame.draw.rect(screen, color, (0, y, WIDTH, 4))

    # 背景圆环
    pygame.draw.circle(
        screen, ornament_color, (-20, 100), 145, 3
    )
    pygame.draw.circle(
        screen, ornament_color, (WIDTH - 75, 85), 65, 3
    )
    pygame.draw.circle(
        screen, ornament_color,
        (WIDTH + 15, HEIGHT - 60), 170, 3
    )

    # 背景方向符号
    decorations = [
        ("↑", (90, 255)),
        ("→", (805, 365)),
        ("↓", (120, 590)),
        ("←", (760, 140))
    ]

    for symbol, center in decorations:
        draw_centered_text(
            symbol, button_font, ornament_color, center
        )

    for position in [(145, 160), (780, 520), (80, 430), (720, 620)]:
        pygame.draw.circle(
            screen, ornament_color, position, 5
        )


def draw_start_screen():
    """绘制带图标和玩法卡片的开始界面"""
    draw_scene_background("blue")

    draw_centered_text(
        "一箭又一箭",
        title_font,
        (45, 65, 95),
        (WIDTH // 2, 130)
    )

    draw_centered_text(
        "观察方向 · 判断阻挡 · 清空棋盘",
        info_font,
        (110, 130, 155),
        (WIDTH // 2, 185)
    )

    # 四种方向图标
    icons = [
        ("↑", (225, 235, 255), (65, 115, 205)),
        ("→", (222, 246, 233), (45, 145, 105)),
        ("↓", (255, 237, 215), (205, 135, 55)),
        ("←", (240, 227, 255), (145, 100, 190))
    ]

    for index, (symbol, background, color) in enumerate(icons):
        center = (360 + index * 60, 245)
        pygame.draw.circle(screen, background, center, 28)

        draw_centered_text(
            symbol, button_font, color, center
        )

    # 玩法说明卡片
    draw_panel(pygame.Rect(190, 315, 520, 185))

    draw_centered_text(
        "玩法指南",
        button_font,
        (50, 75, 105),
        (WIDTH // 2, 345)
    )

    instructions = [
        "01   观察方向：箭头只能沿朝向移动",
        "02   点击消除：前方没有箭头才能飞出",
        "03   避开阻挡：每次碰撞扣除一次失误"
    ]

    for index, text in enumerate(instructions):
        draw_centered_text(
            text, info_font, (105, 120, 140),
            (WIDTH // 2, 390 + index * 35)
        )

    # 开始按钮阴影和悬停反馈
    hovered = start_button.collidepoint(pygame.mouse.get_pos())
    color = (90, 155, 240) if hovered else (65, 130, 225)

    pygame.draw.rect(
        screen, (195, 210, 235),
        start_button.move(0, 5),
        border_radius=16
    )
    pygame.draw.rect(
        screen, color, start_button,
        border_radius=16
    )

    draw_centered_text(
        "开始游戏", button_font, (255, 255, 255),
        start_button.center
    )

    draw_centered_text(
        "3 个关卡  ·  鼠标操作  ·  每关 3 次失误机会",
        info_font,
        (125, 140, 160),
        (WIDTH // 2, 650)
    )


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

def draw_all_clear_screen():
    """绘制独立的全部通关庆祝页面"""
    ticks = pygame.time.get_ticks()
    gold = (255, 211, 105)
    pale_gold = (255, 237, 185)

    # 深蓝色渐变背景
    top_color = (18, 28, 52)
    bottom_color = (37, 56, 90)

    for y in range(0, HEIGHT, 4):
        ratio = y / (HEIGHT - 1)
        color = tuple(
            int(top_color[i] * (1 - ratio) + bottom_color[i] * ratio)
            for i in range(3)
        )
        pygame.draw.rect(screen, color, (0, y, WIDTH, 4))

    # 闪烁星点
    for index in range(30):
        x = (index * 173 + 35) % WIDTH
        y = (index * 97 + 25) % HEIGHT
        radius = 2 if (ticks // 500 + index) % 3 == 0 else 1

        pygame.draw.circle(
            screen, (155, 177, 213), (x, y), radius
        )

    # 缓慢飘落的彩纸
    confetti_colors = [
        gold,
        (115, 205, 190),
        (160, 175, 255),
        (255, 155, 175)
    ]

    for index in range(36):
        x = (index * 137 + 41) % WIDTH
        y = (index * 89 + ticks // (15 + index % 6)) % HEIGHT

        pygame.draw.rect(
            screen,
            confetti_colors[index % len(confetti_colors)],
            (x, y, 7, 4),
            border_radius=1
        )

    draw_centered_text(
        "ONE ARROW AGAIN",
        info_font,
        (170, 189, 220),
        (WIDTH // 2, 55)
    )

    # 奖杯背后的圆形光环
    pygame.draw.circle(
        screen, (43, 59, 88), (450, 205), 106
    )
    pygame.draw.circle(
        screen, (111, 104, 83), (450, 205), 106, 2
    )

    # 奖杯两侧把手
    pygame.draw.circle(screen, gold, (391, 180), 25, 8)
    pygame.draw.circle(screen, gold, (509, 180), 25, 8)

    # 奖杯杯身
    pygame.draw.polygon(
        screen,
        gold,
        [
            (392, 145),
            (508, 145),
            (495, 213),
            (474, 236),
            (426, 236),
            (405, 213)
        ]
    )

    # 奖杯立柱和底座
    pygame.draw.rect(
        screen, gold, (444, 233, 12, 35),
        border_radius=3
    )
    pygame.draw.rect(
        screen, gold, (415, 266, 70, 10),
        border_radius=4
    )
    pygame.draw.rect(
        screen, gold, (402, 279, 96, 13),
        border_radius=5
    )

    # 杯身上的星形
    pygame.draw.polygon(
        screen,
        pale_gold,
        [
            (450, 160),
            (456, 174),
            (472, 174),
            (460, 185),
            (465, 200),
            (450, 191),
            (435, 200),
            (440, 185),
            (428, 174),
            (444, 174)
        ]
    )

    draw_centered_text(
        "全关卡通关！",
        title_font,
        gold,
        (WIDTH // 2, 345)
    )
    draw_centered_text(
        "每一箭，都找到了出路",
        button_font,
        (229, 236, 249),
        (WIDTH // 2, 400)
    )

    # 根据关卡数据显示完成信息，不虚构分数或用时
    total_arrows = sum(
        len(level["arrows"]) for level in LEVELS
    )

    badge = pygame.Rect(200, 440, 500, 46)
    pygame.draw.rect(
        screen, (45, 63, 96), badge,
        border_radius=23
    )
    pygame.draw.rect(
        screen, (145, 129, 87), badge,
        width=1,
        border_radius=23
    )

    draw_centered_text(
        f"完成 {len(LEVELS)} 个关卡 · 清空关卡中的 {total_arrows} 枚箭头",
        info_font,
        pale_gold,
        badge.center
    )

    draw_centered_text(
        "再挑战一次，试试不同的消除顺序吧！",
        info_font,
        (175, 192, 218),
        (WIDTH // 2, 535)
    )

    # 使用原来的按钮矩形，原有重玩事件仍然有效
    hovered = restart_button.collidepoint(pygame.mouse.get_pos())
    button_color = (255, 225, 145) if hovered else gold

    pygame.draw.rect(
        screen, (12, 21, 40),
        restart_button.move(0, 5),
        border_radius=15
    )
    pygame.draw.rect(
        screen, button_color, restart_button,
        border_radius=15
    )

    draw_centered_text(
        "从第一关再玩",
        button_font,
        (45, 52, 72),
        restart_button.center
    )


def draw_result_screen():
    """绘制丰富的通关或失败界面"""
    # 最后一关通关时使用独立庆祝页面
    if result_kind == "clear" and current_level == len(LEVELS):
        draw_all_clear_screen()
        return

    failed = result_kind == "failed"
    final_level = current_level == len(LEVELS)

    draw_scene_background("failed" if failed else "success")

    # 结果展示卡片
    draw_panel(pygame.Rect(155, 90, 590, 485))

    draw_centered_text(
        "挑战结算",
        info_font,
        (115, 130, 150),
        (WIDTH // 2, 115)
    )

    # 成功或失败徽章
    center_x = WIDTH // 2
    center_y = 185

    badge_color = (255, 229, 233) if failed else (222, 246, 233)
    symbol_color = (205, 75, 90) if failed else (45, 155, 110)

    pygame.draw.circle(
        screen, badge_color, (center_x, center_y), 46
    )

    if failed:
        pygame.draw.line(
            screen, symbol_color,
            (center_x - 17, center_y - 17),
            (center_x + 17, center_y + 17), 7
        )
        pygame.draw.line(
            screen, symbol_color,
            (center_x + 17, center_y - 17),
            (center_x - 17, center_y + 17), 7
        )
    else:
        pygame.draw.lines(
            screen, symbol_color, False,
            [
                (center_x - 22, center_y),
                (center_x - 6, center_y + 16),
                (center_x + 24, center_y - 18)
            ],
            7
        )

    if failed:
        title = "挑战失败"
        message = "暂时受阻，不代表不能成功"
        tip = "先移走挡路箭头，再尝试被阻挡的箭头。"
        button_text = "重新开始"
    elif final_level:
        title = "全部通关！"
        message = "每一次判断，都让你离成功更近"
        tip = "所有关卡已完成，可以从第一关再次挑战。"
        button_text = "从第一关再玩"
    else:
        title = f"第 {current_level} 关通关"
        message = "漂亮！棋盘已经清空"
        tip = "准备好了吗？下一关还有新的挑战。"
        button_text = "下一关"

    draw_centered_text(
        title, title_font, symbol_color,
        (WIDTH // 2, 270)
    )
    draw_centered_text(
        message, info_font, (100, 115, 135),
        (WIDTH // 2, 320)
    )

    # 展示真实的当前游戏数据
    max_mistakes = LEVELS[current_level - 1]["mistakes"]
    stats = [
        ("当前关卡", f"{current_level} / {len(LEVELS)}"),
        ("剩余箭头", str(len(arrows))),
        ("剩余失误", f"{mistakes_left} / {max_mistakes}")
    ]

    for index, (label, value) in enumerate(stats):
        rect = pygame.Rect(205 + index * 170, 365, 150, 82)

        pygame.draw.rect(
            screen, (242, 246, 251), rect,
            border_radius=12
        )

        draw_centered_text(
            label, info_font, (110, 125, 145),
            (rect.centerx, 387)
        )
        draw_centered_text(
            value, button_font, (50, 70, 95),
            (rect.centerx, 418)
        )

    draw_centered_text(
        tip, info_font, (105, 120, 140),
        (WIDTH // 2, 520)
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