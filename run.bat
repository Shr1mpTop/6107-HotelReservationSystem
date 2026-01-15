@echo off
REM 酒店预订管理系统 - Windows启动脚本

echo ========================================
echo 酒店预订管理系统 (HRMS)
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.8或更高版本
    pause
    exit /b 1
)

REM 检查数据库是否已初始化
if not exist "data\hrms.db" (
    echo 检测到数据库未初始化
    echo 正在初始化数据库...
    echo.
    
    REM 检查并安装依赖
    echo 正在检查依赖...
    pip install -q -r requirements.txt
    
    REM 初始化数据库
    python src\database\init_db.py
    
    if errorlevel 1 (
        echo.
        echo 数据库初始化失败，请检查错误信息
        pause
        exit /b 1
    )
    
    echo.
    echo 数据库初始化完成!
    echo.
)

REM 启动系统
echo 正在启动系统...
echo.
python src\main.py

pause
