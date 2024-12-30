import pygame
import os

# 初始化Pygame
pygame.init()

# 创建图标尺寸（必须是正方形）
ICON_SIZE = 256
icon_surface = pygame.Surface((ICON_SIZE, ICON_SIZE), pygame.SRCALPHA)

# 绘制迷宫背景
pygame.draw.rect(icon_surface, (139, 69, 19), (0, 0, ICON_SIZE, ICON_SIZE))  # 棕色背景

# 绘制迷宫墙
wall_color = (101, 67, 33)  # 深棕色
wall_size = ICON_SIZE // 8
for i in range(3):
    for j in range(3):
        if (i + j) % 2 == 0:
            pygame.draw.rect(icon_surface, wall_color,
                           (i * wall_size * 2, j * wall_size * 2,
                            wall_size, wall_size))

# 绘制玩家
player_color = (50, 100, 200)  # 蓝色
player_pos = (ICON_SIZE // 2, ICON_SIZE // 2)
player_size = ICON_SIZE // 4
pygame.draw.circle(icon_surface, player_color, player_pos, player_size)

# 绘制帽子
hat_color = (139, 69, 19)  # 棕色
hat_points = [
    (player_pos[0] - player_size // 2, player_pos[1] - player_size // 2),
    (player_pos[0] + player_size // 2, player_pos[1] - player_size // 2),
    (player_pos[0], player_pos[1] - player_size)
]
pygame.draw.polygon(icon_surface, hat_color, hat_points)

# 绘制剑
sword_color = (192, 192, 192)  # 银色
sword_start = (player_pos[0] + player_size, player_pos[1])
sword_end = (sword_start[0] + player_size, player_pos[1])
pygame.draw.line(icon_surface, sword_color, sword_start, sword_end, 6)

# 确保resources目录存在
if not os.path.exists('resources'):
    os.makedirs('resources')

# 保存为PNG文件
pygame.image.save(icon_surface, 'resources/icon.png')

# 转换为ICO文件
try:
    from PIL import Image
    img = Image.open('resources/icon.png')
    img.save('resources/icon.ico', format='ICO', sizes=[(256, 256)])
    print("成功创建图标文件！")
except ImportError:
    print("需要安装Pillow库来创建ICO文件")
    print("请运行: pip install Pillow") 