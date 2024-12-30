from cx_Freeze import setup, Executable
import sys
import os

# 依赖项
build_exe_options = {
    "packages": ["pygame", "pathfinding"],
    "include_files": [("resources", "resources")],
    "excludes": []
}

# 基本信息
base = "Win32GUI" if sys.platform == "win32" else None

# 可执行文件
executables = [
    Executable(
        "game_test.py",
        base=base,
        target_name="迷宫冒险",
        icon="resources/icon.ico"
    )
]

# 设置
setup(
    name="迷宫冒险",
    version="1.0",
    description="一个有趣的迷宫游戏",
    options={"build_exe": build_exe_options},
    executables=executables
) 