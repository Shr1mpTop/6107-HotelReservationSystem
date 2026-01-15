# 酒店预订管理系统（HRMS）- CLI版本

## 概述
这是一个基于命令行界面（CLI）的酒店预订管理系统，使用Python开发，SQLite作为数据库。

## 功能特性

### 1. 核心预订管理
- ✓ 实时房间可用性查询
- ✓ 预订创建与信息录入
- ✓ 超售防护机制
- ✓ 自动价格计算
- ✓ 预订修改与取消
- ✓ 邮件通知模拟

### 2. 运营流程
- ✓ 客人信息查询
- ✓ 入住管理
- ✓ 退房与支付记录
- ✓ 房间状态更新

### 3. 安全与配置
- ✓ 用户认证（密码加盐哈希）
- ✓ 基于角色的访问控制（RBAC）
- ✓ 自动登出机制
- ✓ 房型和定价配置
- ✓ 季节性定价规则

### 4. 报表与审计
- ✓ 入住率和收入报表
- ✓ CSV格式导出
- ✓ 操作日志记录
- ✓ 日志查询
- ✓ 数据库备份

## 安装与运行

### 环境要求
- Python 3.8+
- SQLite 3

### 安装步骤
```bash
# 克隆仓库
cd 6107-HotelReservationSystem

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python src/database/init_db.py

# 运行系统
python src/main.py
```

## 默认用户

系统初始化后会创建以下默认用户：

### 管理员账户
- 用户名: `admin`
- 密码: `admin123`
- 权限: 完全访问权限

### 前台员工账户
- 用户名: `frontdesk`
- 密码: `front123`
- 权限: 预订管理、入住/退房操作

### 客房员工账户
- 用户名: `housekeeping`
- 密码: `house123`
- 权限: 房间状态更新

## 项目结构

```
6107-HotelReservationSystem/
├── src/
│   ├── database/
│   │   ├── init_db.py          # 数据库初始化
│   │   ├── schema.sql          # 数据库结构
│   │   └── db_manager.py       # 数据库管理器
│   ├── models/
│   │   ├── user.py             # 用户模型
│   │   ├── room.py             # 房间模型
│   │   ├── reservation.py      # 预订模型
│   │   └── audit_log.py        # 审计日志模型
│   ├── services/
│   │   ├── auth_service.py     # 认证服务
│   │   ├── reservation_service.py  # 预订服务
│   │   ├── room_service.py     # 房间服务
│   │   ├── pricing_service.py  # 定价服务
│   │   ├── report_service.py   # 报表服务
│   │   └── email_service.py    # 邮件服务（模拟）
│   ├── controllers/
│   │   ├── auth_controller.py  # 认证控制器
│   │   ├── reservation_controller.py  # 预订控制器
│   │   ├── operation_controller.py    # 运营控制器
│   │   └── admin_controller.py        # 管理员控制器
│   ├── ui/
│   │   ├── menu.py             # CLI菜单界面
│   │   └── display.py          # 显示工具
│   ├── utils/
│   │   ├── validator.py        # 输入验证
│   │   └── helpers.py          # 辅助函数
│   └── main.py                 # 主程序入口
├── data/
│   └── hrms.db                 # SQLite数据库文件
├── backups/                    # 数据库备份目录
├── logs/                       # 日志文件目录
├── requirements.txt            # Python依赖
└── README.md                   # 项目说明
```

## 使用说明

### 登录系统
启动程序后，使用上述默认账户登录系统。

### 主要操作流程

#### 预订流程（前台员工）
1. 选择"预订管理" → "查询可用房间"
2. 输入入住/退房日期、房型
3. 选择"创建新预订"
4. 输入客人信息
5. 系统自动计算价格并创建预订

#### 入住流程（前台员工）
1. 选择"运营管理" → "办理入住"
2. 输入预订ID或客人信息
3. 确认入住信息，系统更新房间状态为"已占用"

#### 退房流程（前台员工）
1. 选择"运营管理" → "办理退房"
2. 输入预订ID
3. 记录支付信息，系统更新房间状态为"脏污"

#### 房间清洁（客房员工）
1. 选择"房间管理" → "更新房间状态"
2. 将状态从"脏污"改为"清洁"

#### 系统配置（管理员）
1. 选择"系统配置" → "房型管理"
2. 添加/修改房型和基础价格
3. 配置季节性定价规则

#### 报表查询（管理员）
1. 选择"报表管理" → "生成报表"
2. 选择报表类型和日期范围
3. 查看或导出为CSV格式

## 数据库设计

### 核心表结构
- `users`: 用户账户和权限
- `rooms`: 房间信息和状态
- `room_types`: 房型定义和基础价格
- `reservations`: 预订记录
- `payments`: 支付记录
- `seasonal_pricing`: 季节性定价规则
- `audit_logs`: 操作审计日志
- `email_notifications`: 邮件通知记录

## 安全特性
- 密码使用bcrypt加盐哈希存储
- 基于角色的访问控制（RBAC）
- 30分钟无操作自动登出
- 完整的操作审计日志

## 性能要求
- 房间查询响应时间 < 1秒
- 支持20个并发用户
- 年度报表生成 < 3秒

## 开发说明
- Python 3.8+
- 遵循PEP 8编码规范
- 模块化设计，高内聚低耦合
- 完整的错误处理和用户反馈

## 许可证
MIT License
