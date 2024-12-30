import os
import subprocess
import sys

def install_requirements():
    """安装必要的依赖"""
    print("正在安装打包工具...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def build_game():
    """打包游戏"""
    print("开始打包游戏...")
    
    # 构建命令
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",  # 生成单个可执行文件
        "--noconsole",  # 不显示控制台窗口
        "--add-data", f"resources{os.pathsep}resources",  # 添加资源文件夹
        "game_test.py"  # 主程序文件
    ]
    
    # 执行打包命令
    subprocess.check_call(cmd)
    
    print("\n打包完成！")
    print("可执行文件位于 dist 目录中")

if __name__ == "__main__":
    try:
        install_requirements()
        build_game()
        input("\n按回车键退出...")
    except Exception as e:
        print(f"\n打包过程中出现错误：{e}")
        input("\n按回车键退出...") 