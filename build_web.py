import os
import subprocess
import sys
import shutil

def install_requirements():
    """安装必要的依赖"""
    print("正在安装网页构建工具...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pygbag"])

def build_web():
    """构建网页版游戏"""
    print("开始构建网页版游戏...")
    
    # 创建web目录
    if not os.path.exists("web"):
        os.makedirs("web")
    
    # 复制游戏文件到web目录
    shutil.copy("game_test.py", "web/main.py")
    if os.path.exists("web/resources"):
        shutil.rmtree("web/resources")
    shutil.copytree("resources", "web/resources")
    
    # 创建index.html
    with open("web/index.html", "w", encoding="utf-8") as f:
        f.write("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>迷宫冒险</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background-color: #2b2b2b;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        #canvas {
            border: 2px solid #666;
            box-shadow: 0 0 10px rgba(0,0,0,0.5);
        }
        .game-container {
            text-align: center;
        }
        h1 {
            color: #fff;
            font-family: Arial, sans-serif;
            margin-bottom: 20px;
        }
        .controls {
            color: #fff;
            margin-top: 20px;
            font-family: Arial, sans-serif;
        }
    </style>
</head>
<body>
    <div class="game-container">
        <h1>迷宫冒险</h1>
        <canvas id="canvas"></canvas>
        <div class="controls">
            <p>方向键：移动</p>
            <p>空格键：发射火球</p>
            <p>收集钥匙开启门，到达终点获胜！</p>
        </div>
    </div>
    <script src="main.js"></script>
</body>
</html>
        """.strip())
    
    # 使用pygbag构建
    cmd = [
        sys.executable,
        "-m",
        "pygbag",
        "--build",
        "web"
    ]
    
    subprocess.check_call(cmd)
    
    print("\n构建完成！")
    print("网页版游戏文件位于 web/build 目录中")
    print("\n要在本地测试游戏，请运行：")
    print("python -m http.server")
    print("然后在浏览器中访问：http://localhost:8000/web/build")

if __name__ == "__main__":
    try:
        install_requirements()
        build_web()
        input("\n按回车键退出...")
    except Exception as e:
        print(f"\n构建过程中出现错误：{e}")
        input("\n按回车键退出...") 