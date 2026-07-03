# DataEase MCP Server — 操作标准规范 (SOP)

## 1. 目的与范围

本文档定义了通过 DataEase MCP Server 对 DataEase 平台进行操作的标准流程和规范，确保操作安全、可追溯、不影响生产数据。

### 适用范围
- AI 助手通过 MCP 协议与 DataEase 交互的所有操作
- 管理员和开发者使用 MCP 工具进行 DataEase 管理

---

## 2. 安全原则

### 2.1 读写分离
- **只读操作**（查询、列表、统计）可对任意资源执行
- **写入操作**（创建、修改、删除）仅在新建测试目录下执行

### 2.2 资源隔离
- 所有通过 MCP 创建的测试资源统一放在 `MCP_TEST` 文件夹下
- 严禁修改或删除 `MCP_TEST` 文件夹外的任何已存在资源

### 2.3 操作审批
- 删除数据源、数据集、仪表板等操作前需用户确认
- 创建用户等涉及权限的操作需用户确认

### 2.4 数据安全
- 涉及数据预览时，默认限制返回行数（最多 100 行）
- 不对生产数据集执行写入操作

---

## 3. 标准操作流程

### 3.1 查看资源（只读）

```
步骤 1: 使用 list_dashboards/list_datasets/list_datasources 获取资源树
步骤 2: 使用 get_xxx_detail 获取特定资源详情
步骤 3: 使用 preview_xxx_data 预览数据内容
```

### 3.2 创建仪表板

```
步骤 1: 确认目标目录 ID (pid)，0 为根目录
步骤 2: 如需新目录 → create_folder(name="MCP_TEST", pid=0)
步骤 3: 获取 MCP_TEST 目录的 ID
步骤 4: create_dashboard(name="销售看板", pid=<MCP_TEST_ID>, dv_type="dashboard")
步骤 5: 发布 → publish_dashboard(<dv_id>)
```

### 3.3 从模板创建仪表板

```
步骤 1: list_templates() 查看可用模板
步骤 2: get_template_detail(<template_id>) 查看模板详情
步骤 3: apply_template(template_id, target_pid, "新仪表板名称")
```

### 3.4 创建 SQL 数据集

```
步骤 1: list_datasources() 获取数据源列表
步骤 2: get_datasource_tables(<ds_id>) 查看可用表
步骤 3: get_table_fields(<ds_id>, <table_name>) 查看字段
步骤 4: create_dataset_sql(name="数据集名", pid=<MCP_TEST_ID>, datasource_id=<ds_id>, sql="SELECT ...")
步骤 5: preview_dataset_data(<dataset_id>) 验证数据
```

### 3.5 读取 API 数据源字段

API 类型数据源（type="API"）的字段结构存储在加密配置中，无法通过 `get_datasource_tables` / `get_table_fields` 直接读取，需使用专用工具：

```
步骤 1: list_datasources() 获取数据源树
步骤 2: 识别 type="API" 的数据源，记录其 ds_id
步骤 3: get_api_datasource_fields(ds_id=<ds_id>)
        → 返回完整表名和字段列表（含 name, type, origin_name）

注意: 此工具适用于 get_table_fields 对 API 数据源返回 null 的场景
```

### 3.6 创建图表

创建图表需要：数据集（提供字段）、仪表板（提供容器）、字段绑定（维度+指标）。

```
步骤 1: 获取数据集字段
  get_dataset_fields(dataset_id=<dataset_id>)
  → 记录每个字段的 id, name, dataeaseName, groupType, deType

步骤 2: 选择字段
  维度字段 (x_fields): groupType="d" 的字段
  指标字段 (y_fields): groupType="q" 的字段

步骤 3: 查看支持的图表类型
  get_chart_types()
  → 返回 46 种图表类型标识和中文名称

步骤 4: 创建图表
  save_chart(
    title="图表标题",
    dashboard_id=<dv_id>,
    dataset_id=<dataset_id>,
    chart_type="bar",         # 选择合适的图表类型
    x_fields=[{...}],
    y_fields=[{...}],
  )

步骤 5: 验证
  get_chart_detail(chart_id=<chart_id>)
  → 确认图表配置正确

步骤 6: 查看数据
  get_chart_data(chart_id=<chart_id>)
  → 确认图表数据正确
```

图表示例（调用 save_chart 构建柱状图）：

```python
# 维度字段用 groupType="d"，指标字段用 groupType="q"
x_fields = [{
    "id": 1780368509743,
    "name": "产品大类",
    "dataeaseName": "f_f31b0f1836b8280d",
    "groupType": "d",
    "deType": 0
}]
y_fields = [{
    "id": 1781781621894,
    "name": "实际报废金额",
    "dataeaseName": "f_ac5f9aae09eea59c",
    "groupType": "q",
    "deType": 1,
    "summary": "sum"
}]
```

### 3.7 设置仪表板分享

```
步骤 1: enable_share(<dv_id>) 开启分享
步骤 2: set_share_password(<dv_id>, "密码") 设置密码
步骤 3: set_share_expiry(<dv_id>, <时间戳>) 设置有效期
步骤 4: get_share_detail(<dv_id>) 获取分享链接
```

### 3.8 用户管理

```
创建用户:
  1. create_user(name, account, email, role_ids, enabled=true)
  2. 记录创建的 user_id

删除用户:
  1. list_users() 确认目标用户
  2. 用户确认删除
  3. delete_user(<user_id>)

启用/禁用:
  1. enable_user(<user_id>, true/false)
```

---

## 4. 测试操作规范

### 4.1 测试环境要求
- 所有测试操作在 `MCP_TEST` 独立目录下进行
- 测试完成后清理测试数据

### 4.2 测试前检查
```python
# 1. 确认认证正常
get_current_user() → 返回当前用户信息

# 2. 确认 MCP_TEST 目录存在
list_dashboards(keyword="MCP_TEST")
list_datasets(keyword="MCP_TEST")
```

### 4.3 测试后清理
```python
# 删除 MCP_TEST 目录及其下所有资源
delete_dashboard(<mcp_test_folder_id>)
delete_dataset(<mcp_test_folder_id>)
```

### 4.4 已知限制

| 功能 | 状态 | 说明 |
|------|------|------|
| 数据源创建 | 需前置条件 | 需要目标服务器有可连接的数据库 |
| 图表创建/保存 | ✅ 已可用 | 使用 save_chart 创建，支持 46 种图表类型 |
| API 数据源字段 | ✅ 已可用 | 使用 get_api_datasource_fields 读取 |
| 图表删除 | 需仪表板删除 | 无独立删除 API，可通过删除仪表板级联删除 |
| 数据集 Union 创建 | 未实现 | 多表关联数据集 API 较复杂 |
| 模板市场预览 | 部分可用 | 取决于模板市场服务器状态 |

---

## 5. 错误处理

### 5.1 常见错误及解决

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `token is empty` | 认证失败或 Token 过期 | 检查 .env 配置，重启 MCP Server |
| `RSA key format not supported` | 依赖库问题 | `pip install cryptography` |
| `404 Not Found` | API 前缀配置错误 | 检查 DE_API_PREFIX |
| `406 Not Acceptable` | 数据源连接失败 | 检查数据源配置 |
| `InvocationTargetException` | 参数错误 | 检查请求参数格式 |

### 5.2 调试方法
```bash
# 单独测试认证
python tests/test_auth.py

# 运行完整测试套件
python tests/test_all.py

# 运行深度测试
python tests/test_deep.py
```

---

## 6. 版本兼容性

| DataEase 版本 | API 前缀 | 认证方式 | 测试状态 |
|---------------|----------|----------|----------|
| 2.10.x 分布式版 | `/de2api` | JWT + RSA | ✅ 通过 |
| 2.10.x 社区版 | `/api` | JWT + RSA | 理论兼容 |

---

## 7. 操作日志与审计

建议在实际使用中：
- 记录每次通过 MCP 执行的操作（工具名、参数、结果）
- 对敏感操作（删除、创建用户）进行二次确认
- 定期审查 MCP_TEST 目录，清理过期测试资源
