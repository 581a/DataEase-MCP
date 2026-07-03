from ..client import de_client
from ..utils import generate_view_id


def _field_defaults(fields: list[dict], chart_type: str, group_type: str) -> None:
    for f in fields:
        f.setdefault("summary", "" if group_type == "d" else "sum")
        f.setdefault("sort", "none")
        f.setdefault("dateStyle", "" if group_type == "d" else "y_M_d")
        f.setdefault("datePattern", "" if group_type == "d" else "date_sub")
        f.setdefault("dateShowFormat", "" if group_type == "d" else "y_M_d")
        f.setdefault("chartType", chart_type)
        f.setdefault("groupType", group_type)
        f.setdefault("filter", [])
        f.setdefault("compareCalc", {"type": "none"})
        f.setdefault("formatterCfg", {"unitLanguage": "ch"})
        f.setdefault("extField", 0)
        f.setdefault("originName", f.get("originName") or f.get("name", ""))



async def get_chart_detail(chart_id: int, resource_table: str = "snapshot") -> dict:
    try:
        resp = await de_client.post(f"/chart/getDetail/{chart_id}/{resource_table}")
    except RuntimeError:
        if resource_table != "core":
            resp = await de_client.post(f"/chart/getDetail/{chart_id}/core")
        else:
            raise
    return resp


async def get_chart_data(chart_id: int) -> dict:
    resp = await de_client.post(
        "/chartData/getData",
        {
            "id": chart_id,
            "resourceTable": "core",
            "resultMode": "custom",
            "resultCount": 1000,
        },
    )
    return resp


async def get_dashboard_views(dashboard_id: int) -> list:
    resp = await de_client.get(f"/chart/viewOption/{dashboard_id}")
    return resp


async def get_chart_fields(dataset_id: int, chart_id: int) -> dict:
    resp = await de_client.post(
        f"/chart/listByDQ/{dataset_id}/{chart_id}",
        {
            "id": chart_id,
            "tableId": dataset_id,
        },
    )
    return resp


async def export_chart_data(chart_id: int, dv_id: int) -> dict:
    resp = await de_client.post(
        "/chartData/innerExportDetails",
        {
            "dvId": dv_id,
            "viewId": str(chart_id),
        },
    )
    return resp


async def save_chart(
    title: str,
    dashboard_id: int,
    dataset_id: int,
    chart_type: str,
    x_fields: list[dict],
    y_fields: list[dict],
    chart_id: int = 0,
    result_count: int = 1000,
    custom_attr: dict | None = None,
) -> dict:
    if not chart_id:
        chart_id = generate_view_id()

    _field_defaults(x_fields, chart_type, "d")
    _field_defaults(y_fields, chart_type, "q")

    body = {
        "id": chart_id,
        "title": title,
        "sceneId": dashboard_id,
        "tableId": dataset_id,
        "type": chart_type,
        "render": "antv",
        "chartType": "private",
        "dataFrom": "dataset",
        "resultMode": "custom",
        "resultCount": result_count,
        "xAxis": x_fields,
        "yAxis": y_fields,
        "xAxisExt": [],
        "yAxisExt": [],
        "extStack": [],
        "extBubble": [],
        "extLabel": [],
        "extTooltip": [],
        "extColor": [],
        "drillFields": [],
        "viewFields": [],
        "flowMapStartName": [],
        "flowMapEndName": [],
        "customAttr": custom_attr if custom_attr else {},
        "customAttrMobile": {},
        "customStyle": {},
        "customStyleMobile": {},
        "senior": {},
        "stylePriority": "view",
        "isPlugin": False,
        "refreshViewEnable": False,
        "linkageActive": False,
        "jumpActive": False,
        "aggregate": False,
    }

    resp = await de_client.post("/chart/save", body)
    return resp


async def get_chart_types() -> dict:
    from ..utils import CHART_TYPE_LIST, _CHART_TYPE_DESCRIPTIONS
    return {
        "chart_types": [
            {"type": t, "description": _CHART_TYPE_DESCRIPTIONS.get(t, t)}
            for t in CHART_TYPE_LIST
        ]
    }


async def update_chart(
    title: str,
    dashboard_id: int,
    dataset_id: int,
    chart_type: str,
    x_fields: list[dict],
    y_fields: list[dict],
    chart_id: int,
    result_count: int = 1000,
    custom_attr: dict | None = None,
) -> dict:
    existing = await get_chart_detail(int(chart_id), "snapshot")
    if not existing:
        return {"error": f"图表 {chart_id} 不存在"}

    _field_defaults(x_fields, chart_type, "d")
    _field_defaults(y_fields, chart_type, "q")

    body = {
        "id": int(chart_id),
        "title": title,
        "sceneId": int(dashboard_id),
        "tableId": int(dataset_id),
        "type": chart_type,
        "render": existing.get("render", "antv"),
        "chartType": existing.get("chartType", "private"),
        "dataFrom": existing.get("dataFrom", "dataset"),
        "resultMode": existing.get("resultMode", "custom"),
        "resultCount": result_count,
        "xAxis": x_fields,
        "yAxis": y_fields,
        "xAxisExt": existing.get("xAxisExt", []),
        "yAxisExt": existing.get("yAxisExt", []),
        "extStack": existing.get("extStack", []),
        "extBubble": existing.get("extBubble", []),
        "extLabel": existing.get("extLabel", []),
        "extTooltip": existing.get("extTooltip", []),
        "extColor": existing.get("extColor", []),
        "drillFields": existing.get("drillFields", []),
        "viewFields": existing.get("viewFields", []),
        "flowMapStartName": existing.get("flowMapStartName", []),
        "flowMapEndName": existing.get("flowMapEndName", []),
        "customAttr": custom_attr if custom_attr else existing.get("customAttr", {}),
        "customAttrMobile": existing.get("customAttrMobile", {}),
        "customStyle": existing.get("customStyle", {}),
        "customStyleMobile": existing.get("customStyleMobile", {}),
        "senior": existing.get("senior", {}),
        "stylePriority": existing.get("stylePriority", "view"),
        "isPlugin": existing.get("isPlugin", False),
        "refreshViewEnable": existing.get("refreshViewEnable", False),
        "linkageActive": existing.get("linkageActive", False),
        "jumpActive": existing.get("jumpActive", False),
        "aggregate": existing.get("aggregate", False),
    }

    resp = await de_client.post("/chart/save", body)
    return resp
