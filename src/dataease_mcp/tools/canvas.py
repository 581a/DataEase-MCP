import json as _json
from ..client import de_client
from ..utils import generate_view_id

_FILTER_BASE_TEMPLATE = {
    "showError": False,
    "timeGranularity": "date",
    "timeGranularityMultiple": "datetimerange",
    "sort": "desc",
    "defaultMapValue": [1],
    "mapValue": [1],
    "conditionType": 0,
    "conditionValueOperatorF": "eq",
    "conditionValueF": "",
    "conditionValueOperatorS": "like",
    "conditionValueS": "",
    "defaultConditionValueOperatorF": "eq",
    "defaultConditionValueF": "",
    "defaultConditionValueOperatorS": "like",
    "defaultConditionValueS": "",
    "timeType": "fixed",
    "relativeToCurrent": "custom",
    "required": True,
    "timeNum": 0,
    "relativeToCurrentType": "date",
    "around": "f",
    "parametersStart": None,
    "parametersEnd": None,
    "arbitraryTime": None,
    "timeNumRange": 0,
    "relativeToCurrentTypeRange": "date",
    "aroundRange": "f",
    "arbitraryTimeRange": None,
    "auto": False,
    "selectValue": "",
    "defaultValue": "",
    "optionValueSource": 1,
    "valueSource": [],
    "dataset": {},
    "visible": True,
    "defaultValueCheck": False,
    "multiple": False,
    "displayType": 0,
    "parameters": [],
    "parametersCheck": False,
    "parametersList": [],
    "hideConditionSwitching": False,
    "resultMode": 1,
    "relativeToCurrentRange": "custom",
    "setTimeRange": False,
    "showEmpty": False,
    "defaultNumValueStart": None,
    "defaultNumValueEnd": None,
    "numValueEnd": None,
    "numValueStart": None,
    "displayFormat": 0,
    "timeRange": {
        "intervalType": "none",
        "dynamicWindow": False,
        "maximumSingleQuery": 0,
        "regularOrTrends": "fixed",
        "regularOrTrendsValue": 0,
        "regularOrTrendsUnit": "day",
    },
    "oldTreeLoad": False,
    "treeCheckedList": [1],
    "defaultValueFirstItem": True,
    "treeFieldList": [],
    "checkedFieldsMapArr": {},
    "checkedFieldsMapArrNum": {},
    "checkedFieldsMapStart": {},
    "checkedFieldsMapStartNum": {},
    "checkedFieldsMapEnd": {},
    "checkedFieldsMapEndNum": {},
    "parametersArr": {},
    "queryConditionWidth": 100,
    "sortList": [],
    "placeholder": "",
}

_USER_VIEW_STYLE = {
    "rotate": 0,
    "opacity": 1,
    "borderActive": False,
    "borderWidth": 1,
    "borderRadius": 5,
    "borderStyle": "solid",
    "borderColor": "rgba(204, 204, 204, 1)",
}

_USER_VIEW_BACKGROUND = {
    "backgroundColorSelect": True,
    "backdropFilterEnable": False,
    "backgroundImageEnable": False,
    "backgroundType": "innerImage",
    "innerImage": "board/board_1280_720.png",
}

_USER_VIEW_COLLAPSE_NAMES = [
    "position", "background", "style", "picture",
    "frameLinks", "videoLinks", "streamLinks",
    "carouselInfo", "events", "decoration_style",
]

_USER_VIEW_EVENTS = {
    "checked": False,
    "showTips": False,
    "type": "jump",
    "typeList": [
        {"key": "jump", "label": "jump"},
        {"key": "download", "label": "download"},
    ],
}

_USER_VIEW_CAROUSEL = {"enable": False, "time": 10}
_USER_VIEW_MULTI_DIMENSIONAL = {"enable": False, "x": 0, "y": 0, "z": 0}
_USER_VIEW_GROUP_STYLE = {}
_USER_VIEW_MATRIX_STYLE = {}
_USER_VIEW_LINKAGE = {
    "duration": 0,
    "data": [{"id": "", "label": "", "event": "", "style": [{"key": "", "value": ""}]}],
}
_USER_VIEW_ACTION_SELECTION = {"linkageActive": "custom"}

_FILTER_WRAPPER_TEMPLATE = {
    "canvasId": "canvas-main",
    "isLock": False,
    "maintainRadio": False,
    "aspectRatio": 1,
    "isShow": True,
    "dashboardHidden": False,
    "category": "base",
    "dragging": False,
    "resizing": False,
    "component": "VQuery",
    "name": "查询组件",
    "label": "查询组件",
    "icon": "icon_search",
    "innerType": "VQuery",
    "isHang": False,
    "freeze": True,
    "x": 1,
    "y": 1,
    "sizeX": 72,
    "sizeY": 3,
    "state": "prepare",
    "canvasActive": False,
    "editing": False,
    "_dragId": 0,
    "show": True,
    "expand": False,
    "resizeInnerKeep": False,
}


async def _load_dashboard_canvas(dv_id: int) -> dict:
    resp = await de_client.post(
        "/dataVisualization/findById",
        {"id": dv_id, "resourceTable": "snapshot", "source": "main_edit"},
    )
    return resp


def _parse_component_data(detail: dict) -> list:
    raw = detail.get("componentData", "[]")
    if isinstance(raw, str):
        try:
            return _json.loads(raw)
        except (_json.JSONDecodeError, TypeError):
            return []
    if raw is None:
        return []
    if isinstance(raw, list):
        return raw
    return []


async def _save_dashboard_canvas(
    dv_id: int,
    component_data: list,
    detail: dict,
) -> dict:
    from ..tools import chart as chart_tools

    canvas_view_info = {}
    for comp in component_data:
        if comp.get("component") == "UserView":
            cid = comp.get("id", "")
            if cid:
                try:
                    cid_int = int(cid)
                    cd = await chart_tools.get_chart_detail(cid_int, "snapshot")
                    if cd:
                        canvas_view_info[cid] = {
                            "id": cid_int,
                            "title": cd.get("title", comp.get("name", str(cid))),
                            "sceneId": dv_id,
                            "tableId": cd.get("tableId"),
                            "type": cd.get("type", comp.get("innerType", "table-info")),
                            "render": cd.get("render", "antv"),
                            "xAxis": cd.get("xAxis", []),
                            "yAxis": cd.get("yAxis", []),
                            "xAxisExt": cd.get("xAxisExt", []),
                            "yAxisExt": cd.get("yAxisExt", []),
                            "extStack": cd.get("extStack", []),
                            "extBubble": cd.get("extBubble", []),
                            "extLabel": cd.get("extLabel", []),
                            "extTooltip": cd.get("extTooltip", []),
                            "extColor": cd.get("extColor", []),
                            "drillFields": cd.get("drillFields", []),
                            "customAttr": cd.get("customAttr", {}),
                            "customAttrMobile": cd.get("customAttrMobile", {}),
                            "customStyle": cd.get("customStyle", {}),
                            "customStyleMobile": cd.get("customStyleMobile", {}),
                            "senior": cd.get("senior", {}),
                            "stylePriority": cd.get("stylePriority", "view"),
                            "isPlugin": cd.get("isPlugin", False),
                            "refreshViewEnable": cd.get("refreshViewEnable", False),
                            "linkageActive": cd.get("linkageActive", False),
                            "jumpActive": cd.get("jumpActive", False),
                            "aggregate": cd.get("aggregate", False),
                            "dataFrom": cd.get("dataFrom", "dataset"),
                            "resultMode": cd.get("resultMode", "custom"),
                            "resultCount": cd.get("resultCount", 1000),
                        }
                    else:
                        canvas_view_info[cid] = {
                            "id": cid_int,
                            "title": comp.get("name", str(cid)),
                            "sceneId": dv_id,
                            "type": comp.get("innerType", "table-info"),
                        }
                except (ValueError, TypeError):
                    canvas_view_info[cid] = {
                        "id": cid,
                        "title": comp.get("name", str(cid)),
                        "sceneId": dv_id,
                        "type": comp.get("innerType", "table-info"),
                    }

    for cvi in canvas_view_info.values():
        for axis_key in ("xAxis", "yAxis", "xAxisExt", "yAxisExt"):
            for field in cvi.get(axis_key, []) or []:
                if isinstance(field, dict):
                    if field.get("extField") is None:
                        field["extField"] = 0
                    if field.get("originName") is None:
                        field["originName"] = field.get("name", "")
                    if field.get("dataeaseName") is None:
                        field["dataeaseName"] = field.get("name", "")
                    if field.get("deType") is None:
                        field["deType"] = 0

    body = {
        "id": detail.get("id", dv_id),
        "pid": detail.get("pid", 0),
        "name": detail.get("name", ""),
        "nodeType": detail.get("nodeType", "leaf"),
        "type": detail.get("type", "dashboard"),
        "busiFlag": "dashboard",
        "status": detail.get("status", 1),
        "selfWatermarkStatus": detail.get("selfWatermarkStatus", False),
        "mobileLayout": detail.get("mobileLayout", False),
        "contentId": detail.get("contentId") or "",
        "componentData": _json.dumps(component_data, separators=(",", ":"), ensure_ascii=False),
        "canvasStyleData": detail.get("canvasStyleData") or "{}",
        "canvasViewInfo": canvas_view_info,
    }
    resp = await de_client.post("/dataVisualization/updateCanvas", body)
    return resp


async def get_dashboard_layout(dv_id: int) -> list:
    detail = await _load_dashboard_canvas(dv_id)
    if not detail:
        return []

    components = _parse_component_data(detail)

    result = []
    for comp in components:
        item = {
            "id": comp.get("id"),
            "component": comp.get("component"),
            "name": comp.get("name", comp.get("title", "")),
            "innerType": comp.get("innerType", ""),
            "x": comp.get("x", 0),
            "y": comp.get("y", 0),
            "sizeX": comp.get("sizeX", 0),
            "sizeY": comp.get("sizeY", 0),
            "show": comp.get("show", True),
            "category": comp.get("category", "base"),
        }
        if comp.get("component") == "VQuery":
            pv = comp.get("propValue", [])
            filters = []
            for fitem in pv if isinstance(pv, list) else []:
                filters.append({
                    "id": fitem.get("id"),
                    "name": fitem.get("name", ""),
                    "displayType": fitem.get("displayType", 0),
                    "fieldId": fitem.get("field", {}).get("id", "") if isinstance(fitem.get("field"), dict) else "",
                    "fieldName": fitem.get("field", {}).get("name", "") if isinstance(fitem.get("field"), dict) else "",
                    "checkedFields": fitem.get("checkedFields", []),
                    "operator": fitem.get("conditionValueOperatorF", "eq"),
                    "selectValue": fitem.get("selectValue", ""),
                    "multiple": fitem.get("multiple", False),
                })
            item["filters"] = filters
        result.append(item)

    return result


async def update_component_position(
    dv_id: int,
    component_id: str,
    x: int,
    y: int,
    size_x: int = 0,
    size_y: int = 0,
) -> dict:
    detail = await _load_dashboard_canvas(dv_id)
    if not detail:
        return {"error": "仪表板不存在"}

    components = _parse_component_data(detail)

    found = False
    for comp in components:
        if str(comp.get("id")) == str(component_id):
            comp["x"] = x
            comp["y"] = y
            if size_x > 0:
                comp["sizeX"] = size_x
            if size_y > 0:
                comp["sizeY"] = size_y
            found = True
            break

    if not found:
        return {"error": f"组件 {component_id} 不存在"}

    result = await _save_dashboard_canvas(dv_id, components, detail)
    return {"success": True, "updated": component_id, "result": result}


async def add_chart_to_canvas(
    dv_id: int,
    chart_id: int,
    chart_title: str = "",
    chart_type: str = "bar",
    x: int = 1,
    y: int = 1,
    size_x: int = 36,
    size_y: int = 25,
) -> dict:
    from ..utils import CHART_TYPE_LIST

    detail = await _load_dashboard_canvas(dv_id)
    if not detail:
        return {"error": "仪表板不存在"}

    components = _parse_component_data(detail)

    cid_str = str(chart_id)
    chart_types = {}
    for entry in CHART_TYPE_LIST:
        if isinstance(entry, (tuple, list)) and len(entry) >= 2:
            chart_types[entry[0]] = entry[1]
    chart_name = chart_types.get(chart_type, chart_type)

    icon_map = {
        "bar": "bar", "line": "line", "pie": "pie",
        "indicator": "indicator", "table-info": "table-info",
        "table-normal": "table-normal", "gauge": "gauge",
        "sankey": "sankey", "radar": "radar", "funnel": "funnel",
        "scatter": "scatter", "waterfall": "waterfall", "map": "map",
    }

    new_comp = {
        "animations": [],
        "canvasId": "canvas-main",
        "events": _USER_VIEW_EVENTS,
        "carousel": _USER_VIEW_CAROUSEL,
        "multiDimensional": _USER_VIEW_MULTI_DIMENSIONAL,
        "groupStyle": _USER_VIEW_GROUP_STYLE,
        "isLock": False,
        "maintainRadio": False,
        "aspectRatio": 1,
        "isShow": True,
        "dashboardHidden": False,
        "category": "base",
        "dragging": False,
        "resizing": False,
        "collapseName": _USER_VIEW_COLLAPSE_NAMES,
        "linkage": _USER_VIEW_LINKAGE,
        "component": "UserView",
        "name": chart_title or cid_str,
        "label": chart_name,
        "propValue": {},
        "icon": icon_map.get(chart_type, "bar"),
        "innerType": chart_type,
        "editing": False,
        "canvasActive": False,
        "actionSelection": _USER_VIEW_ACTION_SELECTION,
        "x": x,
        "y": y,
        "sizeX": size_x,
        "sizeY": size_y,
        "style": _USER_VIEW_STYLE,
        "matrixStyle": _USER_VIEW_MATRIX_STYLE,
        "commonBackground": _USER_VIEW_BACKGROUND,
        "state": "ready",
        "render": "antv",
        "isPlugin": False,
        "id": cid_str,
        "_dragId": 0,
        "show": True,
        "linkageFilters": [],
        "expand": False,
        "resizeInnerKeep": False,
        "title": chart_title or "图表",
    }
    components.append(new_comp)

    result = await _save_dashboard_canvas(dv_id, components, detail)
    return {"success": True, "chart_id": chart_id, "result": result}


async def delete_component(
    dv_id: int, component_id: str = "", filter_item_id: str = ""
) -> dict:
    detail = await _load_dashboard_canvas(dv_id)
    if not detail:
        return {"error": "仪表板不存在"}

    components = _parse_component_data(detail)

    if filter_item_id:
        for comp in components:
            if comp.get("component") == "VQuery":
                pv = comp.get("propValue", [])
                new_pv = [
                    fitem for fitem in (pv if isinstance(pv, list) else [])
                    if str(fitem.get("id")) != str(filter_item_id)
                ]
                comp["propValue"] = new_pv
        result = await _save_dashboard_canvas(dv_id, components, detail)
        return {"success": True, "deleted_filter_item": filter_item_id, "result": result}

    new_components = [c for c in components if str(c.get("id")) != str(component_id)]

    for comp in new_components:
        if comp.get("component") == "VQuery":
            pv = comp.get("propValue", [])
            for fitem in pv if isinstance(pv, list) else []:
                cf = fitem.get("checkedFields", [])
                if isinstance(cf, list) and component_id in cf:
                    cf.remove(component_id)
                cfm = fitem.get("checkedFieldsMap", {})
                if isinstance(cfm, dict) and component_id in cfm:
                    del cfm[component_id]

    if len(new_components) == len(components):
        return {"error": f"组件 {component_id} 不存在"}

    result = await _save_dashboard_canvas(dv_id, new_components, detail)
    return {"success": True, "deleted": component_id, "result": result}


async def add_filter_component(
    dv_id: int,
    dataset_id: int,
    field_id: int,
    field_name: str,
    chart_ids: list[str],
    filter_type: str = "dropdown",
    x: int = 1,
    y: int = 1,
) -> dict:
    detail = await _load_dashboard_canvas(dv_id)
    if not detail:
        return {"error": "仪表板不存在"}

    components = _parse_component_data(detail)

    filter_id = generate_view_id()
    field_id_str = str(field_id)
    chart_id_list = [str(cid) for cid in chart_ids]
    checked_fields_map = {cid: field_id_str for cid in chart_id_list}
    checked_fields_map_arr = {cid: [] for cid in chart_id_list}
    checked_fields_map_arr_num = {cid: [] for cid in chart_id_list}
    checked_fields_map_start = {cid: "" for cid in chart_id_list}
    checked_fields_map_start_num = {cid: "" for cid in chart_id_list}
    checked_fields_map_end = {cid: "" for cid in chart_id_list}
    checked_fields_map_end_num = {cid: "" for cid in chart_id_list}
    parameters_arr = {cid: [] for cid in chart_id_list}

    allow_multiple = filter_type in ("multiple", "checkbox")
    display_type = "0"

    import copy
    filter_item = copy.deepcopy(_FILTER_BASE_TEMPLATE)

    filter_item.update({
        "id": filter_id,
        "name": field_name,
        "field": {"id": field_id_str, "type": "VARCHAR", "name": field_name, "deType": 0},
        "displayId": field_id,
        "sortId": field_id,
        "displayType": display_type,
        "checkedFields": chart_id_list,
        "checkedFieldsMap": checked_fields_map,
        "checkedFieldsMapArr": checked_fields_map_arr,
        "checkedFieldsMapArrNum": checked_fields_map_arr_num,
        "checkedFieldsMapStart": checked_fields_map_start,
        "checkedFieldsMapStartNum": checked_fields_map_start_num,
        "checkedFieldsMapEnd": checked_fields_map_end,
        "checkedFieldsMapEndNum": checked_fields_map_end_num,
        "parametersArr": parameters_arr,
        "multiple": allow_multiple,
    })

    vquery_found = False
    for comp in components:
        if comp.get("component") == "VQuery":
            pv = comp.get("propValue")
            if isinstance(pv, list):
                pv.append(filter_item)
            vquery_found = True
            break

    if not vquery_found:
        filter_wrapper = copy.deepcopy(_FILTER_WRAPPER_TEMPLATE)
        filter_wrapper["id"] = str(generate_view_id())
        filter_wrapper["x"] = x
        filter_wrapper["y"] = y
        filter_wrapper["propValue"] = [filter_item]
        components.append(filter_wrapper)

    result = await _save_dashboard_canvas(dv_id, components, detail)
    return {
        "success": True,
        "filter_id": filter_id,
        "field_name": field_name,
        "chart_ids": chart_id_list,
        "result": result,
    }


async def delete_filter_component(
    dv_id: int, filter_component_id: str = "", filter_item_id: str = ""
) -> dict:
    detail = await _load_dashboard_canvas(dv_id)
    if not detail:
        return {"error": "仪表板不存在"}

    components = _parse_component_data(detail)

    if filter_component_id:
        components = [c for c in components if str(c.get("id")) != str(filter_component_id)]
    elif filter_item_id:
        for comp in components:
            if comp.get("component") == "VQuery":
                pv = comp.get("propValue", [])
                if isinstance(pv, list):
                    comp["propValue"] = [
                        f for f in pv if str(f.get("id")) != str(filter_item_id)
                    ]

    result = await _save_dashboard_canvas(dv_id, components, detail)
    return {"success": True, "result": result}


async def update_filter_component(
    dv_id: int,
    filter_item_id: str,
    chart_ids: list[str] | None = None,
    select_value: str | None = None,
    multiple: bool | None = None,
    field_name: str | None = None,
) -> dict:
    detail = await _load_dashboard_canvas(dv_id)
    if not detail:
        return {"error": "仪表板不存在"}

    components = _parse_component_data(detail)

    found = False
    for comp in components:
        if comp.get("component") != "VQuery":
            continue
        pv = comp.get("propValue", [])
        if not isinstance(pv, list):
            continue
        for fitem in pv:
            if str(fitem.get("id")) == str(filter_item_id):
                if chart_ids is not None:
                    chart_id_list = [str(cid) for cid in chart_ids]
                    fitem["checkedFields"] = chart_id_list
                    field_id_str = str(fitem.get("field", {}).get("id", fitem.get("displayId", "")))
                    fitem["checkedFieldsMap"] = {cid: field_id_str for cid in chart_id_list}
                    fitem["checkedFieldsMapArr"] = {cid: [] for cid in chart_id_list}
                    fitem["checkedFieldsMapArrNum"] = {cid: [] for cid in chart_id_list}
                    fitem["checkedFieldsMapStart"] = {cid: "" for cid in chart_id_list}
                    fitem["checkedFieldsMapStartNum"] = {cid: "" for cid in chart_id_list}
                    fitem["checkedFieldsMapEnd"] = {cid: "" for cid in chart_id_list}
                    fitem["checkedFieldsMapEndNum"] = {cid: "" for cid in chart_id_list}
                    fitem["parametersArr"] = {cid: [] for cid in chart_id_list}
                if select_value is not None:
                    fitem["selectValue"] = select_value
                    fitem["defaultValue"] = select_value
                    fitem["defaultValueCheck"] = bool(select_value)
                if multiple is not None:
                    fitem["multiple"] = multiple
                if field_name is not None:
                    fitem["name"] = field_name
                    if isinstance(fitem.get("field"), dict):
                        fitem["field"]["name"] = field_name
                found = True
                break
        if found:
            break

    if not found:
        return {"error": f"筛选条件 {filter_item_id} 不存在"}

    result = await _save_dashboard_canvas(dv_id, components, detail)
    return {"success": True, "updated": filter_item_id, "result": result}
