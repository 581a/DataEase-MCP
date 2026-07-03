# DataEase MCP Server — 使用说明

## 概述

DataEase MCP Server 是一个基于 Model Context Protocol (MCP) 的服务端程序，使 AI 助手（如 Claude Desktop）能够通过自然语言对话对 DataEase 开源 BI 平台进行操作和管理。

## 支持的 MCP 客户端

- Claude Desktop
- 任何支持 MCP 协议的 AI 客户端

---

## 安装与部署

### 环境要求

- Python >= 3.10
- 网络可访问目标 DataEase 服务器

### 安装步骤

```bash
cd dataease-mcp-server
pip install -e .
```

### 配置

复制环境变量模板并修改：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
DE_BASE_URL=http://10.40.9.211:8100
DE_API_PREFIX=/de2api
DE_USERNAME=admin
DE_PASSWORD=123456!a@Reliance
DE_REQUEST_TIMEOUT=60.0
```

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DE_BASE_URL` | DataEase 服务地址 | `http://10.40.9.211:8100` |
| `DE_API_PREFIX` | API 前缀（分布式版为 `/de2api`，社区版为 `/api`） | `/de2api` |
| `DE_USERNAME` | 管理员账号 | `admin` |
| `DE_PASSWORD` | 管理员密码 | — |
| `DE_REQUEST_TIMEOUT` | 请求超时秒数 | `60.0` |

### 配置 Claude Desktop

在 Claude Desktop 的 `claude_desktop_config.json`（或 `mcp.json`）中添加：

```json
{
  "mcpServers": {
    "dataease": {
      "command": "python",
      "args": ["-m", "dataease_mcp.server"],
      "env": {
        "PYTHONPATH": "/path/to/dataease-mcp-server/src",
        "DE_BASE_URL": "http://10.40.9.211:8100",
        "DE_API_PREFIX": "/de2api",
        "DE_USERNAME": "admin",
        "DE_PASSWORD": "your-password"
      }
    }
  }
}
```

---

## 功能清单（62 个 MCP 工具）

### 仪表板/大屏管理（9 个工具）

| 工具 | 功能 | 参数 |
|------|------|------|
| `list_dashboards` | 查询仪表板/大屏树形列表 | keyword, dv_type |
| `get_dashboard_detail` | 获取仪表板详细配置 | dv_id |
| `create_dashboard` | 创建仪表板/大屏 | name, pid, dv_type |
| `create_folder` | 创建可视化目录 | name, pid |
| `update_dashboard_name` | 重命名仪表板 | dv_id, new_name |
| `delete_dashboard` | 删除仪表板 | dv_id |
| `publish_dashboard` | 发布仪表板 | dv_id |
| `unpublish_dashboard` | 取消发布 | dv_id |
| `copy_dashboard` | 复制仪表板 | source_dv_id, target_pid, new_name |

### 数据集管理（12 个工具）

| 工具 | 功能 | 参数 |
|------|------|------|
| `list_datasets` | 查询数据集树形列表 | keyword, pid |
| `get_dataset_detail` | 获取数据集详情 | dataset_id |
| `get_dataset_fields` | 获取数据集字段列表 | dataset_id |
| `get_dataset_count` | 获取数据总行数 | dataset_id |
| `get_field_enum_values` | 获取字段枚举值 | dataset_id, field_ids |
| `preview_dataset_data` | 预览数据集数据 | dataset_id, limit |
| `preview_sql` | 预览 SQL 查询结果 | datasource_id, sql |
| `create_dataset_folder` | 创建数据集目录 | name, pid |
| `create_dataset_sql` | 创建 SQL 数据集 | name, pid, datasource_id, sql |
| `delete_dataset` | 删除数据集 | dataset_id |
| `rename_dataset` | 重命名数据集 | dataset_id, new_name |
| `export_dataset` | 导出数据集 | dataset_id |

### 数据源管理（12 个工具）

| 工具 | 功能 | 参数 |
|------|------|------|
| `list_datasources` | 查询数据源列表 | keyword |
| `get_datasource_detail` | 获取数据源配置（脱敏） | ds_id |
| `get_datasource_full_config` | 获取完整配置（含原始字段） | ds_id |
| `get_datasource_types` | 支持的数据源类型 | — |
| `get_datasource_tables` | 数据源下表列表 | ds_id |
| `get_api_datasource_fields` | 获取 API 数据源的接口定义和字段列表 | ds_id |
| `get_table_fields` | 表的字段信息 | ds_id, table_name |
| `preview_table_data` | 预览表数据 | ds_id, table_name |
| `test_datasource_connection` | 测试连接 | ds_id |
| `create_datasource_folder` | 创建目录 | name, pid |
| `rename_datasource` | 重命名 | ds_id, new_name |
| `delete_datasource` | 删除数据源 | ds_id |

### 图表管理（7 个工具）

| 工具 | 功能 | 参数 |
|------|------|------|
| `get_chart_detail` | 获取图表配置（默认草稿版本） | chart_id, resource_table |
| `get_chart_data` | 获取图表数据 | chart_id |
| `get_dashboard_views` | 仪表板下视图列表 | dashboard_id |
| `get_chart_fields` | 图表维度/指标字段 | dataset_id, chart_id |
| `get_chart_types` | 获取支持的图表类型列表 | — |
| `save_chart` | 创建或更新图表视图 | title, dashboard_id, dataset_id, chart_type, x_fields, y_fields, chart_id, result_count |
| `update_chart` | 更新已有图表配置 | chart_id, dashboard_id, dataset_id, title, chart_type, x_fields, y_fields, result_count |

### 用户管理（7 个工具）

| 工具 | 功能 | 参数 |
|------|------|------|
| `list_users` | 用户列表（分页） | keyword, page, page_size |
| `get_user_detail` | 用户详情 | user_id |
| `get_current_user` | 当前用户信息 | — |
| `get_user_count` | 用户总数 | — |
| `create_user` | 创建用户 | name, account, email, role_ids, enabled |
| `delete_user` | 删除用户 | user_id |
| `enable_user` | 启用/禁用用户 | user_id, enabled |

### 分享管理（6 个工具）

| 工具 | 功能 | 参数 |
|------|------|------|
| `get_share_status` | 分享状态 | resource_id |
| `enable_share` | 开启分享 | resource_id |
| `disable_share` | 关闭分享 | resource_id |
| `set_share_expiry` | 设置有效期 | resource_id, expiry_timestamp |
| `set_share_password` | 设置密码 | resource_id, password |
| `get_share_detail` | 分享详情 | resource_id |
| `list_shares` | 分享列表 | — |

### 导出中心（4 个工具）

| 工具 | 功能 | 参数 |
|------|------|------|
| `get_export_stats` | 导出任务统计 | — |
| `list_export_tasks` | 导出任务列表 | status, page, page_size |
| `download_export_file` | 获取下载链接 | task_id |
| `retry_export` | 重试导出 | task_id |

### 模板管理（3 个工具）

| 工具 | 功能 | 参数 |
|------|------|------|
| `list_templates` | 本地模板列表 | keyword |
| `get_template_detail` | 模板详情 | template_id |
| `apply_template` | 应用模板创建 | template_id, target_pid, new_name |
| `list_market_templates` | 模板市场 | — |
| `preview_template` | 模板预览 | — |

---

## 使用示例

### 自然语言对话示例

```
用户: 帮我看下有哪些仪表板？
AI: [调用 list_dashboards] 你的 DataEase 中有以下仪表板...

用户: 在仪表板根目录下创建一个叫"销售分析"的仪表板
AI: [调用 create_dashboard(name="销售分析", pid=0, dv_type="dashboard")]

用户: 查看数据集 ID 为 12345 的数据
AI: [调用 preview_dataset_data(dataset_id=12345, limit=20)]

用户: 检查所有数据源的连接状态
AI: [调用 list_datasources → 遍历每个数据源 → test_datasource_connection]

用户: 把仪表板 100 发布并设置分享密码为 "abc123"
AI: [调用 publish_dashboard(100) → enable_share(100) → set_share_password(100, "abc123")]
```

### 创建图表示例

创建图表的标准流程：

```
步骤 1: 获取数据集字段
  get_dataset_fields(dataset_id=1259160149965279232)
  → 返回字段列表，包含 id, name, dataeaseName, groupType, deType

步骤 2: 选择维度和指标字段
  维度字段：筛选 groupType="d" 的字段（如产品大类、批次号等）
  指标字段：筛选 groupType="q" 的字段（如金额、数量等）

步骤 3: 创建图表
  save_chart(
    title="报废金额柱状图",
    dashboard_id=1257692258241744896,   # 已有仪表板 ID
    dataset_id=1259160149965279232,     # 数据集 ID
    chart_type="bar",                   # 柱状图
    x_fields=[{...维度字段...}],         # 从 step1 获取
    y_fields=[{...指标字段...}],         # 从 step1 获取
  )
```

支持的图表类型（部分）：

| 类型标识 | 中文名称 | 类型标识 | 中文名称 |
|----------|----------|----------|----------|
| `bar` | 柱状图 | `line` | 折线图 |
| `bar-group` | 分组柱状图 | `area` | 面积图 |
| `bar-stack` | 堆叠柱状图 | `chart-mix` | 组合图 |
| `pie` | 饼图 | `table-info` | 明细表 |
| `pie-donut` | 环形图 | `table-normal` | 汇总表 |
| `indicator` | 指标卡 | `table-pivot` | 透视表 |
| `gauge` | 仪表盘 | `sankey` | 桑基图 |
| `radar` | 雷达图 | `funnel` | 漏斗图 |
| `scatter` | 散点图 | `waterfall` | 瀑布图 |
| `map` | 地图 | `word-cloud` | 词云图 |

> 完整 46 种图表类型可通过 `get_chart_types` 查询。

### API 数据源字段读取示例

API 类型数据源的字段无法通过 `get_datasource_tables` / `get_table_fields` 读取，
需使用专用工具：

```
步骤 1: 列出所有数据源，找到 API 类型数据源
  list_datasources()
  → 找到 type="API" 的数据源，如 df25_批次报废还原报表 (id=1259150604970889216)

步骤 2: 获取 API 数据源字段
  get_api_datasource_fields(ds_id=1259150604970889216)
  → 返回表名和字段列表：
    {
      "datasource_name": "df25_批次报废还原报表",
      "tables": [
        {
          "name": "df25_批次报废还原报表",
          "fields": [
            {"name": "产品大类", "type": "LONGTEXT"},
            {"name": "报废数量", "type": "DECIMAL"},
            ...
          ]
        }
      ]
    }
```

---

## 技术架构

```
┌─────────────────┐     MCP Protocol     ┌────────────────────┐
│  Claude Desktop  │ ◄──────────────────► │  dataease-mcp      │
│  (MCP Client)    │     stdio/JSON-RPC  │  server (Python)   │
└─────────────────┘                      └────────┬───────────┘
                                                   │
                                          HTTPS + RSA/AES
                                                   │
                                          ┌────────▼───────────┐
                                          │  DataEase Server   │
                                          │  http://10.40...   │
                                          └────────────────────┘
```

### 认证流程

1. `GET /de2api/dekey` → 获取 AES 加密的 RSA 公钥
2. AES-128-CBC 解密 → 得到 RSA 公钥（SPKI DER 格式）
3. 用 RSA 公钥分段加密用户名和密码
4. `POST /de2api/login/localLogin` → 获取 JWT Token
5. 后续请求在 Header 中携带 `X-DE-TOKEN`

---

## MCP 客户端更新指南

当 DataEase MCP Server 代码更新后（如新增工具、修复 bug），客户端通常无需额外操作即可自动获取最新工具列表。以下是不同客户端的更新方式：

### Claude Desktop

Claude Desktop 会在每次启动时重新读取 MCP Server 的工具列表，**无需手动更新**。

如果工具列表未刷新，尝试以下方法：

1. **重启 Claude Desktop**（最可靠的方式）
2. 检查 MCP 连接状态：在 Claude Desktop 中查看 MCP 服务器状态，确认 `dataease` 没有错误
3. 如果连接报错，在终端直接运行 MCP Server 排查：
   ```bash
   cd dataease-mcp-server
   pip install -e .        # 确保安装了最新代码
   python -m dataease_mcp.server
   ```

### 其他 MCP 客户端

大多数 MCP 客户端会在会话开始时调用 `tools/list` 获取工具列表。更新后只需：

1. **重新连接** MCP 服务（断开后再连接）
2. 或**重启客户端应用**

### 验证更新是否生效

在新会话中询问 AI 助手：

```
请列出 DataEase MCP 中所有图表相关的工具
```

如果看到 `save_chart`、`get_chart_types`、`update_chart` 等新增工具，说明更新已生效。

### 配置注意事项

- 如果 `claude_desktop_config.json` 中配置了 `PYTHONPATH`，确保其指向最新的源码目录
- 保留 `.env` 文件中的配置不变，新增工具使用相同的认证凭据

---

## 常见问题

### Q: 登录失败 "RSA key format is not supported"
A: 确保已安装 `cryptography` 库，该库用于加载 DataEase 分布式版使用的 SPKI 格式 RSA 密钥。

### Q: API 返回 401 "token is empty"
A: 检查 `DE_API_PREFIX` 配置。DataEase 分布式版使用 `/de2api`，社区版使用 `/api`。

### Q: 部署的 DataEase 是社区版，如何配置？
A: 将 `.env` 中 `DE_API_PREFIX` 改为 `/api`。
