import pygame
import sys
import random
import math
import time
from pathlib import Path

# 初始化Pygame
pygame.init()
pygame.mixer.init()

# 定义颜色和游戏参数
COLORS = {
    'BLUE': (80, 80, 180),
    'BLUE_DARK': (50, 50, 150),
    'BLUE_DARKER': (30, 30, 100),
    'GRAY': (120, 120, 140),
    'GRAY_DARK': (80, 80, 100),
    'WHITE': (255, 255, 255),
    'BLACK': (0, 0, 0),
    'GREEN_GRASS': (34, 139, 34),
    'GREEN_DARK': (0, 100, 0),
    'YELLOW': (255, 255, 0),
    'BROWN': (139, 69, 19),
    'GOLD': (255, 215, 0),
    'LEAF_GREEN': (50, 205, 50),
    'ORANGE': (255, 140, 0),
    'RED': (255, 0, 0)
}

# 游戏设置
CELL_SIZE = 40  # 增大格子尺寸以容纳更多细节
MAZE_WIDTH = 25
MAZE_HEIGHT = 15
PIXEL_SCALE = 2  # 像素缩放比例，使图像更清晰

# 创建游戏窗口
WINDOW_WIDTH = MAZE_WIDTH * CELL_SIZE
WINDOW_HEIGHT = MAZE_HEIGHT * CELL_SIZE
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("像素迷宫冒险")

# 创建资源文件夹
RESOURCE_DIR = Path("resources")
RESOURCE_DIR.mkdir(exist_ok=True)

# 音效和音乐
class AudioManager:
    def __init__(self):
        self.sounds = {}
        self.load_sounds()
        self.load_background_music()
        
    def load_sounds(self):
        sound_files = {
            'key': 'key.wav',
            'door': 'door.wav',
            'win': 'win.wav',
            'monster': 'monster.wav',
            'death': 'death.wav'
        }
        
        for name, file in sound_files.items():
            try:
                self.sounds[name] = pygame.mixer.Sound(str(RESOURCE_DIR / file))
            except:
                print(f"Warning: Could not load sound {file}")
                self.sounds[name] = pygame.mixer.Sound(bytes(0))
    
    def load_background_music(self):
        try:
            pygame.mixer.music.load(str(RESOURCE_DIR / "background.mp3"))
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)  # 循环播放
        except:
            print("Warning: Could not load background music")
    
    def play(self, sound_name):
        if sound_name in self.sounds:
            self.sounds[sound_name].play()

# 怪物类
class Monster:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 0.02  # 移动速度
        self.exact_x = float(x)
        self.exact_y = float(y)
        self.animation_frame = 0
        self.create_animations()
        
    def create_animations(self):
        self.frames = []
        size = CELL_SIZE - 4
        for i in range(4):
            frame = pygame.Surface((size, size), pygame.SRCALPHA)
            
            # 怪物基本形状（像素风格）
            pixels = [
                # 眼睛
                [(size//3, size//3), COLORS['RED']],
                [(size*2//3, size//3), COLORS['RED']],
                # 身体轮廓
                [(size//2, size//2), COLORS['BLUE_DARKER']],
                # 触角
                [(size//4, size//4), COLORS['BLUE_DARK']],
                [(size*3//4, size//4), COLORS['BLUE_DARK']]
            ]
            
            # 添加像素点
            for pos, color in pixels:
                pygame.draw.rect(frame, color, 
                               (pos[0]-1, pos[1]-1, PIXEL_SCALE, PIXEL_SCALE))
            
            # 添加动画效果
            wave = math.sin(i * math.pi/2) * 3
            for y in range(size//2, size, 2):
                x_offset = int(math.sin((y + i*4) * 0.2) * wave)
                pygame.draw.line(frame, COLORS['BLUE_DARKER'],
                               (size//3 + x_offset, y),
                               (size*2//3 + x_offset, y),
                               PIXEL_SCALE)
            
            self.frames.append(frame)
    
    def update(self, player_x, player_y, maze):
        # 计算到玩家的方向
        dx = player_x - self.exact_x
        dy = player_y - self.exact_y
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist > 0:
            # 标准化方向向量
            dx /= dist
            dy /= dist
            
            # 尝试移动
            new_x = self.exact_x + dx * self.speed
            new_y = self.exact_y + dy * self.speed
            
            # 检查碰撞
            cell_x = int(new_x)
            cell_y = int(new_y)
            
            if (0 <= cell_x < MAZE_WIDTH and 
                0 <= cell_y < MAZE_HEIGHT and 
                maze[cell_y][cell_x] != 1):  # 不是墙
                self.exact_x = new_x
                self.exact_y = new_y
                self.x = int(self.exact_x)
                self.y = int(self.exact_y)
        
        # 更新动画
        self.animation_frame = (self.animation_frame + 0.1) % 4
    
    def draw(self, screen):
        frame = self.frames[int(self.animation_frame)]
        screen.blit(frame, 
                   (int(self.exact_x * CELL_SIZE + 2), 
                    int(self.exact_y * CELL_SIZE + 2)))

# 更新玩家类的动画
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.animation_frame = 0
        self.facing_right = True
        self.walking = False
        self.keys = 0
        self.move_cooldown = 0
        self.move_delay = 8
        self.is_burning = False
        self.burn_frame = 0
        self.create_animations()
    
    def create_animations(self):
        self.frames = []
        size = CELL_SIZE - 4
        
        for i in range(4):  # 4个动画帧
            frame = pygame.Surface((size, size), pygame.SRCALPHA)
            
            if not self.is_burning:
                # 像素风格的人物
                pixels = []
                
                # 帽子
                hat_color = COLORS['BROWN']
                for x in range(size//3, size*2//3):
                    pixels.append([(x, size//4-6), hat_color])  # 帽檐
                    pixels.append([(x, size//4-8), hat_color])  # 帽子主体
                
                # 头部
                head_color = (255, 200, 150)
                for y in range(size//4-4, size//3):
                    for x in range(size//3, size*2//3):
                        pixels.append([(x, y), head_color])
                
                # 眼睛
                eye_color = COLORS['BLUE_DARK']
                pixels.append([(size//2-4, size//4-2), eye_color])
                pixels.append([(size//2+2, size//4-2), eye_color])
                
                # 微笑
                smile_color = (200, 100, 100)
                for x in range(-2, 3):
                    pixels.append([(size//2+x, size//4+2), smile_color])
                
                # 身体
                shirt_color = (50, 100, 200)
                leg_swing = math.sin(i * math.pi/2) * 3
                arm_swing = -math.cos(i * math.pi/2) * 3
                
                # 躯干
                for y in range(size//3, size*2//3):
                    for x in range(size//3-2, size*2//3+2):
                        pixels.append([(x, y), shirt_color])
                
                # 手臂
                arm_y = size//2
                for x in range(-4, 5):
                    pixels.append([(size//3+x+arm_swing, arm_y), shirt_color])
                    pixels.append([(size*2//3+x-arm_swing, arm_y), shirt_color])
                
                # 腿部
                pants_color = (30, 50, 120)
                for y in range(size*2//3, size-4):
                    offset = int(leg_swing * (y-size*2//3)/(size//3))
                    pixels.append([(size//2-5+offset, y), pants_color])
                    pixels.append([(size//2+3-offset, y), pants_color])
                
                # 鞋子
                shoe_color = COLORS['BLACK']
                for x in range(-3, 4):
                    pixels.append([(size//2-5+int(leg_swing)+x, size-4), shoe_color])
                    pixels.append([(size//2+3-int(leg_swing)+x, size-4), shoe_color])
                
            else:
                # 骷髅效果
                skull_color = (200, 200, 200)
                fire_colors = [(255, 140, 0), (255, 200, 0), (255, 100, 0)]
                
                # 骷髅头
                for y in range(size//4-4, size//3):
                    for x in range(size//3, size*2//3):
                        pixels.append([(x, y), skull_color])
                
                # 眼窝
                eye_color = COLORS['BLACK']
                for x in range(-2, 3):
                    for y in range(-2, 3):
                        pixels.append([(size//2-4+x, size//4-2+y), eye_color])
                        pixels.append([(size//2+4+x, size//4-2+y), eye_color])
                
                # 火焰效果
                self.burn_frame = (self.burn_frame + 0.2) % len(fire_colors)
                fire_color = fire_colors[int(self.burn_frame)]
                
                for y in range(size//3, size):
                    wave = math.sin((y + i*4) * 0.2) * 3
                    for x in range(-10, 11, 2):
                        if random.random() < 0.7:
                            flame_x = size//2 + x + int(wave)
                            pixels.append([(flame_x, y), fire_color])
            
            # 绘制所有像素
            for pos, color in pixels:
                pygame.draw.rect(frame, color,
                               (pos[0]-1, pos[1]-1, PIXEL_SCALE, PIXEL_SCALE))
            
            self.frames.append(frame)

def create_pixel_apple():
    size = CELL_SIZE - 4
    img = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # 像素风格的苹果
    pixels = []
    
    # 苹果主体
    apple_color = (220, 20, 20)
    highlight_color = (255, 150, 150)
    
    # 创建圆形轮廓
    for y in range(size):
        for x in range(size):
            dx = x - size//2
            dy = y - size//2
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < size//3:
                pixels.append([(x, y), apple_color])
                # 添加高光效果
                if x < size//2 and y < size//2 and dist < size//4:
                    pixels.append([(x, y), highlight_color])
    
    # 叶子
    leaf_color = (50, 180, 50)
    stem_color = (101, 67, 33)
    
    # 茎
    for y in range(size//6-4, size//6):
        pixels.append([(size//2, y), stem_color])
    
    # 叶子像素
    leaf_pixels = [
        (size//2-1, size//6-2),
        (size//2-2, size//6-3),
        (size//2-3, size//6-3),
        (size//2+1, size//6-2),
        (size//2+2, size//6-3),
    ]
    
    for pos in leaf_pixels:
        pixels.append([pos, leaf_color])
    
    # 绘制所有像素
    for pos, color in pixels:
        pygame.draw.rect(img, color,
                        (pos[0]-1, pos[1]-1, PIXEL_SCALE, PIXEL_SCALE))
    
    return img

def create_pixel_wall(x, y):
    surface = pygame.Surface((CELL_SIZE, CELL_SIZE))
    
    # 基础墙面
    pixels = []
    base_color = COLORS['BLUE']
    dark_color = COLORS['BLUE_DARK']
    highlight_color = COLORS['BLUE_LIGHT']
    
    # 创建砖块图案
    for row in range(3):
        for col in range(4):
            # 随机选择颜色变化
            color_variation = random.randint(-20, 20)
            brick_color = (
                max(0, min(255, base_color[0] + color_variation)),
                max(0, min(255, base_color[1] + color_variation)),
                max(0, min(255, base_color[2] + color_variation))
            )
            
            # 砖块主体
            start_x = col * (CELL_SIZE//4)
            start_y = row * (CELL_SIZE//3)
            
            for by in range(CELL_SIZE//3 - 2):
                for bx in range(CELL_SIZE//4 - 2):
                    pixels.append([(start_x + bx, start_y + by), brick_color])
            
            # 添加阴影和高光
            for i in range(CELL_SIZE//4 - 2):
                pixels.append([(start_x + i, start_y + CELL_SIZE//3 - 2), dark_color])
                pixels.append([(start_x + CELL_SIZE//4 - 2, start_y + i), dark_color])
                pixels.append([(start_x, start_y + i), highlight_color])
                pixels.append([(start_x + i, start_y), highlight_color])
    
    # 绘制所有像素
    for pos, color in pixels:
        pygame.draw.rect(surface, color,
                        (pos[0], pos[1], PIXEL_SCALE, PIXEL_SCALE))
    
    return surface

def generate_maze_dfs():
    # 初始化迷宫为全墙
    maze = [[1 for _ in range(MAZE_WIDTH)] for _ in range(MAZE_HEIGHT)]
    
    def get_neighbors(x, y, distance=2):
        neighbors = []
        for dx, dy in [(0, -distance), (distance, 0), (0, distance), (-distance, 0)]:
            new_x, new_y = x + dx, y + dy
            if (0 <= new_x < MAZE_WIDTH and 0 <= new_y < MAZE_HEIGHT and
                    maze[new_y][new_x] == 1):
                neighbors.append((new_x, new_y, dx, dy))
        random.shuffle(neighbors)
        return neighbors
    
    def carve_path(x, y):
        maze[y][x] = 0
        
        neighbors = get_neighbors(x, y)
        for next_x, next_y, dx, dy in neighbors:
            # 在两个格子之间开一条路
            maze[y + dy//2][x + dx//2] = 0
            carve_path(next_x, next_y)
    
    # 从随机点开始生成迷宫
    start_x = random.randrange(1, MAZE_WIDTH-1, 2)
    start_y = random.randrange(1, MAZE_HEIGHT-1, 2)
    carve_path(start_x, start_y)
    
    return maze

def place_items(maze):
    # 获取所有可用的空格
    empty_cells = []
    for y in range(MAZE_HEIGHT):
        for x in range(MAZE_WIDTH):
            if maze[y][x] == 0:
                empty_cells.append((x, y))
    
    if len(empty_cells) < 7:  # 需要至少7个空格（起点、终点、4个钥匙、1个怪物）
        return None, None, None, None
    
    # 随机选择起点和终点
    start_pos = random.choice(empty_cells)
    empty_cells.remove(start_pos)
    
    # 确保终点和起点距离足够远
    end_pos = None
    min_distance = (MAZE_WIDTH + MAZE_HEIGHT) // 3
    
    for pos in empty_cells:
        dist = abs(pos[0] - start_pos[0]) + abs(pos[1] - start_pos[1])
        if dist >= min_distance:
            end_pos = pos
            empty_cells.remove(pos)
            break
    
    if not end_pos:
        return None, None, None, None
    
    # 放置钥匙和门
    keys = []
    doors = []
    
    # 尝试放置4对钥匙和门
    for _ in range(4):
        if len(empty_cells) < 2:
            break
            
        # 放置钥匙
        key_pos = random.choice(empty_cells)
        empty_cells.remove(key_pos)
        keys.append(key_pos)
        maze[key_pos[1]][key_pos[0]] = 2  # 2表示钥匙
        
        # 找到合适的门的位置（必须是墙）
        wall_cells = []
        for y in range(MAZE_HEIGHT):
            for x in range(MAZE_WIDTH):
                if maze[y][x] == 1:
                    # 检查是否至少有一个相邻的通道
                    has_path = False
                    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                        nx, ny = x + dx, y + dy
                        if (0 <= nx < MAZE_WIDTH and 0 <= ny < MAZE_HEIGHT and
                                maze[ny][nx] == 0):
                            has_path = True
                            break
                    if has_path:
                        wall_cells.append((x, y))
        
        if wall_cells:
            door_pos = random.choice(wall_cells)
            doors.append(door_pos)
            maze[door_pos[1]][door_pos[0]] = 3  # 3表示门
    
    # 放置怪物
    monster_positions = []
    num_monsters = min(3, len(empty_cells))  # 最多3个怪物
    for _ in range(num_monsters):
        if empty_cells:
            monster_pos = random.choice(empty_cells)
            empty_cells.remove(monster_pos)
            monster_positions.append(monster_pos)
    
    return start_pos, end_pos, monster_positions, maze

def initialize_game():
    while True:
        maze = generate_maze_dfs()
        result = place_items(maze)
        if result is not None:
            start_pos, end_pos, monster_positions, maze = result
            break
    
    # 创建玩家和怪物
    player = Player(start_pos[0], start_pos[1])
    monsters = [Monster(pos[0], pos[1]) for pos in monster_positions]
    
    # 设置苹果（终点）位置
    apple_x, apple_y = end_pos
    
    return maze, player, monsters, apple_x, apple_y

# 游戏状态
maze, player, monsters, apple_x, apple_y = initialize_game()
particles = []
game_won = False
game_over = False
start_time = time.time()
GAME_DURATION = 60  # 60秒游戏时长

# 创建音频管理器
audio_manager = AudioManager()

# 游戏主循环
clock = pygame.time.Clock()
while True:
    current_time = time.time()
    elapsed_time = int(current_time - start_time)
    remaining_time = max(0, GAME_DURATION - elapsed_time)
    
    if remaining_time == 0 and not game_won:
        game_over = True
        player.is_burning = True
    
    # 处理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    if not game_won and not game_over:
        # 获取按键状态
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_LEFT]:
            dx = -1
        elif keys[pygame.K_RIGHT]:
            dx = 1
        if keys[pygame.K_UP]:
            dy = -1
        elif keys[pygame.K_DOWN]:
            dy = 1
        
        # 更新玩家位置
        if player.move_cooldown <= 0:
            new_x = player.x + dx
            new_y = player.y + dy
            
            if (0 <= new_x < MAZE_WIDTH and 0 <= new_y < MAZE_HEIGHT):
                if maze[new_y][new_x] == 0 or maze[new_y][new_x] == 2:  # 通道或钥匙
                    if maze[new_y][new_x] == 2:  # 拾取钥匙
                        maze[new_y][new_x] = 0
                        player.keys += 1
                        audio_manager.play('key')
                    player.x = new_x
                    player.y = new_y
                elif maze[new_y][new_x] == 3 and player.keys > 0:  # 门
                    maze[new_y][new_x] = 0
                    player.keys -= 1
                    audio_manager.play('door')
                    player.x = new_x
                    player.y = new_y
        
        player.update(dx, dy)
        
        # 更新怪物
        for monster in monsters:
            monster.update(player.x, player.y, maze)
            # 检查是否被怪物抓到
            if (abs(monster.x - player.x) < 0.5 and 
                abs(monster.y - player.y) < 0.5):
                game_over = True
                player.is_burning = True
                audio_manager.play('death')
    
    # 清空屏幕
    screen.fill(COLORS['WHITE'])
    
    # 绘制迷宫
    for y in range(MAZE_HEIGHT):
        for x in range(MAZE_WIDTH):
            if maze[y][x] == 0:  # 通道
                draw_grass(screen, x, y)
            elif maze[y][x] == 1:  # 墙
                wall_surface = create_pixel_wall(x, y)
                screen.blit(wall_surface, (x * CELL_SIZE, y * CELL_SIZE))
            elif maze[y][x] == 2:  # 钥匙
                draw_grass(screen, x, y)  # 先画草地背景
                draw_key(screen, x, y)
            elif maze[y][x] == 3:  # 门
                draw_door(screen, x, y)
    
    # 绘制怪物
    for monster in monsters:
        monster.draw(screen)
    
    # 绘制玩家
    player.draw(screen, player.x, player.y)
    
    # 绘制苹果
    apple_img = create_pixel_apple()
    screen.blit(apple_img, (apple_x * CELL_SIZE + 2, apple_y * CELL_SIZE + 2))
    
    # 绘制UI
    font = pygame.font.Font(None, 36)
    time_text = font.render(f'Time: {remaining_time}s', True, COLORS['BLACK'])
    key_text = font.render(f'Keys: {player.keys}', True, COLORS['GOLD'])
    screen.blit(time_text, (10, 10))
    screen.blit(key_text, (10, 40))
    
    # 检查是否获胜
    if player.x == apple_x and player.y == apple_y and not game_won:
        game_won = True
        audio_manager.play('win')
    
    if game_won:
        # 添加烟花效果
        if random.random() < 0.3:
            x = random.randint(0, WINDOW_WIDTH)
            y = random.randint(0, WINDOW_HEIGHT)
            for _ in range(30):
                particles.append(Particle(x, y))
        
        # 更新和绘制粒子
        for particle in particles[:]:
            particle.update()
            particle.draw(screen)
            if particle.lifetime <= 0:
                particles.remove(particle)
        
        # 显示获胜文字
        font = pygame.font.Font(None, 74)
        text = font.render('You Win!', True, COLORS['BLACK'])
        text_rect = text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
        screen.blit(text, text_rect)
    
    if game_over and not game_won:
        font = pygame.font.Font(None, 74)
        text = font.render('Game Over!', True, COLORS['BLACK'])
        text_rect = text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
        screen.blit(text, text_rect)
    
    # 更新显示
    pygame.display.flip()
    clock.tick(60) 