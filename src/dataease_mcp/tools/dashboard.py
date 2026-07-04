import json as _json
import uuid as _uuid

from ..client import de_client
from ..config import config as _de_config


async def list_dashboards(
    keyword: str = "", dv_type: str = ""
) -> list:
    busi_flag = dv_type if dv_type else "dashboard"
    body = {"busiFlag": busi_flag}
    resp = await de_client.post("/dataVisualization/tree", body)
    return resp


async def get_dashboard_detail(dv_id: int) -> dict:
    resp = await de_client.post(
        "/dataVisualization/findById",
        {"id": dv_id, "resourceTable": "snapshot", "source": "main_edit"},
    )
    return resp

_DEFAULT_CANVAS_STYLE = _json.dumps({
    "width": 1920, "height": 1080, "scale": 100, "scaleWidth": 1920, "scaleHeight": 1080,
    "refreshBrowserEnable": False, "refreshBrowserUnit": "minute", "refreshBrowserTime": 5,
    "refreshViewEnable": False, "refreshViewLoading": True, "refreshUnit": "minute",
    "refreshTime": 5, "popupAvailable": True, "popupButtonAvailable": True,
    "suspensionButtonAvailable": False, "suspensionViewButtonAvailable": True,
    "screenAdaptor": "widthFirst", "dashboardAdaptor": "keepHeightAndWidth",
    "scaleWidth": 60, "scaleHeight": 60,
    "backgroundColorSelect": True, "backgroundImageEnable": False,
    "backgroundType": "backgroundColor", "background": "",
    "openCommonStyle": True, "commonStyle": {},
    "opacity": 1, "fontSize": 14, "fontFamily": "PingFang",
    "color": "#000000", "backgroundColor": "rgba(245, 246, 247, 1)",
    "themeId": "10001",
    "dialogBackgroundColor": "rgba(255,255,255,1)",
    "dialogButton": "#020408",
    "dashboard": {
        "gap": "yes", "gapSize": 5, "gapMode": "middle",
        "showGrid": False, "matrixBase": 4,
        "resultMode": "all", "resultCount": 1000,
        "themeColor": "light", "mobileSetting": {
            "customSetting": False, "imageUrl": None,
            "backgroundType": "image", "color": "#000"
        }
    },
    "component": {
        "chartTitle": {
            "show": True, "fontSize": 16, "hPosition": "left",
            "vPosition": "top", "isItalic": False, "isBolder": True,
            "remarkShow": False, "remark": "",
            "fontFamily": "", "letterSpace": "0",
            "fontShadow": False, "color": "#000000",
            "remarkBackgroundColor": "#ffffff"
        },
        "chartColor": {
            "basicStyle": {
                "colorScheme": "default",
                "colors": ["#5470c6", "#91cc75", "#fac858", "#ee6666", "#73c0de", "#3ba272", "#fc8452", "#9a60b4", "#ea7ccc"],
                "alpha": 100, "gradient": False,
                "mapStyle": "normal", "areaBaseColor": "#FFFFFF",
                "areaBorderColor": "#303133", "gaugeStyle": "default",
                "tableBorderColor": "rgba(230, 231, 228, 1)",
                "tableScrollBarColor": "rgba(0, 0, 0, 0.15)",
                "zoomButtonColor": "#aaa", "zoomBackground": "#fff"
            },
            "misc": {
                "flowMapConfig": {
                    "lineConfig": {
                        "mapLineAnimate": True, "mapLineGradient": False,
                        "mapLineSourceColor": "#146C94", "mapLineTargetColor": "#576CBC"
                    }
                },
                "nameFontColor": "#000000", "valueFontColor": "#5470c6"
            },
            "tableHeader": {
                "tableHeaderBgColor": "#1E90FF", "tableHeaderCornerBgColor": "#1E90FF",
                "tableHeaderColBgColor": "#1E90FF", "tableHeaderFontColor": "#000000",
                "tableHeaderCornerFontColor": "#000000", "tableHeaderColFontColor": "#000000"
            },
            "tableCell": {
                "tableItemBgColor": "rgba(255, 255, 255, 1)", "tableFontColor": "#000000",
                "tableItemSubBgColor": "#1E90FF"
            }
        },
        "chartCommonStyle": {
            "backgroundColorSelect": True, "backgroundColor": "rgba(255,255,255,1)",
            "backdropFilterEnable": False, "backdropFilter": 4,
            "backgroundImageEnable": False, "backgroundType": "innerImage",
            "innerImage": "board/board_1.svg", "outerImage": None,
            "innerPadding": {"mode": "uniform", "top": 12},
            "borderRadius": {"mode": "uniform", "topLeft": 0},
            "innerImageColor": "rgba(16, 148, 229,1)",
        },
        "filterStyle": {
            "layout": "horizontal",
            "titleLayout": "left",
            "labelColor": "#1F2329",
            "titleColor": "#1F2329",
            "color": "#1f2329",
            "borderColor": "#BBBFC4",
            "text": "#1F2329",
            "bgColor": "#FFFFFF",
        },
        "tabStyle": {
            "headPosition": "left",
            "headFontColor": "#000000",
            "headFontActiveColor": "#000000",
            "headBorderColor": "#ffffff",
            "headBorderActiveColor": "#ffffff",
        },
        "seniorStyleSetting": {
            "linkageIconColor": "#A6A6A6",
            "drillLayerColor": "#A6A6A6",
            "pagerColor": "rgba(166, 166, 166, 1)",
        },
        "formatterItem": {
            "type": "auto", "unit": 1, "suffix": "",
            "decimalCount": 2, "thousandSeparator": True,
            "unitLanguage": "ch"
        }
    }
}, ensure_ascii=False)


async def create_dashboard(
    name: str, pid: int, node_type: str = "leaf", dv_type: str = "dashboard"
) -> str:
    resp = await de_client.post(
        "/dataVisualization/saveCanvas",
        {
            "name": name,
            "pid": pid,
            "nodeType": node_type,
            "type": dv_type,
            "busiFlag": dv_type,
            "canvasStyleData": _DEFAULT_CANVAS_STYLE,
            "componentData": "[]",
            "canvasViewInfo": {},
            "mobileLayout": False,
            "selfWatermarkStatus": False,
            "checkVersion": _de_config.DE_VERSION,
            "watermarkInfo": None,
            "status": 0,
            "contentId": str(_uuid.uuid4()),
        },
    )
    return resp


async def update_dashboard_name(dv_id: int, new_name: str) -> None:
    await de_client.post(
        "/dataVisualization/updateBase",
        {"id": dv_id, "name": new_name},
    )
    return None


async def delete_dashboard(dv_id: int) -> None:
    await de_client.post(
        f"/dataVisualization/deleteLogic/{dv_id}/core"
    )
    return None


async def set_publish_status(dv_id: int, status: int) -> None:
    from ..client import de_client as _de_client
    ctx = {"id": dv_id, "status": status}
    try:
        snap = await _de_client.post(
            "/dataVisualization/findById",
            {"id": dv_id, "resourceTable": "snapshot", "source": "main_edit"},
        )
        if snap and snap.get("name"):
            ctx["name"] = snap["name"]
            components = _json.loads(
                snap.get("componentData")
                if isinstance(snap.get("componentData"), str)
                else "[]"
            )
            active_ids = [
                str(c["id"])
                for c in components
                if c.get("component") == "UserView"
                and isinstance(c.get("id"), (int, str))
            ]
            ctx["activeViewIds"] = active_ids
            ctx["mobileLayout"] = snap.get("mobileLayout", False)
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning("set_publish_status snapshot lookup failed: %s", e)
    result = await de_client.post("/dataVisualization/updatePublishStatus", ctx)
    if status == 1:
        await _de_client.post(
            "/dataVisualization/findById",
            {"id": dv_id, "resourceTable": "snapshot", "source": "main_edit"},
        )
    status_map = {0: "已取消发布", 1: "已发布", 2: "已保存未发布"}
    return {"success": True, "dv_id": dv_id, "status": status, "status_text": status_map.get(status, str(status)), "result": result}


async def copy_dashboard(
    source_dv_id: int, target_pid: int, new_name: str = ""
) -> str:
    body = {
        "id": source_dv_id,
        "pid": target_pid,
        "optType": "copy",
    }
    if new_name:
        body["name"] = new_name
    resp = await de_client.post("/dataVisualization/copy", body)
    return resp
