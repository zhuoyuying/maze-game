import os
import shutil
import subprocess
import sys

def create_package():
    # 创建打包目录
    if not os.path.exists('package'):
        os.makedirs('package')
    
    # 复制主游戏文件
    shutil.copy('game_test.py', 'package/game_test.py')
    
    # 复制资源文件夹
    if os.path.exists('package/resources'):
        shutil.rmtree('package/resources')
    shutil.copytree('resources', 'package/resources')
    
    # 创建启动脚本
    with open('package/启动游戏.bat', 'w', encoding='utf-8') as f:
        f.write('@echo off\n')
        f.write('python game_test.py\n')
        f.write('pause\n')
    
    # 创建说明文件
    with open('package/说明.txt', 'w', encoding='utf-8') as f:
        f.write('迷宫冒险游戏\n\n')
        f.write('操作说明：\n')
        f.write('- 使用方向键移动\n')
        f.write('- 空格键发射火球\n')
        f.write('- 收集钥匙开启门\n')
        f.write('- 躲避怪物\n')
        f.write('- 到达终点获胜\n\n')
        f.write('注意：需要安装Python和以下依赖：\n')
        f.write('pip install pygame pathfinding\n')
    
    print('打包完成！文件在 package 目录中。')

if __name__ == '__main__':
    create_package() 