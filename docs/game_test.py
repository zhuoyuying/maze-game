import pygame
import sys
import random
import math
import time
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pathfinding.core.diagonal_movement import DiagonalMovement

# 初始化Pygame
pygame.init()
pygame.mixer.init()  # 初始化音频系统

# 定义颜色和游戏参数
BROWN_LIGHT = (139, 69, 19)  # 浅棕色
BROWN_DARK = (101, 67, 33)  # 深棕色
RED_DARK = (139, 0, 0)  # 深红色
GRAY = (120, 120, 140)  # 墙的灰色部分
GRAY_DARK = (80, 80, 100)  # 墙的深灰色部分
WHITE = (255, 255, 255)  # 基础颜色
BLACK = (0, 0, 0)  # 黑色
GREEN_GRASS = (34, 139, 34)  # 草地颜色
GREEN_DARK = (0, 100, 0)  # 深色草地
YELLOW = (255, 255, 0)  # 门的颜色
GOLD = (255, 215, 0)  # 钥匙的颜色
LEAF_GREEN = (50, 205, 50)  # 植物叶子颜色
ORANGE = (255, 140, 0)  # 火焰颜色
HAT_COLOR = (139, 69, 19)  # 帽子颜色
SILVER = (192, 192, 192)  # 剑的颜色
SILVER_LIGHT = (220, 220, 220)  # 剑的高光

# 迷宫参数
CELL_SIZE = 30  # 增加格子的大小
MAZE_WIDTH = 25  # 减少迷宫的宽度，使通道相对更宽
MAZE_HEIGHT = 17  # 减少迷宫的高度，使通道相对更宽

# 创建游戏窗口
WINDOW_WIDTH = MAZE_WIDTH * CELL_SIZE
WINDOW_HEIGHT = MAZE_HEIGHT * CELL_SIZE
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("迷宫游戏")

# 加载音效
try:
    win_sound = pygame.mixer.Sound("resources/win.wav")
    key_sound = pygame.mixer.Sound("resources/key.wav")
    door_sound = pygame.mixer.Sound("resources/door.wav")
    death_sound = pygame.mixer.Sound("resources/death.wav")
    monster_sound = pygame.mixer.Sound("resources/monster.wav")
    # 加载并播放背景音乐
    pygame.mixer.music.load("resources/background.wav")
    pygame.mixer.music.play(-1)  # -1表示循环播放
except Exception as e:
    print(f"Error loading sounds: {e}")
    # 如果找不到音效文件，创建空的音效
    win_sound = pygame.mixer.Sound(bytes(0))
    key_sound = pygame.mixer.Sound(bytes(0))
    door_sound = pygame.mixer.Sound(bytes(0))
    death_sound = pygame.mixer.Sound(bytes(0))
    monster_sound = pygame.mixer.Sound(bytes(0))


# 玩家动画类
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.animation_frame = 0
        self.facing_right = True
        self.walking = False
        self.keys = 0
        self.move_cooldown = 0
        self.move_delay = 6  # 约0.1秒（60FPS下）
        self.is_burning = False
        self.burn_frame = 0
        self.fireballs = []
        self.fireball_cooldown = 0
        self.fireball_delay = 20
        self.sword_angle = 0
        self.sword_swing = False
        self.sword_cooldown = 0
        self.sword_delay = 15
        self.create_animations()

    def create_animations(self):
        self.frames = []
        for i in range(4):  # 4个动画帧
            frame = pygame.Surface((CELL_SIZE - 4, CELL_SIZE - 4), pygame.SRCALPHA)

            # 计算腿部摆动
            leg_swing = math.sin(i * math.pi / 2) * 3
            arm_swing = -math.cos(i * math.pi / 2) * 3  # 手臂摆动与腿部相反

            if not self.is_burning:
                # 帽子
                hat_height = CELL_SIZE // 6
                pygame.draw.rect(frame, HAT_COLOR,
                                 (CELL_SIZE // 3 - 4, CELL_SIZE // 4 - hat_height - 2,
                                  CELL_SIZE // 3 + 8, hat_height))
                # 帽檐
                pygame.draw.rect(frame, HAT_COLOR,
                                 (CELL_SIZE // 4 - 2, CELL_SIZE // 4 - hat_height + 2,
                                  CELL_SIZE // 2 + 4, 3))

                # 头部（带面部特征）
                head_color = (255, 200, 150)  # 肤色
                pygame.draw.circle(frame, head_color,
                                   (CELL_SIZE // 2 - 2, CELL_SIZE // 4), CELL_SIZE // 5)

                # 眼睛
                eye_color = (50, 50, 150)  # 蓝色眼睛
                pygame.draw.circle(frame, eye_color,
                                   (CELL_SIZE // 2 - 6, CELL_SIZE // 4 - 1), 2)
                pygame.draw.circle(frame, eye_color,
                                   (CELL_SIZE // 2 + 2, CELL_SIZE // 4 - 1), 2)

                # 微笑
                smile_rect = (CELL_SIZE // 2 - 4, CELL_SIZE // 4 + 2, 8, 4)
                pygame.draw.arc(frame, (200, 100, 100), smile_rect, 0, math.pi, 1)

                # 身体（带衣服）
                shirt_color = (50, 100, 200)  # 蓝色衬衫
                body_top = CELL_SIZE // 3
                body_height = CELL_SIZE // 2
                pygame.draw.rect(frame, shirt_color,
                                 (CELL_SIZE // 3 - 3, body_top,
                                  CELL_SIZE // 3 + 6, body_height))

                # 裤子
                pants_color = (30, 50, 120)  # 深蓝色裤子
                pygame.draw.rect(frame, pants_color,
                                 (CELL_SIZE // 3 - 2, body_top + body_height,
                                  CELL_SIZE // 3 + 4, CELL_SIZE // 6))

                # 手臂（带动画）
                arm_color = shirt_color
                left_arm_x = CELL_SIZE // 3 - 4
                right_arm_x = CELL_SIZE * 2 // 3
                arm_y = body_top + CELL_SIZE // 6
                # 左手臂
                pygame.draw.line(frame, arm_color,
                                 (left_arm_x, arm_y),
                                 (left_arm_x - 2 + arm_swing, arm_y + 10), 3)
                # 右手臂
                pygame.draw.line(frame, arm_color,
                                 (right_arm_x, arm_y),
                                 (right_arm_x + 2 - arm_swing, arm_y + 10), 3)

                # 腿（带动画）
                leg_color = pants_color
                leg_start_y = body_top + body_height + CELL_SIZE // 6
                # 左腿
                pygame.draw.line(frame, leg_color,
                                 (CELL_SIZE // 3, leg_start_y),
                                 (CELL_SIZE // 3 - 2 - leg_swing, CELL_SIZE - 6), 4)
                # 右腿
                pygame.draw.line(frame, leg_color,
                                 (CELL_SIZE * 2 // 3 - 4, leg_start_y),
                                 (CELL_SIZE * 2 // 3 - 6 + leg_swing, CELL_SIZE - 6), 4)

                # 鞋子
                shoe_color = (40, 40, 40)  # 黑色鞋子
                # 左鞋
                pygame.draw.circle(frame, shoe_color,
                                   (int(CELL_SIZE // 3 - 2 - leg_swing), CELL_SIZE - 5), 3)
                # 右鞋
                pygame.draw.circle(frame, shoe_color,
                                   (int(CELL_SIZE * 2 // 3 - 6 + leg_swing), CELL_SIZE - 5), 3)

                # 剑的位置根据朝向调整
                sword_base_x = CELL_SIZE // 2 + (10 if self.facing_right else -10)
                sword_base_y = CELL_SIZE // 2 + 5  # 稍微往下移动一点

                # 计算剑的摆动角度
                if self.sword_swing:
                    sword_swing = self.sword_angle
                else:
                    sword_swing = 45 if self.facing_right else 135  # 固定的休息角度

                # 剑的长度和宽度
                sword_length = CELL_SIZE * 2 // 3  # 剑的长度为格子大小的2/3
                sword_width = 6  # 剑的宽度

                # 计算剑尖的位置（根据朝向调整角度）
                angle_rad = math.radians(sword_swing)
                sword_tip_x = sword_base_x + math.cos(angle_rad) * sword_length
                sword_tip_y = sword_base_y - math.sin(angle_rad) * sword_length

                # 绘制剑身（带高光效果）
                pygame.draw.line(frame, SILVER,
                                 (sword_base_x, sword_base_y),
                                 (sword_tip_x, sword_tip_y), sword_width)
                # 高光效果
                pygame.draw.line(frame, SILVER_LIGHT,
                                 (sword_base_x + 1, sword_base_y + 1),
                                 (sword_tip_x + 1, sword_tip_y + 1), sword_width // 2)

                # 绘制剑柄
                handle_length = 12
                handle_angle = angle_rad + math.pi / 2  # 垂直于剑身
                handle_x = sword_base_x
                handle_y = sword_base_y
                pygame.draw.line(frame, BROWN_DARK,
                                 (handle_x - math.cos(handle_angle) * handle_length // 2,
                                  handle_y - math.sin(handle_angle) * handle_length // 2),
                                 (handle_x + math.cos(handle_angle) * handle_length // 2,
                                  handle_y + math.sin(handle_angle) * handle_length // 2),
                                 4)
            else:
                # 骷髅头
                pygame.draw.circle(frame, (200, 200, 200),
                                   (CELL_SIZE // 2 - 2, CELL_SIZE // 4), CELL_SIZE // 5)

                # 骷髅眼睛（黑色空洞）
                eye_size = 4
                pygame.draw.rect(frame, BLACK,
                                 (CELL_SIZE // 2 - 8, CELL_SIZE // 4 - 2, eye_size, eye_size))
                pygame.draw.rect(frame, BLACK,
                                 (CELL_SIZE // 2 + 4, CELL_SIZE // 4 - 2, eye_size, eye_size))

                # 骷髅鼻子
                pygame.draw.polygon(frame, BLACK, [
                    (CELL_SIZE // 2 - 2, CELL_SIZE // 4),
                    (CELL_SIZE // 2 + 2, CELL_SIZE // 4),
                    (CELL_SIZE // 2, CELL_SIZE // 4 + 3)
                ])

                # 骷髅牙齿
                teeth_y = CELL_SIZE // 4 + 5
                for tx in range(3):
                    pygame.draw.rect(frame, BLACK,
                                     (CELL_SIZE // 2 - 6 + tx * 4, teeth_y, 3, 3))

                # 火焰效果
                self.burn_frame = (self.burn_frame + 0.2) % 4
                flame_height = 5 + math.sin(self.burn_frame * math.pi / 2) * 3
                for fx in range(-10, 11, 4):
                    flame_x = CELL_SIZE // 2 + fx
                    pygame.draw.line(frame, ORANGE,
                                     (flame_x, CELL_SIZE // 2),
                                     (flame_x + random.randint(-2, 2),
                                      CELL_SIZE // 2 - flame_height),
                                     2)

            self.frames.append(frame)

    def update(self, dx, dy):
        # 更新移动状态
        if dx != 0 or dy != 0:
            if self.move_cooldown <= 0:  # 只在冷却结束时移动
                self.walking = True
                self.animation_frame = (self.animation_frame + 0.2) % 4
                if dx > 0:
                    self.facing_right = True
                elif dx < 0:
                    self.facing_right = False
                self.move_cooldown = self.move_delay
        else:
            self.walking = False
            self.animation_frame = 0

        # 更新冷却时间
        if self.move_cooldown > 0:
            self.move_cooldown -= 1
        if self.fireball_cooldown > 0:
            self.fireball_cooldown -= 1
        if self.sword_cooldown > 0:
            self.sword_cooldown -= 1
            self.sword_swing = True
            if self.facing_right:
                self.sword_angle = 45 + (self.sword_cooldown / self.sword_delay) * 90
            else:
                self.sword_angle = 135 - (self.sword_cooldown / self.sword_delay) * 90
        else:
            self.sword_swing = False

        # 更新火球
        for fireball in self.fireballs[:]:
            fireball.update()
            if fireball.lifetime <= 0:
                self.fireballs.remove(fireball)

    def draw(self, screen, x, y):
        # 绘制玩家动画
        current_frame = self.frames[int(self.animation_frame)]
        if not self.facing_right:
            current_frame = pygame.transform.flip(current_frame, True, False)
        screen.blit(current_frame, (x * CELL_SIZE + 2, y * CELL_SIZE + 2))

        # 独立绘制剑
        if not self.is_burning:
            # 计算剑的基准位置（在玩家手部）
            sword_base_x = x * CELL_SIZE + CELL_SIZE // 2
            sword_base_y = y * CELL_SIZE + CELL_SIZE // 2

            # 根据朝向调整剑的位置
            if self.facing_right:
                sword_base_x += 10
                sword_angle = 45 if not self.sword_swing else self.sword_angle
            else:
                sword_base_x -= 10
                sword_angle = 135 if not self.sword_swing else (180 - self.sword_angle)

            # 剑的尺寸
            sword_length = CELL_SIZE * 2 // 3
            sword_width = 6

            # 计算剑尖的位置
            angle_rad = math.radians(sword_angle)
            sword_tip_x = sword_base_x + math.cos(angle_rad) * sword_length
            sword_tip_y = sword_base_y - math.sin(angle_rad) * sword_length

            # 绘制剑身（带高光效果）
            pygame.draw.line(screen, SILVER,
                             (sword_base_x, sword_base_y),
                             (sword_tip_x, sword_tip_y), sword_width)
            # 高光效果
            pygame.draw.line(screen, SILVER_LIGHT,
                             (sword_base_x + 1, sword_base_y + 1),
                             (sword_tip_x + 1, sword_tip_y + 1), sword_width // 2)

            # 绘制剑柄
            handle_length = 12
            handle_angle = angle_rad + math.pi / 2
            handle_x = sword_base_x
            handle_y = sword_base_y
            pygame.draw.line(screen, BROWN_DARK,
                             (handle_x - math.cos(handle_angle) * handle_length // 2,
                              handle_y - math.sin(handle_angle) * handle_length // 2),
                             (handle_x + math.cos(handle_angle) * handle_length // 2,
                              handle_y + math.sin(handle_angle) * handle_length // 2),
                             4)

    def shoot_fireball(self, direction_x, direction_y):
        if self.fireball_cooldown <= 0 and len(self.fireballs) == 0:  # 确保只有一个火球
            self.fireballs.append(Fireball(self.x, self.y, direction_x, direction_y))
            self.fireball_cooldown = self.fireball_delay
            self.sword_swing = True
            self.sword_cooldown = self.sword_delay


# 烟花粒子类
class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-5, 5)
        self.color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
        self.lifetime = random.randint(30, 60)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2
        self.lifetime -= 1

    def draw(self, screen):
        if self.lifetime > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 2)


# 生成随机迷宫（使用深度优先搜索算法）
maze = [[1 for _ in range(MAZE_WIDTH)] for _ in range(MAZE_HEIGHT)]


def draw_door(surface, x, y):
    # 门框
    pygame.draw.rect(surface, BROWN_DARK,
                     (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # 门面板（带木纹效果）
    door_padding = 3
    pygame.draw.rect(surface, YELLOW,
                     (x * CELL_SIZE + door_padding,
                      y * CELL_SIZE + door_padding,
                      CELL_SIZE - 2 * door_padding,
                      CELL_SIZE - 2 * door_padding))

    # 添加木纹
    for i in range(3):
        line_x = x * CELL_SIZE + door_padding + (CELL_SIZE - 2 * door_padding) // 3 * i
        pygame.draw.line(surface, BROWN_DARK,
                         (line_x, y * CELL_SIZE + door_padding),
                         (line_x, y * CELL_SIZE + CELL_SIZE - door_padding), 1)

    # 门把手
    handle_x = x * CELL_SIZE + CELL_SIZE * 3 / 4
    handle_y = y * CELL_SIZE + CELL_SIZE / 2
    pygame.draw.circle(surface, BROWN_DARK, (int(handle_x), int(handle_y)), 3)
    pygame.draw.circle(surface, BLACK, (int(handle_x), int(handle_y)), 2)


def draw_wall(surface, x, y):
    # 主体墙块（使用棕色系）
    pygame.draw.rect(surface, BROWN_LIGHT,
                     (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # 添加深色边缘（立体效果）
    pygame.draw.rect(surface, BROWN_DARK,
                     (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, 6))  # 顶部阴影
    pygame.draw.rect(surface, RED_DARK,
                     (x * CELL_SIZE, y * CELL_SIZE, 6, CELL_SIZE))  # 左侧阴影

    # 添加纹理
    for i in range(3):
        texture_x = x * CELL_SIZE + random.randint(8, CELL_SIZE - 10)
        texture_y = y * CELL_SIZE + random.randint(8, CELL_SIZE - 10)
        pygame.draw.rect(surface, BROWN_DARK,
                         (texture_x, texture_y, 4, 4))

        texture_x = x * CELL_SIZE + random.randint(8, CELL_SIZE - 10)
        texture_y = y * CELL_SIZE + random.randint(8, CELL_SIZE - 10)
        pygame.draw.rect(surface, RED_DARK,
                         (texture_x, texture_y, 3, 3))


def draw_wall_decoration(surface, x, y):
    # 使用固定的随机种子来减少闪烁
    random.seed(x * 2000 + y)

    # 随机但固定的植物位置
    if random.random() < 0.3:  # 30%的概率添加植物
        start_x = x * CELL_SIZE + 5 + (x % 10)
        start_y = y * CELL_SIZE + 2 + (y % 8)
        points = [(start_x, start_y)]
        for i in range(3):
            points.append((points[-1][0] + (-3 if i % 2 else 3),
                           points[-1][1] + 3))
        pygame.draw.lines(surface, LEAF_GREEN, False, points, 2)

        # 叶子
        leaf_x = points[-1][0]
        leaf_y = points[-1][1]
        pygame.draw.circle(surface, LEAF_GREEN, (leaf_x, leaf_y), 3)


def draw_key(surface, x, y, time_passed):
    # 钥匙的柄
    handle_center_x = x * CELL_SIZE + CELL_SIZE // 2
    handle_center_y = y * CELL_SIZE + CELL_SIZE // 2
    handle_radius = CELL_SIZE // 4

    # 添加浮动效果
    float_offset = math.sin(time_passed * 3) * 2  # 减慢浮动速度
    handle_center_y += float_offset

    # 绘制钥匙的圆形把手
    pygame.draw.circle(surface, GOLD,
                       (handle_center_x, handle_center_y), handle_radius)

    # 绘制钥匙的齿部
    teeth_start_x = handle_center_x + handle_radius
    teeth_width = CELL_SIZE // 3
    teeth_height = CELL_SIZE // 6

    # 绘制钥匙的主体
    pygame.draw.rect(surface, GOLD,
                     (teeth_start_x, handle_center_y - 2,
                      teeth_width, 4))

    # 绘制钥匙的齿
    for i in range(2):
        tooth_x = teeth_start_x + teeth_width * (i + 1) // 3
        pygame.draw.rect(surface, GOLD,
                         (tooth_x, handle_center_y - teeth_height // 2,
                          2, teeth_height))


def create_apple_image():
    img = pygame.Surface((CELL_SIZE - 4, CELL_SIZE - 4), pygame.SRCALPHA)

    # 苹果主体
    pygame.draw.circle(img, (220, 20, 20),  # 鲜艳的红色
                       (CELL_SIZE // 2 - 2, CELL_SIZE // 2),
                       CELL_SIZE // 2 - 4)

    # 苹果高光
    highlight_radius = (CELL_SIZE // 2 - 4) // 2
    pygame.draw.circle(img, (255, 150, 150),
                       (CELL_SIZE // 2 - 5, CELL_SIZE // 2 - 5),
                       highlight_radius)

    # 苹果叶子
    leaf_color = (50, 180, 50)
    leaf_points = [
        (CELL_SIZE // 2 - 2, CELL_SIZE // 4),
        (CELL_SIZE // 2 + 4, CELL_SIZE // 6),
        (CELL_SIZE // 2 - 8, CELL_SIZE // 6)
    ]
    pygame.draw.polygon(img, leaf_color, leaf_points)

    # 苹果茎
    pygame.draw.rect(img, (101, 67, 33),
                     (CELL_SIZE // 2 - 1, CELL_SIZE // 6,
                      2, CELL_SIZE // 8))

    return img


def draw_grass(surface, x, y, time_passed):
    # 绘制基础草地
    pygame.draw.rect(surface, GREEN_GRASS,
                     (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # 添加深色草地纹理（使用固定的随机种子来避免闪烁）
    random.seed(x * 1000 + y)  # 添加这行
    for i in range(3):
        grass_x = x * CELL_SIZE + random.randint(0, CELL_SIZE - 4)
        grass_y = y * CELL_SIZE + random.randint(0, CELL_SIZE - 4)
        pygame.draw.rect(surface, GREEN_DARK,
                         (grass_x, grass_y, 4, 4))

    # 添加随机摆动的小草（大幅降低摆动频率）
    grass_movement = math.sin(time_passed * 0.2) * 2  # 降低到0.2
    base_x = x * CELL_SIZE + (x * 17) % (CELL_SIZE - 10) + 5  # 使用固定位置
    base_y = y * CELL_SIZE + (y * 23) % (CELL_SIZE - 10) + 5
    points = [
        (base_x, base_y),
        (base_x + grass_movement, base_y - 5),
        (base_x + 2, base_y)
    ]
    pygame.draw.lines(surface, LEAF_GREEN, False, points, 2)


def find_path_length(start, end):
    """使用广度优先搜索计算两点之间的最短路径长度"""
    visited = set()
    queue = [(start, 0)]  # (位置, 距离)
    while queue:
        (x, y), dist = queue.pop(0)
        if (x, y) == end:
            return dist
        if (x, y) not in visited:
            visited.add((x, y))
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                new_x, new_y = x + dx, y + dy
                if (0 <= new_x < MAZE_WIDTH and 0 <= new_y < MAZE_HEIGHT and
                        maze[new_y][new_x] != 1):  # 不是墙就可以走
                    queue.append(((new_x, new_y), dist + 1))
    return float('inf')  # 如果找不到路径，返回无穷大


def generate_maze_dfs():
    # 初始化迷宫
    maze = [[1 for _ in range(MAZE_WIDTH)] for _ in range(MAZE_HEIGHT)]

    def carve_path(x, y):
        maze[y][x] = 0
        directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
        random.shuffle(directions)

        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            if (0 <= new_x < MAZE_WIDTH and 0 <= new_y < MAZE_HEIGHT and
                    maze[new_y][new_x] == 1):
                maze[y + dy // 2][x + dx // 2] = 0
                carve_path(new_x, new_y)

    # 从随机位置开始生成迷宫
    start_x = random.randrange(1, MAZE_WIDTH - 1, 2)
    start_y = random.randrange(1, MAZE_HEIGHT - 1, 2)
    carve_path(start_x, start_y)

    # 随机选择起点和终点
    valid_positions = [(x, y) for x in range(MAZE_WIDTH) for y in range(MAZE_HEIGHT)
                       if maze[y][x] == 0]

    start_pos = random.choice(valid_positions)
    valid_positions.remove(start_pos)

    # 确保终点离起点足够远
    end_positions = [(x, y) for x, y in valid_positions
                     if abs(x - start_pos[0]) + abs(y - start_pos[1]) > MAZE_WIDTH // 2]
    end_pos = random.choice(end_positions)

    # 放置4个门和4个钥匙
    doors = []
    keys = []

    # 找到合适的门的位置（必须在墙上，且至少一边有通道）
    wall_positions = []
    for y in range(1, MAZE_HEIGHT - 1):
        for x in range(1, MAZE_WIDTH - 1):
            if maze[y][x] == 1:
                # 检查是否至少有一边是通道
                if ((maze[y - 1][x] == 0 and maze[y + 1][x] == 0) or
                        (maze[y][x - 1] == 0 and maze[y][x + 1] == 0)):
                    wall_positions.append((x, y))

    # 随机选择4个门的位置
    if len(wall_positions) >= 4:
        door_positions = random.sample(wall_positions, 4)
        for x, y in door_positions:
            maze[y][x] = 3  # 3表示门
            doors.append((x, y))

    # 在通道上放置4个钥匙
    path_positions = [(x, y) for x, y in valid_positions
                      if (x, y) != end_pos and maze[y][x] == 0]
    if len(path_positions) >= 4:
        key_positions = random.sample(path_positions, 4)
        for x, y in key_positions:
            maze[y][x] = 2  # 2表示钥匙
            keys.append((x, y))

    return maze, start_pos, end_pos, doors, keys


# 生成迷宫并初始化游戏状态
maze, start_pos, end_pos, doors, keys = generate_maze_dfs()
player = Player(start_pos[0], start_pos[1])
apple_x, apple_y = end_pos

# 创建苹果图形
apple_img = create_apple_image()

# 游戏状态
particles = []
game_won = False
game_over = False
start_time = time.time()
GAME_DURATION = 90  # 增加到90秒

# 游戏主循环
clock = pygame.time.Clock()


# 添加怪物类
class Monster:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.animation_frame = 0
        self.move_cooldown = 0
        self.move_delay = 15  # 每0.25秒移动一次
        self.particles = []
        self.active = True
        self.is_dying = False
        self.death_frame = 0
        self.dead = False  # 新增：标记怪物是否已死亡

    def die(self):
        if not self.is_dying and not self.dead:
            self.is_dying = True
            self.death_frame = 30
            monster_sound.play()

    def update(self, player_x, player_y, maze):
        if self.dead or self.is_dying:
            return

        # 更新移动冷却
        if self.move_cooldown > 0:
            self.move_cooldown -= 1
            return

        # 随机决定是追踪玩家还是随机移动
        if random.random() < 0.7:  # 70%的概率追踪玩家
            # 计算到玩家的方向
            dx = player_x - self.x
            dy = player_y - self.y

            # 选择主要移动方向
            if abs(dx) > abs(dy):
                next_x = self.x + (1 if dx > 0 else -1)
                next_y = self.y
            else:
                next_x = self.x
                next_y = self.y + (1 if dy > 0 else -1)
        else:  # 30%的概率随机移动
            # 随机选择一个方向：上下左右
            direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
            next_x = self.x + direction[0]
            next_y = self.y + direction[1]

        # 检查新位置是否有效
        if (0 <= next_x < MAZE_WIDTH and 0 <= next_y < MAZE_HEIGHT and
                maze[next_y][next_x] != 1 and  # 不是墙
                maze[next_y][next_x] != 3):  # 不是门
            self.x = next_x
            self.y = next_y
            self.move_cooldown = self.move_delay

            # 生成移动粒子效果
            center_x = self.x * CELL_SIZE + CELL_SIZE // 2
            center_y = self.y * CELL_SIZE + CELL_SIZE // 2
            for _ in range(3):
                particle = Particle(
                    center_x + random.randint(-5, 5),
                    center_y + random.randint(-5, 5)
                )
                particle.color = (200, 0, 0)  # 红色粒子
                particle.lifetime = random.randint(10, 20)
                particle.vx = random.uniform(-1, 1)
                particle.vy = random.uniform(-1, 1)
                self.particles.append(particle)

        # 更新粒子效果
        for particle in self.particles[:]:
            particle.update()
            if particle.lifetime <= 0:
                self.particles.remove(particle)

    def reset_position(self, new_pos, maze):
        self.x, self.y = new_pos
        self.particles = []
        # 立即更新路径
        grid = Grid(matrix=[[0 if cell != 1 else 1 for cell in row] for row in maze])
        start = grid.node(self.x, self.y)
        end = grid.node(player.x, player.y)
        finder = AStarFinder(diagonal_movement=DiagonalMovement.never)
        path, _ = finder.find_path(start, end, grid)
        self.path = path

    def draw(self, screen):
        if self.is_dying:
            # 死亡动画
            center_x = self.x * CELL_SIZE + CELL_SIZE // 2
            center_y = self.y * CELL_SIZE + CELL_SIZE // 2

            # 生成爆炸粒子
            if self.death_frame > 0:
                for _ in range(5):
                    angle = random.uniform(0, math.pi * 2)
                    speed = random.uniform(2, 5)
                    particle = Particle(center_x, center_y)
                    particle.vx = math.cos(angle) * speed
                    particle.vy = math.sin(angle) * speed
                    particle.color = (255, random.randint(0, 100), 0)  # 红色系
                    particle.lifetime = random.randint(10, 20)
                    self.particles.append(particle)
                self.death_frame -= 1

            # 如果死亡动画结束，重置位置
            if self.death_frame <= 0:
                monster_pos = find_monster_start_position(maze, (player.x, player.y))
                self.reset_position(monster_pos, maze)
                self.is_dying = False
        else:
            # 正常绘制怪物本体（一个红色的不规则形状）
            center_x = self.x * CELL_SIZE + CELL_SIZE // 2
            center_y = self.y * CELL_SIZE + CELL_SIZE // 2

            # 绘制怪物的核心
            pygame.draw.circle(screen, (200, 0, 0), (center_x, center_y), CELL_SIZE // 3)

            # 绘制触手
            self.animation_frame = (self.animation_frame + 0.1) % (2 * math.pi)
            for i in range(8):
                angle = i * math.pi / 4 + self.animation_frame
                length = CELL_SIZE // 3 + math.sin(angle * 2) * 5
                end_x = center_x + math.cos(angle) * length
                end_y = center_y + math.sin(angle) * length
                pygame.draw.line(screen, (150, 0, 0),
                                 (center_x, center_y),
                                 (end_x, end_y),
                                 3)

            # 绘制眼睛
            eye_color = (255, 255, 0)  # 黄色的眼睛
            eye_radius = CELL_SIZE // 8
            eye_offset = CELL_SIZE // 6
            pygame.draw.circle(screen, eye_color,
                               (center_x - eye_offset, center_y - eye_offset),
                               eye_radius)
            pygame.draw.circle(screen, eye_color,
                               (center_x + eye_offset, center_y - eye_offset),
                               eye_radius)

            # 绘制粒子效果
            for particle in self.particles:
                particle.draw(screen)


# 在游戏初始化部分添加怪物
def find_monster_start_position(maze, player_pos):
    valid_positions = []
    min_distance = MAZE_WIDTH // 3  # 确保怪物和玩家的最小距离

    for y in range(MAZE_HEIGHT):
        for x in range(MAZE_WIDTH):
            if maze[y][x] == 0:  # 如果是通道
                distance = abs(x - player_pos[0]) + abs(y - player_pos[1])
                if distance >= min_distance:
                    valid_positions.append((x, y))

    return random.choice(valid_positions)


# 在游戏状态初始化部分添加
monster_pos = find_monster_start_position(maze, start_pos)
monster = Monster(monster_pos[0], monster_pos[1])


# 添加火球类
class Fireball:
    def __init__(self, x, y, direction_x, direction_y):
        self.x = x * CELL_SIZE + CELL_SIZE // 2
        self.y = y * CELL_SIZE + CELL_SIZE // 2
        self.dx = direction_x * (CELL_SIZE / 20)  # 提高速度，每秒3格
        self.dy = direction_y * (CELL_SIZE / 20)
        self.lifetime = 30  # 减少存在时间，因为速度更快了
        self.size = CELL_SIZE // 3
        self.particles = []

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.lifetime -= 1

        # 火球尾迹效果
        if random.random() < 0.3:  # 减少粒子生成频率
            particle = Particle(self.x, self.y)
            particle.color = (255, random.randint(100, 200), 0)  # 火焰色
            particle.lifetime = random.randint(5, 10)
            particle.vx = random.uniform(-1, 1)
            particle.vy = random.uniform(-1, 1)
            self.particles.append(particle)

        # 更新粒子
        for particle in self.particles[:]:
            particle.update()
            if particle.lifetime <= 0:
                self.particles.remove(particle)

    def draw(self, screen):
        # 绘制火球核心（立体效果）
        pygame.draw.circle(screen, (255, 50, 0), (int(self.x), int(self.y)), self.size)  # 红色底层
        pygame.draw.circle(screen, (255, 150, 0), (int(self.x - 2), int(self.y - 2)), self.size - 2)  # 橙色中层
        pygame.draw.circle(screen, (255, 255, 0), (int(self.x - 4), int(self.y - 4)), self.size - 4)  # 黄色顶层

        # 绘制粒子
        for particle in self.particles:
            particle.draw(screen)

    def get_grid_position(self):
        return (int(self.x // CELL_SIZE), int(self.y // CELL_SIZE))


# 在Particle类后添加新的烟花粒子类
class Firework:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.particles = []
        self.exploded = False
        self.speed = random.uniform(-15, -10)
        self.color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))

    def update(self):
        if not self.exploded:
            self.y += self.speed
            if self.speed < -1:
                self.speed += 0.5
            if self.speed >= -1:
                self.explode()
        else:
            for particle in self.particles[:]:
                particle.update()
                if particle.lifetime <= 0:
                    self.particles.remove(particle)

    def explode(self):
        self.exploded = True
        for _ in range(50):  # 更多的粒子
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(3, 8)
            particle = Particle(self.x, self.y)
            particle.vx = math.cos(angle) * speed
            particle.vy = math.sin(angle) * speed
            particle.color = self.color
            particle.lifetime = random.randint(30, 60)
            self.particles.append(particle)

    def draw(self, screen):
        if not self.exploded:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 3)
        for particle in self.particles:
            particle.draw(screen)

    def is_dead(self):
        return self.exploded and len(self.particles) == 0


# 添加按钮类
class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = (min(color[0] + 30, 255), min(color[1] + 30, 255), min(color[2] + 30, 255))
        self.is_hovered = False

    def draw(self, screen):
        # 绘制按钮阴影
        shadow_rect = self.rect.copy()
        shadow_rect.x += 4
        shadow_rect.y += 4
        pygame.draw.rect(screen, BROWN_DARK, shadow_rect)

        # 绘制主按钮
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)

        # 绘制边框
        pygame.draw.rect(screen, BROWN_DARK, self.rect, 3)

        # 绘制文字
        font = pygame.font.Font(None, 36)
        text = font.render(self.text, True, BROWN_DARK)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # 只响应左键点击
            if self.rect.collidepoint(event.pos):
                return True
        return False


# 修改开始菜单函数
def show_start_menu():
    start_button = Button(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 - 50, 200, 50,
                          "Start Game", BROWN_LIGHT)
    exit_button = Button(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 + 50, 200, 50,
                         "Exit", RED_DARK)

    while True:
        # 绘制背景（草地）
        screen.fill(GREEN_GRASS)

        # 绘制装饰性的墙壁（只在四周）
        for i in range(0, WINDOW_WIDTH, CELL_SIZE):
            draw_wall(screen, i // CELL_SIZE, 0)  # 顶部
            draw_wall(screen, i // CELL_SIZE, MAZE_HEIGHT - 1)  # 底部
        for i in range(0, WINDOW_HEIGHT, CELL_SIZE):
            draw_wall(screen, 0, i // CELL_SIZE)  # 左侧
            draw_wall(screen, MAZE_WIDTH - 1, i // CELL_SIZE)  # 右侧

        # 在草地上添加一些装饰
        for i in range(1, MAZE_WIDTH - 1):
            for j in range(1, MAZE_HEIGHT - 1):
                draw_grass(screen, i, j, pygame.time.get_ticks() / 1000)

        # 绘制标题
        font = pygame.font.Font(None, 74)
        title = font.render("Maze Game", True, BROWN_DARK)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4))
        # 绘制标题阴影
        shadow_text = font.render("Maze Game", True, RED_DARK)
        shadow_rect = title_rect.copy()
        shadow_rect.x += 4
        shadow_rect.y += 4
        screen.blit(shadow_text, shadow_rect)
        screen.blit(title, title_rect)

        # 绘制按钮
        start_button.draw(screen)
        exit_button.draw(screen)

        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if start_button.handle_event(event):
                return True
            if exit_button.handle_event(event):
                return False

        pygame.display.flip()
        clock.tick(60)


# 修改胜利菜单函数
def show_victory_menu():
    restart_button = Button(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 + 50, 200, 50,
                            "Play Again", BROWN_LIGHT)
    exit_button = Button(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 + 150, 200, 50,
                         "Exit", RED_DARK)

    fireworks = []

    while True:
        # 绘制背景
        screen.fill(BROWN_LIGHT)

        # 绘制装饰性的墙壁
        for i in range(0, WINDOW_WIDTH, CELL_SIZE):
            draw_wall(screen, i // CELL_SIZE, 0)
            draw_wall(screen, i // CELL_SIZE, MAZE_HEIGHT - 1)
        for i in range(0, WINDOW_HEIGHT, CELL_SIZE):
            draw_wall(screen, 0, i // CELL_SIZE)
            draw_wall(screen, MAZE_WIDTH - 1, i // CELL_SIZE)

        # 生成新的烟花
        if random.random() < 0.1:
            fireworks.append(Firework(
                random.randint(0, WINDOW_WIDTH),
                WINDOW_HEIGHT + 10
            ))

        # 更新和绘制烟花
        for firework in fireworks[:]:
            firework.update()
            firework.draw(screen)
            if firework.is_dead():
                fireworks.remove(firework)

        # 绘制胜利文字
        font = pygame.font.Font(None, 74)
        text = font.render('You Win!', True, BROWN_DARK)
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4))
        # 绘制文字阴影
        shadow_text = font.render('You Win!', True, RED_DARK)
        shadow_rect = text_rect.copy()
        shadow_rect.x += 4
        shadow_rect.y += 4
        screen.blit(shadow_text, shadow_rect)
        screen.blit(text, text_rect)

        # 绘制按钮
        restart_button.draw(screen)
        exit_button.draw(screen)

        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if restart_button.handle_event(event):
                return True
            if exit_button.handle_event(event):
                return False

        pygame.display.flip()
        clock.tick(60)


# 修改主游戏循环
def main_game():
    global maze, start_pos, end_pos, doors, keys, player, apple_x, apple_y, monster

    # 重置游戏状态
    maze, start_pos, end_pos, doors, keys = generate_maze_dfs()
    player = Player(start_pos[0], start_pos[1])
    apple_x, apple_y = end_pos
    monster_pos = find_monster_start_position(maze, start_pos)
    monster = Monster(monster_pos[0], monster_pos[1])

    game_won = False
    game_over = False
    start_time = time.time()
    fireworks = []

    while True:
        current_time = time.time()
        elapsed_time = int(current_time - start_time)
        remaining_time = max(0, GAME_DURATION - elapsed_time)

        if remaining_time == 0 and not game_won:
            game_over = True

        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over and not game_won:
                    direction_x = 1 if player.facing_right else -1
                    player.shoot_fireball(direction_x, 0)

        if not game_won and not game_over:
            # 获取按键状态
            keys = pygame.key.get_pressed()
            dx = dy = 0

            # 处理移动输入
            if keys[pygame.K_LEFT]:
                dx = -1
            elif keys[pygame.K_RIGHT]:
                dx = 1
            elif keys[pygame.K_UP]:
                dy = -1
            elif keys[pygame.K_DOWN]:
                dy = 1

            # 检查移动的有效性
            if dx != 0 or dy != 0:  # 只在有输入时检查移动
                if player.move_cooldown <= 0:  # 只在冷却结束时移动
                    new_x = player.x + dx
                    new_y = player.y + dy

                    if (0 <= new_x < MAZE_WIDTH and 0 <= new_y < MAZE_HEIGHT):
                        can_move = False
                        if maze[new_y][new_x] == 0 or maze[new_y][new_x] == 2:  # 通道或钥匙
                            can_move = True
                            if maze[new_y][new_x] == 2:  # 拾取钥匙
                                maze[new_y][new_x] = 0
                                player.keys += 1
                                key_sound.play()
                        elif maze[new_y][new_x] == 3 and player.keys > 0:  # 门
                            can_move = True
                            maze[new_y][new_x] = 0
                            player.keys -= 1
                            door_sound.play()

                        if can_move:
                            player.x = new_x
                            player.y = new_y

        # 更新玩家动画
        player.update(dx, dy)

        # 更新怪物
        monster.update(player.x, player.y, maze)

        # 检查怪物是否抓到玩家
        if not monster.dead and not monster.is_dying and monster.x == player.x and monster.y == player.y:
            game_over = True
            player.is_burning = True
            death_sound.play()
            monster_sound.play()

        # 清空屏幕
        screen.fill(WHITE)

        # 绘制迷宫
        for y in range(MAZE_HEIGHT):
            for x in range(MAZE_WIDTH):
                if maze[y][x] == 0:  # 通道
                    draw_grass(screen, x, y, elapsed_time)
                elif maze[y][x] == 1:  # 墙
                    draw_wall(screen, x, y)
                elif maze[y][x] == 2:  # 钥匙
                    draw_grass(screen, x, y, elapsed_time)
                    draw_key(screen, x, y, elapsed_time)
                elif maze[y][x] == 3:  # 门
                    draw_door(screen, x, y)

        # 绘制玩家
        player.draw(screen, player.x, player.y)

        # 绘制苹果
        screen.blit(apple_img, (apple_x * CELL_SIZE + 2, apple_y * CELL_SIZE + 2))

        # 绘制剩余时间
        font = pygame.font.Font(None, 36)
        time_text = font.render(f'Time: {remaining_time}s', True, BLACK)
        screen.blit(time_text, (10, 10))

        # 绘制钥匙数量
        key_text = font.render(f'Keys: {player.keys}', True, GOLD)
        screen.blit(key_text, (10, 40))

        # 绘制怪物
        monster.draw(screen)

        # 更新和检查火球碰撞
        for fireball in player.fireballs[:]:
            fireball.update()
            fireball.draw(screen)
            fx, fy = fireball.get_grid_position()

            # 检查火球是否击中怪物
            if (fx, fy) == (monster.x, monster.y) and not monster.is_dying:
                monster.die()
                player.fireballs.remove(fireball)
                break
            # 检查火球是否击中墙
            if 0 <= fx < MAZE_WIDTH and 0 <= fy < MAZE_HEIGHT:
                if maze[fy][fx] == 1:
                    player.fireballs.remove(fireball)
                    break

        # 检查是否获胜
        if player.x == apple_x and player.y == apple_y and not game_won:
            game_won = True
            win_sound.play()

        if game_won:
            # 生成新的烟花
            if random.random() < 0.1:
                fireworks.append(Firework(
                    random.randint(0, WINDOW_WIDTH),
                    WINDOW_HEIGHT + 10
                ))

            # 更新和绘制烟花
            for firework in fireworks[:]:
                firework.update()
                firework.draw(screen)
                if firework.is_dead():
                    fireworks.remove(firework)

            # 显示获胜文字
            font = pygame.font.Font(None, 74)
            text = font.render('You Win!', True, BROWN_DARK)
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(60)

        if game_over or (game_won and len(fireworks) == 0):
            time.sleep(1)  # 等待1秒
            return True


# 修改主程序入口
def main():
    while True:
        if show_start_menu():
            if not main_game():
                break
        else:
            break
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main() 