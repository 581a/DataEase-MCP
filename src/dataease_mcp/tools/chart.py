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
    except (RuntimeError, Exception) as e:
        if resource_table != "core":
            try:
                resp = await de_client.post(f"/chart/getDetail/{chart_id}/core")
            except (RuntimeError, Exception) as e2:
                raise RuntimeError(f"Chart {chart_id} not found in snapshot or core: {e2}") from e2
        else:
            raise RuntimeError(f"Chart {chart_id} not found in core: {e}") from e
    return resp


async def get_chart_data(chart_id: int) -> dict:
    try:
        resp = await de_client.post(
            "/chartData/getData",
            {
                "id": chart_id,
                "resourceTable": "snapshot",
                "resultMode": "custom",
                "resultCount": 1000,
            },
        )
        return resp
    except RuntimeError:
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
    y_fields_ext: list[dict] | None = None,
    chart_id: int = 0,
    result_count: int = 1000,
    custom_attr: dict | None = None,
) -> dict:
    if not chart_id:
        chart_id = generate_view_id()

    _field_defaults(x_fields, chart_type, "d")
    _field_defaults(y_fields, chart_type, "q")
    if y_fields_ext:
        _field_defaults(y_fields_ext, chart_type, "q")

    # 合并 x_fields 和 y_fields 作为 viewFields
    view_fields = []
    for f in x_fields:
        vf = {
            "id": f["id"],
            "name": f.get("name", ""),
            "dataeaseName": f.get("dataeaseName", ""),
            "groupType": f.get("groupType", "d"),
            "deType": f.get("deType", 0),
            "extField": f.get("extField", 0),
            "originName": f.get("originName", f.get("name", "")),
            "checked": True,
            "summary": "",
            "sort": "none",
            "filter": [],
            "dateStyle": "",
            "datePattern": "",
            "dateShowFormat": "",
            "chartType": chart_type,
            "compareCalc": {"type": "none"},
            "formatterCfg": {"type": "auto", "unitLanguage": "ch"},
            "index": None,
            "logic": None,
            "filterType": None,
        }
        view_fields.append(vf)
    for f in y_fields:
        vf = {
            "id": f["id"],
            "name": f.get("name", ""),
            "dataeaseName": f.get("dataeaseName", ""),
            "groupType": f.get("groupType", "q"),
            "deType": f.get("deType", 0),
            "extField": f.get("extField", 0),
            "originName": f.get("originName", f.get("name", "")),
            "checked": True,
            "summary": f.get("summary", "sum"),
            "sort": "none",
            "filter": [],
            "dateStyle": "y_M_d",
            "datePattern": "date_sub",
            "dateShowFormat": "y_M_d",
            "chartType": chart_type,
            "compareCalc": {"type": "none"},
            "formatterCfg": {"type": "auto", "unitLanguage": "ch"},
            "index": None,
            "logic": None,
            "filterType": None,
        }
        view_fields.append(vf)

    if y_fields_ext:
        for f in y_fields_ext:
            vf = {
                "id": f["id"],
                "name": f.get("name", ""),
                "dataeaseName": f.get("dataeaseName", ""),
                "groupType": f.get("groupType", "q"),
                "deType": f.get("deType", 0),
                "extField": f.get("extField", 0),
                "originName": f.get("originName", f.get("name", "")),
                "checked": True,
                "summary": f.get("summary", "sum"),
                "sort": "none",
                "filter": [],
                "dateStyle": "y_M_d",
                "datePattern": "date_sub",
                "dateShowFormat": "y_M_d",
                "chartType": chart_type,
                "compareCalc": {"type": "none"},
                "formatterCfg": {"type": "auto", "unitLanguage": "ch"},
                "index": None,
                "logic": None,
                "filterType": None,
            }
            view_fields.append(vf)

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
        "yAxisExt": y_fields_ext if y_fields_ext else [],
        "extStack": [],
        "extBubble": [],
        "extLabel": [],
        "extTooltip": [],
        "extColor": [],
        "drillFields": [],
        "viewFields": view_fields,
        "flowMapStartName": [],
        "flowMapEndName": [],
        "customAttr": custom_attr if custom_attr else {},
        "customAttrMobile": {},
        "customStyle": {},
        "customStyleMobile": {},
        "senior": {"_mcp_yAxisExt": y_fields_ext} if y_fields_ext else {},
        "stylePriority": "view",
        "isPlugin": False,
        "refreshViewEnable": False,
        "linkageActive": False,
        "jumpActive": False,
        "aggregate": False,
    }

    resp = await de_client.post("/chart/save", body)
    if isinstance(resp, dict) and "id" in resp:
        resp["id"] = str(resp["id"])
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

    # 合并 x_fields 和 y_fields 作为 viewFields
    view_fields = []
    for f in x_fields:
        vf = {
            "id": f["id"], "name": f.get("name", ""),
            "dataeaseName": f.get("dataeaseName", ""),
            "groupType": f.get("groupType", "d"),
            "deType": f.get("deType", 0), "extField": f.get("extField", 0),
            "originName": f.get("originName", f.get("name", "")),
            "checked": True, "summary": "", "sort": "none", "filter": [],
            "dateStyle": "", "datePattern": "", "dateShowFormat": "",
            "chartType": chart_type,
            "compareCalc": {"type": "none"},
            "formatterCfg": {"type": "auto", "unitLanguage": "ch"},
            "index": None, "logic": None, "filterType": None,
        }
        view_fields.append(vf)
    for f in y_fields:
        vf = {
            "id": f["id"], "name": f.get("name", ""),
            "dataeaseName": f.get("dataeaseName", ""),
            "groupType": f.get("groupType", "q"),
            "deType": f.get("deType", 0), "extField": f.get("extField", 0),
            "originName": f.get("originName", f.get("name", "")),
            "checked": True, "summary": f.get("summary", "sum"),
            "sort": "none", "filter": [],
            "dateStyle": "y_M_d", "datePattern": "date_sub", "dateShowFormat": "y_M_d",
            "chartType": chart_type,
            "compareCalc": {"type": "none"},
            "formatterCfg": {"type": "auto", "unitLanguage": "ch"},
            "index": None, "logic": None, "filterType": None,
        }
        view_fields.append(vf)

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
        "viewFields": view_fields,
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
    if isinstance(resp, dict) and "id" in resp:
        resp["id"] = str(resp["id"])
    return resp
