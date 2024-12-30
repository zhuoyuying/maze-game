@echo off
python -m PyInstaller ^
    --onefile ^
    --windowed ^
    --icon resources/icon.ico ^
    --add-data "resources;resources" ^
    --name "迷宫冒险" ^
    game_test.py

if exist dist\迷宫冒险.exe (
    echo 打包成功！可执行文件位于 dist\迷宫冒险.exe
) else (
    echo 打包失败，请检查错误信息
) 