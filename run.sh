#!/bin/bash

# Hotel Reservation Management System - Quick Start Script

echo "========================================"
echo "Hotel Reservation Management System (HRMS)"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python 3.8或更高版本"
    exit 1
fi

# 检查数据库是否已初始化
if [ ! -f "data/hrms.db" ]; then
    echo "检测到数据库未初始化"
    echo "正在初始化数据库..."
    echo ""
    
    # 检查并安装依赖
    echo "正在检查依赖..."
    pip3 install -q -r requirements.txt
    
    # 初始化数据库
    python3 src/database/init_db.py
    
    if [ $? -ne 0 ]; then
        echo ""
        echo "数据库初始化失败，请检查错误信息"
        exit 1
    fi
    
    echo ""
    echo "数据库初始化完成!"
    echo ""
fi

# 启动系统
echo "正在启动系统..."
echo ""
python3 src/main.py
