# 前端黑盒测试计划

## 测试环境

- **测试日期**: 2026年2月1日
- **前端URL**: http://localhost:3000
- **后端URL**: http://localhost:8000
- **浏览器**: Chrome/Edge（最新版本）
- **测试类型**: 黑盒功能测试

## 测试账号

- **管理员**: admin / admin123
- **前台员工**: receptionist / receptionist123

---

## 测试模块清单

### 1. 登录与认证 (Authentication)

- [x] TC-AUTH-001: 成功登录（管理员）
- [x] TC-AUTH-002: 成功登录（前台员工）
- [x] TC-AUTH-003: 登录失败（错误密码）
- [x] TC-AUTH-004: 登录失败（不存在的用户）
- [x] TC-AUTH-005: 登出功能
- [x] TC-AUTH-006: 未登录访问Dashboard自动跳转

### 2. Dashboard总览 (Dashboard)

- [ ] TC-DASH-001: Dashboard统计数据显示
- [ ] TC-DASH-002: 统计卡片数据正确性
- [ ] TC-DASH-003: 图表显示正常
- [ ] TC-DASH-004: 自动刷新功能（30秒）
- [ ] TC-DASH-005: 不同角色看到的菜单项

### 3. 酒店地图 (Hotel Map)

- [ ] TC-MAP-001: 地图加载所有房间
- [ ] TC-MAP-002: 房间状态颜色显示正确
- [ ] TC-MAP-003: 可用房间显示（绿色）
- [ ] TC-MAP-004: 已预订房间显示（橙色+日历图标）
- [ ] TC-MAP-005: 已入住房间显示（红色）
- [ ] TC-MAP-006: 点击房间显示详情面板
- [ ] TC-MAP-007: 楼层统计数据正确
- [ ] TC-MAP-008: 图例显示完整

### 4. 创建新预订 (New Reservation)

- [ ] TC-RES-001: 搜索可用房间
- [ ] TC-RES-002: 日期验证（入住日期不能早于今天）
- [ ] TC-RES-003: 日期验证（退房日期必须晚于入住日期）
- [ ] TC-RES-004: 选择房间
- [ ] TC-RES-005: 填写客人信息（所有必填字段）
- [ ] TC-RES-006: 邮箱格式验证
- [ ] TC-RES-007: 电话格式验证
- [ ] TC-RES-008: 客人数量验证（不能超过房间容量）
- [ ] TC-RES-009: 特殊要求（可选字段）
- [ ] TC-RES-010: 成功创建预订
- [ ] TC-RES-011: 预订后房间地图状态更新
- [ ] TC-RES-012: 价格计算正确

### 5. 预订搜索与管理 (Reservation Search)

- [ ] TC-SEARCH-001: 按预订ID搜索
- [ ] TC-SEARCH-002: 按客人姓名搜索
- [ ] TC-SEARCH-003: 按电话号码搜索
- [ ] TC-SEARCH-004: 按房间号搜索
- [ ] TC-SEARCH-005: 搜索结果显示
- [ ] TC-SEARCH-006: 查看预订详情（模态框）
- [ ] TC-SEARCH-007: 编辑预订信息
- [ ] TC-SEARCH-008: 保存编辑后的预订
- [ ] TC-SEARCH-009: 取消预订（需确认）
- [ ] TC-SEARCH-010: 取消预订成功

### 6. 今日入住列表 (Today Check-ins)

- [ ] TC-TODAY-001: 显示今日预期入住列表
- [ ] TC-TODAY-002: 卡片显示客人信息
- [ ] TC-TODAY-003: 点击卡片显示详情
- [ ] TC-TODAY-004: 空状态显示

### 7. 当前客人列表 (Current Guests)

- [ ] TC-CURRENT-001: 显示当前在住客人
- [ ] TC-CURRENT-002: 卡片显示客人信息
- [ ] TC-CURRENT-003: 点击卡片显示详情
- [ ] TC-CURRENT-004: 空状态显示

### 8. 办理入住 (Check-in)

- [ ] TC-CHECKIN-001: 搜索预订ID
- [ ] TC-CHECKIN-002: 显示预订详情
- [ ] TC-CHECKIN-003: 状态验证（只能Confirmed状态）
- [ ] TC-CHECKIN-004: 日期验证（不能太早入住）
- [ ] TC-CHECKIN-005: 确认办理入住
- [ ] TC-CHECKIN-006: 入住后房间状态变为Occupied
- [ ] TC-CHECKIN-007: 预订状态变为CheckedIn

### 9. 办理退房 (Check-out)

- [ ] TC-CHECKOUT-001: 搜索预订ID
- [ ] TC-CHECKOUT-002: 显示退房详情
- [ ] TC-CHECKOUT-003: 状态验证（只能CheckedIn状态）
- [ ] TC-CHECKOUT-004: 选择支付方式
- [ ] TC-CHECKOUT-005: 输入支付金额
- [ ] TC-CHECKOUT-006: 找零计算正确
- [ ] TC-CHECKOUT-007: 确认办理退房
- [ ] TC-CHECKOUT-008: 退房后房间状态变为Dirty
- [ ] TC-CHECKOUT-009: 预订状态变为Completed

### 10. 房间列表 (Room List)

- [ ] TC-ROOM-001: 显示所有房间列表
- [ ] TC-ROOM-002: 房间信息显示完整
- [ ] TC-ROOM-003: 房间状态显示正确
- [ ] TC-ROOM-004: 刷新按钮功能

### 11. 房型管理 (Room Types) - 仅管理员

- [ ] TC-TYPE-001: 显示所有房型列表
- [ ] TC-TYPE-002: 添加新房型
- [ ] TC-TYPE-003: 房型信息验证
- [ ] TC-TYPE-004: 编辑房型信息
- [ ] TC-TYPE-005: 保存编辑后的房型

### 12. 季节价格管理 (Seasonal Pricing) - 仅管理员

- [ ] TC-PRICE-001: 显示季节价格列表
- [ ] TC-PRICE-002: 添加季节价格规则
- [ ] TC-PRICE-003: 日期范围验证
- [ ] TC-PRICE-004: 价格类型选择（乘数/固定）
- [ ] TC-PRICE-005: 删除价格规则

### 13. 入住率报表 (Occupancy Report) - 仅管理员

- [ ] TC-REPORT-001: 选择日期范围
- [ ] TC-REPORT-002: 生成报表
- [ ] TC-REPORT-003: 统计卡片显示正确
- [ ] TC-REPORT-004: 数据表格显示完整
- [ ] TC-REPORT-005: 平均入住率计算正确

### 14. 收入报表 (Revenue Report) - 仅管理员

- [ ] TC-REVENUE-001: 选择日期范围
- [ ] TC-REVENUE-002: 生成报表
- [ ] TC-REVENUE-003: 房型收入统计
- [ ] TC-REVENUE-004: 支付方式统计
- [ ] TC-REVENUE-005: 总收入和平均房价

### 15. 审计日志 (Audit Logs) - 仅管理员

- [ ] TC-AUDIT-001: 加载审计日志
- [ ] TC-AUDIT-002: 按操作类型筛选
- [ ] TC-AUDIT-003: 按表名筛选
- [ ] TC-AUDIT-004: 按日期范围筛选
- [ ] TC-AUDIT-005: 显示操作详情

### 16. 备份管理 (Backup Management) - 仅管理员

- [ ] TC-BACKUP-001: 查看备份历史
- [ ] TC-BACKUP-002: 创建新备份
- [ ] TC-BACKUP-003: 备份名称验证
- [ ] TC-BACKUP-004: 备份成功显示

### 17. 系统设置 (Settings)

- [ ] TC-SETTINGS-001: 显示用户信息
- [ ] TC-SETTINGS-002: 修改密码（当前密码错误）
- [ ] TC-SETTINGS-003: 修改密码（新密码不匹配）
- [ ] TC-SETTINGS-004: 修改密码（密码太短）
- [ ] TC-SETTINGS-005: 修改密码成功
- [ ] TC-SETTINGS-006: 系统信息显示

### 18. 权限控制 (Permission Control)

- [ ] TC-PERM-001: 前台员工不能访问报表
- [ ] TC-PERM-002: 前台员工不能访问房型管理
- [ ] TC-PERM-003: 前台员工不能访问季节价格
- [ ] TC-PERM-004: 管理员可以访问所有功能

### 19. UI/UX测试 (User Experience)

- [ ] TC-UX-001: Toast通知显示和自动关闭
- [ ] TC-UX-002: Loading状态显示
- [ ] TC-UX-003: 错误消息显示清晰
- [ ] TC-UX-004: 成功消息显示清晰
- [ ] TC-UX-005: 模态框打开和关闭
- [ ] TC-UX-006: 按钮禁用状态（loading时）
- [ ] TC-UX-007: 响应式布局（移动端）
- [ ] TC-UX-008: 动画效果流畅

### 20. 数据一致性 (Data Consistency)

- [ ] TC-DATA-001: 创建预订后Dashboard数据更新
- [ ] TC-DATA-002: 入住后房间地图更新
- [ ] TC-DATA-003: 退房后房间地图更新
- [ ] TC-DATA-004: 取消预订后房间状态恢复
- [ ] TC-DATA-005: 多个页面数据同步

---

## 测试执行记录

### 测试开始时间: ****\_\_\_****

### 测试执行人: AI Assistant

### 发现的问题 (Issues Found):

#### Issue #1:

- **测试用例**:
- **严重级别**:
- **描述**:
- **重现步骤**:
- **修复状态**:

---

## 测试总结

- **总测试用例数**: 118
- **通过**:
- **失败**:
- **阻塞**:
- **跳过**:
- **通过率**:

### 关键发现

1.
2.
3.

### 建议

1.
2.
3.
