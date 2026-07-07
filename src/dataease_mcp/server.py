import asyncio

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .tools import (
    dashboard,
    dataset,
    datasource,
    chart,
    user,
    share,
    canvas,
    export as export_tools,
    template,
)
from .utils import CHART_TYPE_LIST, safe_int

_ID_PARAMS = {
    "dv_id", "dashboard_id", "dataset_id", "ds_id", "datasource_id",
    "user_id", "resource_id", "chart_id", "view_id", "pid", "target_pid",
    "source_dv_id", "scene_id", "table_id", "expiry_timestamp",
}
_ARRAY_INT_PARAMS = {"field_ids", "role_ids"}

_CHART_TYPE_DESCRIPTIONS = {
    "table-info": "明细表",
    "table-normal": "汇总表",
    "table-pivot": "透视表",
    "t-heatmap": "表格热力图",
    "bar": "柱状图",
    "bar-horizontal": "横向柱状图",
    "bar-group": "分组柱状图",
    "bar-group-stack": "分组堆叠柱状图",
    "bar-stack": "堆叠柱状图",
    "bar-stack-horizontal": "横向堆叠柱状图",
    "percentage-bar-stack": "百分比堆叠柱状图",
    "percentage-bar-stack-horizontal": "横向百分比堆叠柱状图",
    "bar-range": "区间条形图",
    "progress-bar": "进度条",
    "bullet-graph": "子弹图",
    "bidirectional-bar": "双向条形图",
    "line": "折线图",
    "area": "面积图",
    "area-stack": "堆叠面积图",
    "chart-mix": "组合图",
    "chart-mix-stack": "堆叠组合图",
    "chart-mix-group": "分组组合图",
    "chart-mix-dual-line": "双线组合图",
    "pie": "饼图",
    "pie-rose": "玫瑰图",
    "pie-donut": "环形图",
    "pie-donut-rose": "环形玫瑰图",
    "scatter": "散点图",
    "quadrant": "象限图",
    "multi-scatter": "多维散点图",
    "radar": "雷达图",
    "funnel": "漏斗图",
    "word-cloud": "词云图",
    "waterfall": "瀑布图",
    "treemap": "矩形树图",
    "sankey": "桑基图",
    "circle-packing": "圆形打包图",
    "indicator": "指标卡",
    "gauge": "仪表盘",
    "liquid": "水波图",
    "map": "地图",
    "flow-map": "流向地图",
    "symbolic-map": "符号地图",
    "heat-map": "热力地图",
    "bubble-map": "气泡地图",
    "rich-text": "富文本",
}

server = Server("dataease-mcp-server")

TOOLS = [
    Tool(
        name="list_dashboards",
        description="查询 DataEase 仪表板/大屏列表（树形结构）。可选参数 keyword 进行关键词过滤，type 指定类型(dashboard/dataV)。",
        inputSchema={
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "搜索关键词",
                },
                "dv_type": {
                    "type": "string",
                    "description": "仪表板类型: dashboard 或 dataV",
                    "enum": ["dashboard", "dataV"],
                },
            },
        },
    ),
    Tool(
        name="get_dashboard_detail",
        description="获取 DataEase 仪表板/大屏的详细配置信息，包括组件布局、样式、数据源绑定等。",
        inputSchema={
            "type": "object",
            "properties": {
                "dv_id": {
                    "type": ["integer", "string"],
                    "description": "仪表板/大屏的 ID",
                },
            },
            "required": ["dv_id"],
        },
    ),
    Tool(
        name="create_dashboard",
        description="在指定目录下新建一个 DataEase 仪表板或大屏。",
        inputSchema={
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "仪表板名称",
                },
                "pid": {
                    "type": ["integer", "string"],
                    "description": "父目录 ID，0 表示根目录",
                },
                "dv_type": {
                    "type": "string",
                    "description": "类型: dashboard=仪表板, dataV=数据大屏",
                    "enum": ["dashboard", "dataV"],
                },
            },
            "required": ["name", "pid", "dv_type"],
        },
    ),

    Tool(
        name="delete_dashboard",
        description="删除指定的仪表板/大屏。",
        inputSchema={
            "type": "object",
            "properties": {
                "dv_id": {
                    "type": ["integer", "string"],
                    "description": "要删除的仪表板 ID",
                },
            },
            "required": ["dv_id"],
        },
    ),

    Tool(
        name="set_publish_status",
        description="设置仪表板的发布状态。status: 0=取消发布, 1=发布, 2=已保存未发布。",
        inputSchema={
            "type": "object",
            "properties": {
                "dv_id": {
                    "type": ["integer", "string"],
                    "description": "仪表板 ID",
                },
                "status": {
                    "type": "integer",
                    "description": "发布状态: 0=未发布, 1=已发布",
                    "enum": [0, 1],
                },
            },
            "required": ["dv_id", "status"],
        },
    ),
    Tool(
        name="copy_dashboard",
        description="复制一个仪表板/大屏到目标目录。",
        inputSchema={
            "type": "object",
            "properties": {
                "source_dv_id": {
                    "type": ["integer", "string"],
                    "description": "源仪表板 ID",
                },
                "target_pid": {
                    "type": ["integer", "string"],
                    "description": "目标父目录 ID",
                },
                "new_name": {
                    "type": "string",
                    "description": "新名称（可选，不填则自动生成）",
                },
            },
            "required": ["source_dv_id", "target_pid"],
        },
    ),
    Tool(
        name="list_datasets",
        description="查询 DataEase 数据集树形列表。",
        inputSchema={
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "搜索关键词",
                },
                "pid": {
                    "type": ["integer", "string"],
                    "description": "父目录 ID",
                    "default": 0,
                },
            },
        },
    ),

    Tool(
        name="get_dataset_info",
        description="获取数据集的完整信息，包括详细信息、所有字段定义和数据总量。一次调用同时返回 detail+fields+count。",
        inputSchema={
            "type": "object",
            "properties": {
                "dataset_id": {
                    "type": ["integer", "string"],
                    "description": "数据集 ID",
                },
            },
            "required": ["dataset_id"],
        },
    ),
    Tool(
        name="preview_dataset_data",
        description="预览数据集的前 N 行数据。",
        inputSchema={
            "type": "object",
            "properties": {
                "dataset_id": {
                    "type": ["integer", "string"],
                    "description": "数据集 ID",
                },
                "limit": {
                    "type": "integer",
                    "description": "返回行数，默认 100",
                    "default": 100,
                },
            },
            "required": ["dataset_id"],
        },
    ),

    Tool(
        name="create_dataset",
        description="创建数据集目录或 SQL 数据集。node_type=folder 创建目录，node_type=dataset 时需提供 datasource_id 和 sql。",
        inputSchema={
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "名称",
                },
                "pid": {
                    "type": ["integer", "string"],
                    "description": "父目录 ID",
                },
                "node_type": {
                    "type": "string",
                    "description": "节点类型: folder=目录, dataset=SQL数据集",
                    "default": "dataset",
                    "enum": ["folder", "dataset"],
                },
                "datasource_id": {
                    "type": ["integer", "string"],
                    "description": "SQL数据源 ID（node_type=dataset时必填）",
                },
                "sql": {
                    "type": "string",
                    "description": "SQL 查询语句（node_type=dataset时必填）",
                },
            },
            "required": ["name", "pid"],
        },
    ),
    Tool(
        name="delete_dataset",
        description="删除指定的数据集。",
        inputSchema={
            "type": "object",
            "properties": {
                "dataset_id": {
                    "type": ["integer", "string"],
                    "description": "数据集 ID",
                },
            },
            "required": ["dataset_id"],
        },
    ),
    Tool(
        name="rename_dataset",
        description="重命名数据集。",
        inputSchema={
            "type": "object",
            "properties": {
                "dataset_id": {
                    "type": ["integer", "string"],
                    "description": "数据集 ID",
                },
                "new_name": {
                    "type": "string",
                    "description": "新名称",
                },
            },
            "required": ["dataset_id", "new_name"],
        },
    ),
    Tool(
        name="preview_sql",
        description="在指定数据源上预览 SQL 查询的返回结果。",
        inputSchema={
            "type": "object",
            "properties": {
                "datasource_id": {
                    "type": ["integer", "string"],
                    "description": "数据源 ID",
                },
                "sql": {
                    "type": "string",
                    "description": "要预览的 SQL 语句",
                },
            },
            "required": ["datasource_id", "sql"],
        },
    ),
    Tool(
        name="list_datasources",
        description="查询 DataEase 数据源列表（树形结构），包含数据库连接、API 数据源、Excel 文件等。",
        inputSchema={
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "搜索关键词",
                },
            },
        },
    ),
    Tool(
        name="get_datasource_detail",
        description="获取数据源的详细配置信息（密码等敏感信息已隐藏）。",
        inputSchema={
            "type": "object",
            "properties": {
                "ds_id": {
                    "type": ["integer", "string"],
                    "description": "数据源 ID",
                },
                "full": {
                    "type": "boolean",
                    "description": "是否返回完整配置（包含加密密码）",
                    "default": False,
                },
            },
            "required": ["ds_id"],
        },
    ),
    Tool(
        name="get_datasource_tables",
        description="获取指定数据源下的所有数据表/视图列表。",
        inputSchema={
            "type": "object",
            "properties": {
                "ds_id": {
                    "type": ["integer", "string"],
                    "description": "数据源 ID",
                },
            },
            "required": ["ds_id"],
        },
    ),

    Tool(
        name="get_datasource_types",
        description="获取 DataEase 支持的所有数据源类型列表（MySQL、PostgreSQL、Oracle、Excel、API 等）。",
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
    Tool(
        name="test_datasource_connection",
        description="测试数据源连接是否正常。",
        inputSchema={
            "type": "object",
            "properties": {
                "ds_id": {
                    "type": ["integer", "string"],
                    "description": "数据源 ID",
                },
            },
            "required": ["ds_id"],
        },
    ),
    Tool(
        name="preview_table_data",
        description="预览数据表的前几行数据。",
        inputSchema={
            "type": "object",
            "properties": {
                "ds_id": {
                    "type": ["integer", "string"],
                    "description": "数据源 ID",
                },
                "table_name": {
                    "type": "string",
                    "description": "表名",
                },
            },
            "required": ["ds_id", "table_name"],
        },
    ),
    Tool(
        name="delete_datasource",
        description="删除指定数据源。",
        inputSchema={
            "type": "object",
            "properties": {
                "ds_id": {
                    "type": ["integer", "string"],
                    "description": "数据源 ID",
                },
            },
            "required": ["ds_id"],
        },
    ),
    Tool(
        name="list_users",
        description="查询 DataEase 用户列表（分页）。",
        inputSchema={
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "搜索关键词（用户名或邮箱）",
                },
                "page": {
                    "type": "integer",
                    "description": "页码，默认 1",
                    "default": 1,
                },
                "page_size": {
                    "type": "integer",
                    "description": "每页数量，默认 20",
                    "default": 20,
                },
            },
        },
    ),

    Tool(
        name="get_user_info",
        description="获取用户信息。不传 user_id 时返回当前用户信息+系统用户总数；传入 user_id 返回指定用户详情。",
        inputSchema={
            "type": "object",
            "properties": {
                "user_id": {
                    "type": ["integer", "string"],
                    "description": "用户 ID。不传则获取当前用户信息+总数",
                    "default": 0,
                },
            },
        },
    ),
    Tool(
        name="create_user",
        description="在 DataEase 中创建新用户。",
        inputSchema={
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "用户昵称",
                },
                "account": {
                    "type": "string",
                    "description": "登录账号",
                },
                "email": {
                    "type": "string",
                    "description": "邮箱地址",
                },
                "role_ids": {
                    "type": "array",
                    "items": {"type": ["integer", "string"]},
                    "description": "角色 ID 列表",
                },
                "enabled": {
                    "type": "boolean",
                    "description": "是否启用，默认 true",
                    "default": True,
                },
            },
            "required": ["name", "account", "email", "role_ids"],
        },
    ),
    Tool(
        name="delete_user",
        description="删除指定用户。",
        inputSchema={
            "type": "object",
            "properties": {
                "user_id": {
                    "type": ["integer", "string"],
                    "description": "用户 ID",
                },
            },
            "required": ["user_id"],
        },
    ),
    Tool(
        name="enable_user",
        description="启用或禁用用户。",
        inputSchema={
            "type": "object",
            "properties": {
                "user_id": {
                    "type": ["integer", "string"],
                    "description": "用户 ID",
                },
                "enabled": {
                    "type": "boolean",
                    "description": "是否启用",
                },
            },
            "required": ["user_id", "enabled"],
        },
    ),

    Tool(
        name="configure_share",
        description="配置仪表板分享设置。action: toggle=切换分享开关, expiry=设置过期时间, password=设置密码。",
        inputSchema={
            "type": "object",
            "properties": {
                "resource_id": {
                    "type": ["integer", "string"],
                    "description": "仪表板资源 ID",
                },
                "action": {
                    "type": "string",
                    "description": "操作类型: toggle/expiry/password",
                    "enum": ["toggle", "expiry", "password"],
                    "default": "toggle",
                },
                "expiry_timestamp": {
                    "type": ["integer", "string"],
                    "description": "过期时间戳（action=expiry 时使用）",
                },
                "password": {
                    "type": "string",
                    "description": "分享密码（action=password 时使用）",
                },
            },
            "required": ["resource_id"],
        },
    ),
    Tool(
        name="get_share_info",
        description="查询仪表板分享信息。传入 resource_id 返回指定仪表板的分享状态+详情；不传返回所有分享列表。",
        inputSchema={
            "type": "object",
            "properties": {
                "resource_id": {
                    "type": ["integer", "string"],
                    "description": "仪表板资源 ID，不传则返回所有分享列表",
                    "default": 0,
                },
            },
        },
    ),
    Tool(
        name="get_export_info",
        description="获取导出中心的任务统计信息（各状态数量）。",
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),

    Tool(
        name="download_export_file",
        description="获取导出文件的下载链接。",
        inputSchema={
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "导出任务 ID",
                },
            },
            "required": ["task_id"],
        },
    ),
    Tool(
        name="retry_export",
        description="重试失败的导出任务。",
        inputSchema={
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "导出任务 ID",
                },
            },
            "required": ["task_id"],
        },
    ),
    Tool(
        name="list_templates",
        description="查询 DataEase 本地模板列表。",
        inputSchema={
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "搜索关键词",
                },
            },
        },
    ),
    Tool(
        name="get_template_detail",
        description="获取模板的详细配置信息。",
        inputSchema={
            "type": "object",
            "properties": {
                "template_id": {
                    "type": "string",
                    "description": "模板 ID",
                },
                "preview": {
                    "type": "boolean",
                    "description": "获取市场预览信息而非本地模板详情",
                    "default": False,
                },
            },
            "required": ["template_id"],
        },
    ),
    Tool(
        name="apply_template",
        description="使用模板在指定目录新建仪表板。",
        inputSchema={
            "type": "object",
            "properties": {
                "template_id": {
                    "type": "string",
                    "description": "模板 ID",
                },
                "target_pid": {
                    "type": ["integer", "string"],
                    "description": "目标父目录 ID",
                },
                "new_name": {
                    "type": "string",
                    "description": "新仪表板名称",
                },
            },
            "required": ["template_id", "target_pid", "new_name"],
        },
    ),
    Tool(
        name="get_chart_detail",
        description="获取图表视图的详细配置信息。默认从快照版本（snapshot）读取，也可指定 resource_table 参数读取已发布版本（core）。",
        inputSchema={
            "type": "object",
            "properties": {
                "chart_id": {
                    "type": ["integer", "string"],
                    "description": "图表 ID",
                },
                "resource_table": {
                    "type": "string",
                    "description": "资源表: snapshot=草稿版本, core=已发布版本",
                    "default": "snapshot",
                    "enum": ["snapshot", "core"],
                },
            },
            "required": ["chart_id"],
        },
    ),
    Tool(
        name="get_chart_data",
        description="获取图表的数据查询结果。",
        inputSchema={
            "type": "object",
            "properties": {
                "chart_id": {
                    "type": ["integer", "string"],
                    "description": "图表 ID",
                },
            },
            "required": ["chart_id"],
        },
    ),
    Tool(
        name="get_dashboard_views",
        description="获取指定仪表板下所有的图表视图列表。",
        inputSchema={
            "type": "object",
            "properties": {
                "dashboard_id": {
                    "type": ["integer", "string"],
                    "description": "仪表板 ID",
                },
            },
            "required": ["dashboard_id"],
        },
    ),
    Tool(
        name="get_chart_fields",
        description="获取数据集在图表中的维度/指标字段分组。",
        inputSchema={
            "type": "object",
            "properties": {
                "dataset_id": {
                    "type": ["integer", "string"],
                    "description": "数据集 ID",
                },
                "chart_id": {
                    "type": ["integer", "string"],
                    "description": "图表 ID",
                },
            },
            "required": ["dataset_id", "chart_id"],
        },
    ),
    Tool(
        name="update_dashboard_name",
        description="重命名仪表板或大屏。",
        inputSchema={
            "type": "object",
            "properties": {
                "dv_id": {
                    "type": ["integer", "string"],
                    "description": "仪表板 ID",
                },
                "new_name": {
                    "type": "string",
                    "description": "新名称",
                },
            },
            "required": ["dv_id", "new_name"],
        },
    ),

    Tool(
        name="rename_datasource",
        description="重命名数据源。",
        inputSchema={
            "type": "object",
            "properties": {
                "ds_id": {
                    "type": ["integer", "string"],
                    "description": "数据源 ID",
                },
                "new_name": {
                    "type": "string",
                    "description": "新名称",
                },
            },
            "required": ["ds_id", "new_name"],
        },
    ),
    Tool(
        name="get_field_enum_values",
        description="获取数据集字段的枚举值（用于过滤组件下拉选项）。",
        inputSchema={
            "type": "object",
            "properties": {
                "dataset_id": {
                    "type": ["integer", "string"],
                    "description": "数据集 ID",
                },
                "field_ids": {
                    "type": "array",
                    "items": {"type": ["integer", "string"]},
                    "description": "字段 ID 列表",
                },
            },
            "required": ["dataset_id", "field_ids"],
        },
    ),

    Tool(
        name="create_datasource_folder",
        description="在数据源目录下创建文件夹。",
        inputSchema={
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "文件夹名称",
                },
                "pid": {
                    "type": ["integer", "string"],
                    "description": "父目录 ID，默认 0",
                    "default": 0,
                },
            },
            "required": ["name"],
        },
    ),

    Tool(
        name="save_chart",
        description="在指定仪表板中创建或更新一个图表视图。需要提供仪表板 ID、数据集 ID、图表类型以及维度和指标字段列表。字段需从 get_dataset_fields 获取，每个字段至少需要 id、name、dataeaseName、groupType、deType 属性。",
        inputSchema={
            "type": "object",
            "properties": {
                "dashboard_id": {
                    "type": ["integer", "string"],
                    "description": "仪表板（场景）ID",
                },
                "dataset_id": {
                    "type": ["integer", "string"],
                    "description": "数据集 ID，图表将绑定到此数据集",
                },
                "title": {
                    "type": "string",
                    "description": "图表标题",
                },
                "chart_type": {
                    "type": "string",
                    "description": "图表类型：bar=柱状图, line=折线图, pie=饼图, table-info=明细表, table-normal=汇总表, indicator=指标卡, gauge=仪表盘, liquid=水波图, area=面积图, scatter=散点图, funnel=漏斗图, radar=雷达图, word-cloud=词云图, treemap=矩形树图, map=地图 等",
                },
                "x_fields": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "维度（横轴/分组）字段列表。每个字段需包含: id, name, dataeaseName, groupType(必须为\"d\"), deType。可选: summary, sort, filter",
                },
                "y_fields": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "指标（纵轴/数值）字段列表。每个字段需包含: id, name, dataeaseName, groupType(必须为\"q\"), deType。可选: summary(sum/count/avg/max/min), sort, filter",
                },
                "y_fields_ext": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "【组合图专用】右值轴指标字段列表。仅 chart-mix 类型使用。格式同 y_fields",
                    "default": [],
                },
                "chart_id": {
                    "type": ["integer", "string"],
                    "description": "图表 ID（更新时使用）。不填则自动生成新的图表 ID",
                    "default": 0,
                },
                "custom_attr": {
                    "type": "object",
                    "description": "图表自定义属性（样式配置），包括 basicStyle、label、tooltip 等。不填则自动使用默认值或保留已有值",
                    "default": None,
                },
                "custom_style": {
                    "type": "object",
                    "description": "图表自定义样式（轴配置），包括 yAxis、yAxisExt 等。不填则自动使用默认值或保留已有值",
                    "default": None,
                },
                "result_count": {
                    "type": "integer",
                    "description": "结果展示条数限制，默认 1000",
                    "default": 1000,
                },
            },
            "required": ["dashboard_id", "dataset_id", "title", "chart_type", "x_fields", "y_fields"],
        },
    ),
    Tool(
        name="get_chart_types",
        description="获取 DataEase 支持的所有图表类型列表，包含类型标识和中文名称。",
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
    Tool(
        name="update_chart",
        description="更新仪表板中已有的图表配置（修改图表类型、字段绑定、样式等）。需要提供现有图表的 ID。",
        inputSchema={
            "type": "object",
            "properties": {
                "chart_id": {
                    "type": ["integer", "string"],
                    "description": "要更新的图表视图 ID",
                },
                "dashboard_id": {
                    "type": ["integer", "string"],
                    "description": "仪表板 ID",
                },
                "dataset_id": {
                    "type": ["integer", "string"],
                    "description": "数据集 ID",
                },
                "title": {
                    "type": "string",
                    "description": "图表标题",
                },
                "chart_type": {
                    "type": "string",
                    "description": "图表类型",
                },
                "x_fields": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "维度字段列表",
                },
                "y_fields": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "指标字段列表",
                },
                "result_count": {
                    "type": "integer",
                    "description": "结果展示条数，默认 1000",
                    "default": 1000,
                },
            },
            "required": ["chart_id", "dashboard_id", "dataset_id", "title", "chart_type", "x_fields", "y_fields"],
        },
    ),
    Tool(
        name="get_dashboard_layout",
        description="获取仪表板的画布布局，列出所有组件（图表视图、筛选器、分组等）及其位置和大小。",
        inputSchema={
            "type": "object",
            "properties": {
                "dv_id": {
                    "type": ["integer", "string"],
                    "description": "仪表板 ID",
                },
            },
            "required": ["dv_id"],
        },
    ),
    Tool(
        name="update_component_position",
        description="更新仪表板上某个组件的坐标位置和尺寸大小。",
        inputSchema={
            "type": "object",
            "properties": {
                "dv_id": {
                    "type": ["integer", "string"],
                    "description": "仪表板 ID",
                },
                "component_id": {
                    "type": "string",
                    "description": "组件 ID",
                },
                "x": {
                    "type": "integer",
                    "description": "水平坐标（栅格单位）",
                },
                "y": {
                    "type": "integer",
                    "description": "垂直坐标（栅格单位）",
                },
                "size_x": {
                    "type": "integer",
                    "description": "组件宽度（栅格单位），0 表示不修改",
                    "default": 0,
                },
                "size_y": {
                    "type": "integer",
                    "description": "组件高度（栅格单位），0 表示不修改",
                    "default": 0,
                },
            },
            "required": ["dv_id", "component_id", "x", "y"],
        },
    ),
    Tool(
        name="add_chart_to_canvas",
        description="将已有的图表视图添加到仪表板画布上，指定位置和大小。应先调用 save_chart 创建图表再添加。",
        inputSchema={
            "type": "object",
            "properties": {
                "dv_id": {
                    "type": ["integer", "string"],
                    "description": "仪表板 ID",
                },
                "chart_id": {
                    "type": ["integer", "string"],
                    "description": "图表 ID（由 save_chart 创建时返回）",
                },
                "chart_title": {
                    "type": "string",
                    "description": "图表标题",
                },
                "chart_type": {
                    "type": "string",
                    "description": "图表类型（如 bar, line, pie 等）",
                },
                "x": {
                    "type": "integer",
                    "description": "水平位置",
                    "default": 1,
                },
                "y": {
                    "type": "integer",
                    "description": "垂直位置",
                    "default": 1,
                },
                "size_x": {
                    "type": "integer",
                    "description": "宽度",
                    "default": 36,
                },
                "size_y": {
                    "type": "integer",
                    "description": "高度",
                    "default": 25,
                },
            },
            "required": ["dv_id", "chart_id"],
        },
    ),
    Tool(
        name="delete_component",
        description="删除仪表板画布上的组件或筛选条件。传入 component_id 删除整个组件（图表/筛选器），传入 filter_item_id 仅删除筛选条件项。",
        inputSchema={
            "type": "object",
            "properties": {
                "dv_id": {
                    "type": ["integer", "string"],
                    "description": "仪表板 ID",
                },
                "component_id": {
                    "type": "string",
                    "description": "要删除的组件 ID",
                },
                "filter_item_id": {
                    "type": "string",
                    "description": "筛选条件项 ID（仅删除筛选条件时提供）",
                },
            },
            "required": ["dv_id"],
        },
    ),
    Tool(
        name="add_filter_component",
        description="向仪表板添加筛选器组件。筛选器类型支持 dropdown（下拉）、multiple（多选）、checkbox（复选框）。需要先获取数据集的字段信息和图表 ID。",
        inputSchema={
            "type": "object",
            "properties": {
                "dv_id": {
                    "type": ["integer", "string"],
                    "description": "仪表板 ID",
                },
                "dataset_id": {
                    "type": ["integer", "string"],
                    "description": "数据集 ID",
                },
                "field_id": {
                    "type": ["integer", "string"],
                    "description": "筛选字段 ID（从 get_dataset_fields 获取）",
                },
                "field_name": {
                    "type": "string",
                    "description": "筛选字段名称",
                },
                "chart_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "受筛选器控制的图表组件 ID 列表",
                },
                "filter_type": {
                    "type": "string",
                    "description": "筛选器类型: dropdown=下拉单选, multiple=多选, checkbox=复选框",
                    "default": "dropdown",
                    "enum": ["dropdown", "multiple", "checkbox"],
                },
                "x": {
                    "type": "integer",
                    "description": "水平位置",
                    "default": 1,
                },
                "y": {
                    "type": "integer",
                    "description": "垂直位置",
                    "default": 1,
                },
            },
            "required": ["dv_id", "dataset_id", "field_id", "field_name", "chart_ids"],
        },
    ),

    Tool(
        name="update_filter_component",
        description="更新仪表板上筛选器组件的配置，如修改筛选字段值、关联图表、多选模式等。",
        inputSchema={
            "type": "object",
            "properties": {
                "dv_id": {
                    "type": ["integer", "string"],
                    "description": "仪表板 ID",
                },
                "filter_item_id": {
                    "type": "string",
                    "description": "筛选条件项 ID",
                },
                "chart_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "更新关联的图表 ID 列表",
                },
                "select_value": {
                    "type": "string",
                    "description": "默认筛选值",
                },
                "multiple": {
                    "type": "boolean",
                    "description": "是否多选",
                },
                "field_name": {
                    "type": "string",
                    "description": "筛选字段名称",
                },
            },
            "required": ["dv_id", "filter_item_id"],
        },
    ),
]

TOOL_HANDLERS = {
    "list_dashboards": lambda args: dashboard.list_dashboards(
        args.get("keyword", ""), args.get("dv_type", "")
    ),
    "get_dashboard_detail": lambda args: dashboard.get_dashboard_detail(
        args["dv_id"]
    ),
    "create_dashboard": lambda args: dashboard.create_dashboard(args["name"], args["pid"], args.get("node_type", "leaf"), args.get("dv_type", "dashboard")),
    "delete_dashboard": lambda args: dashboard.delete_dashboard(args["dv_id"]),
    "set_publish_status": lambda args: dashboard.set_publish_status(args["dv_id"], args["status"]),
    "copy_dashboard": lambda args: dashboard.copy_dashboard(
        args["source_dv_id"],
        args["target_pid"],
        args.get("new_name", ""),
    ),
    "update_dashboard_name": lambda args: dashboard.update_dashboard_name(
        args["dv_id"], args["new_name"]
    ),
    "list_datasets": lambda args: dataset.list_datasets(
        args.get("keyword", ""), args.get("pid", 0)
    ),
    "preview_dataset_data": lambda args: dataset.preview_dataset_data(
        args["dataset_id"], args.get("limit", 100)
    ),
    "get_dataset_info": lambda args: dataset.get_dataset_info(args["dataset_id"]),
    "create_dataset": lambda args: dataset.create_dataset(args["name"], args["pid"], args.get("node_type", "dataset"), args.get("datasource_id", 0), args.get("sql", "")),
    "delete_dataset": lambda args: dataset.delete_dataset(args["dataset_id"]),
    "rename_dataset": lambda args: dataset.rename_dataset(
        args["dataset_id"], args["new_name"]
    ),
    "preview_sql": lambda args: dataset.preview_sql(
        args["datasource_id"], args["sql"]
    ),
    "list_datasources": lambda args: datasource.list_datasources(
        args.get("keyword", "")
    ),
    "get_datasource_detail": lambda args: datasource.get_datasource_detail(args["ds_id"], args.get("full", False)),
    "get_datasource_tables": lambda args: datasource.get_datasource_tables(args["ds_id"], args.get("include_fields", False)),
    "get_datasource_types": lambda args: datasource.list_datasource_types(),
    "test_datasource_connection": lambda args: datasource.test_datasource_connection(
        args["ds_id"]
    ),
    "preview_table_data": lambda args: datasource.preview_table_data(
        args["ds_id"], args["table_name"]
    ),
    "delete_datasource": lambda args: datasource.delete_datasource(args["ds_id"]),
    "rename_datasource": lambda args: datasource.rename_datasource(
        args["ds_id"], args["new_name"]
    ),
    "create_datasource_folder": lambda args: datasource.create_datasource_folder(
        args["name"], args.get("pid", 0)
    ),
    "list_users": lambda args: user.list_users(
        args.get("keyword", ""),
        args.get("page", 1),
        args.get("page_size", 20),
    ),
    "get_user_info": lambda args: user.get_user_info(
        args.get("user_id", 0)
    ),
    "create_user": lambda args: user.create_user(
        args["name"],
        args["account"],
        args["email"],
        args["role_ids"],
        args.get("enabled", True),
    ),
    "delete_user": lambda args: user.delete_user(args["user_id"]),
    "enable_user": lambda args: user.enable_user(
        args["user_id"], args["enabled"]
    ),
    "configure_share": lambda args: share.configure_share(args["resource_id"], args.get("action", "toggle"), args.get("expiry_timestamp", 0), args.get("password", "")),
    "get_share_info": lambda args: share.get_share_info(args.get("resource_id", 0)),
    "get_export_info": lambda args: export_tools.get_export_info(args.get("status", ""), args.get("page", 1), args.get("page_size", 20)),
    "download_export_file": lambda args: export_tools.download_export_file(
        args["task_id"]
    ),
    "retry_export": lambda args: export_tools.retry_export(args["task_id"]),
    "list_templates": lambda args: template.list_templates(args.get("keyword", ""), args.get("source", "local")),
    "get_template_detail": lambda args: template.get_template_detail(
        args["template_id"], args.get("preview", False)
    ),
    "apply_template": lambda args: template.apply_template(
        args["template_id"], args["target_pid"], args["new_name"]
    ),
    "get_chart_detail": lambda args: chart.get_chart_detail(
        args["chart_id"], args.get("resource_table", "snapshot")
    ),
    "get_chart_data": lambda args: chart.get_chart_data(args["chart_id"]),
    "get_dashboard_views": lambda args: chart.get_dashboard_views(
        args["dashboard_id"]
    ),
    "get_chart_fields": lambda args: chart.get_chart_fields(
        args["dataset_id"], args["chart_id"]
    ),
    "get_field_enum_values": lambda args: dataset.get_field_enum_values(
        args["dataset_id"], args["field_ids"]
    ),
    "save_chart": lambda args: chart.save_chart(
        title=args["title"],
        dashboard_id=args["dashboard_id"],
        dataset_id=args["dataset_id"],
        chart_type=args["chart_type"],
        x_fields=args["x_fields"],
        y_fields=args["y_fields"],
        y_fields_ext=args.get("y_fields_ext", None),
        chart_id=args.get("chart_id", 0),
        custom_attr=args.get("custom_attr", None),
        custom_style=args.get("custom_style", None),
        result_count=args.get("result_count", 1000),
    ),
    "get_chart_types": lambda args: chart.get_chart_types(),
    "update_chart": lambda args: chart.update_chart(
        title=args["title"],
        dashboard_id=args["dashboard_id"],
        dataset_id=args["dataset_id"],
        chart_type=args["chart_type"],
        x_fields=args["x_fields"],
        y_fields=args["y_fields"],
        chart_id=args["chart_id"],
        result_count=args.get("result_count", 1000),
    ),
    "get_dashboard_layout": lambda args: canvas.get_dashboard_layout(
        args["dv_id"]
    ),
    "update_component_position": lambda args: canvas.update_component_position(
        args["dv_id"],
        args["component_id"],
        args["x"],
        args["y"],
        args.get("size_x", 0),
        args.get("size_y", 0),
    ),
    "add_chart_to_canvas": lambda args: canvas.add_chart_to_canvas(
        args["dv_id"],
        args["chart_id"],
        args.get("chart_title", ""),
        args.get("chart_type", "bar"),
        args.get("x", 1),
        args.get("y", 1),
        args.get("size_x", 36),
        args.get("size_y", 25),
    ),
    "delete_component": lambda args: canvas.delete_component(args["dv_id"], args.get("component_id", ""), args.get("filter_item_id", "")),
    "add_filter_component": lambda args: canvas.add_filter_component(
        args["dv_id"],
        args["dataset_id"],
        args["field_id"],
        args["field_name"],
        args["chart_ids"],
        args.get("filter_type", "dropdown"),
        args.get("x", 1),
        args.get("y", 1),
    ),
    "update_filter_component": lambda args: canvas.update_filter_component(
        args["dv_id"],
        args["filter_item_id"],
        args.get("chart_ids"),
        args.get("select_value"),
        args.get("multiple"),
        args.get("field_name"),
    ),
}

@server.list_tools()
async def list_tools() -> list[Tool]:
    return TOOLS

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    handler = TOOL_HANDLERS.get(name)
    if not handler:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]
    try:
        for key in list(arguments.keys()):
            val = arguments[key]
            if key in _ID_PARAMS and val is not None:
                if isinstance(val, list):
                    arguments[key] = [safe_int(v) for v in val]
                else:
                    arguments[key] = safe_int(val)
            elif key in _ARRAY_INT_PARAMS and isinstance(val, list):
                arguments[key] = [safe_int(v) for v in val]
        result = await handler(arguments)
        import json

        return [
            TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2),
            )
        ]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {e}")]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
