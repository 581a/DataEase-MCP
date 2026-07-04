"""Add chart to dashboard canvas directly."""
import asyncio
import json
from src.dataease_mcp.client import de_client

async def main():
    dv_id = 1270730479120814080
    chart_id = 1270731968736268288

    # Get dashboard detail
    detail = await de_client.post(
        "/dataVisualization/findById",
        {"id": dv_id, "resourceTable": "snapshot", "source": "main_edit"},
    )
    if not detail:
        print("Dashboard not found")
        return

    # Parse existing component data
    comp_data_str = detail.get("componentData", "[]")
    if isinstance(comp_data_str, str):
        components = json.loads(comp_data_str)
    else:
        components = comp_data_str or []

    # Update chart title via POST /chart/save
    chart_detail = await de_client.post(f"/chart/getDetail/{chart_id}/snapshot")
    if chart_detail.get("title") is None:
        chart_detail["title"] = "批次不良报废组合图"
        resp = await de_client.post("/chart/save", chart_detail)
        print(f"Chart title fixed: {json.dumps(resp, indent=2, ensure_ascii=False)[:200]}")
    else:
        print(f"Chart title OK: {chart_detail.get('title')}")

    # Check if chart already in components
    cid_str = str(chart_id)
    existing = [c for c in components if str(c.get("id")) == cid_str]
    if existing:
        print(f"Chart {chart_id} already in canvas, updating position")
        existing[0]["x"] = 1
        existing[0]["y"] = 1
        existing[0]["sizeX"] = 50
        existing[0]["sizeY"] = 30
    else:
        # Create component entry
        new_comp = {
            "animations": [],
            "canvasId": "canvas-main",
            "events": {"checked": False, "showTips": False, "type": "jump", "typeList": [{"key": "jump", "label": "jump"}, {"key": "download", "label": "download"}]},
            "carousel": {"enable": False, "time": 10},
            "multiDimensional": {"enable": False, "x": 0, "y": 0, "z": 0},
            "groupStyle": {},
            "isLock": False, "maintainRadio": False, "aspectRatio": 1,
            "isShow": True, "dashboardHidden": False, "category": "base",
            "dragging": False, "resizing": False,
            "collapseName": ["position", "background", "style", "picture", "frameLinks", "videoLinks", "streamLinks", "carouselInfo", "events", "decoration_style"],
            "linkage": {"duration": 0, "data": [{"id": "", "label": "", "event": "", "style": [{"key": "", "value": ""}]}]},
            "component": "UserView", "name": "批次不良报废组合图", "label": "组合图",
            "propValue": {}, "icon": "chart-mix", "innerType": "chart-mix",
            "editing": False, "canvasActive": False,
            "actionSelection": {"linkageActive": "custom"},
            "x": 1, "y": 1, "sizeX": 50, "sizeY": 30,
            "style": {"rotate": 0, "opacity": 1, "borderActive": False, "borderWidth": 1, "borderRadius": 5, "borderStyle": "solid", "borderColor": "rgba(204, 204, 204, 1)"},
            "matrixStyle": {},
            "commonBackground": {"backgroundColorSelect": True, "backdropFilterEnable": False, "backgroundImageEnable": False, "backgroundType": "innerImage", "innerImage": "board/board_1280_720.png"},
            "state": "ready", "render": "antv", "isPlugin": False,
            "id": cid_str,
            "_dragId": 0, "show": True, "linkageFilters": [], "expand": False,
            "resizeInnerKeep": False, "title": "批次不良报废组合图",
        }
        components.append(new_comp)
        print(f"Added chart {chart_id} to canvas")

    # Update componentData and canvasViewInfo
    detail["componentData"] = json.dumps(components, ensure_ascii=False)

    # Update canvasViewInfo to include chart info
    canvas_view_info = detail.get("canvasViewInfo", {}) or {}
    canvas_view_info[cid_str] = {
        "id": cid_str,
        "name": "批次不良报废组合图",
        "title": "批次不良报废组合图",
        "tableId": "1257777977563942912",
        "type": "chart-mix",
        "render": "antv",
        "resultMode": "custom",
        "resultCount": 1000,
    }
    detail["canvasViewInfo"] = canvas_view_info

    # Save
    resp = await de_client.post("/dataVisualization/updateCanvas", detail)
    print(f"Canvas updated: {json.dumps(resp, indent=2, ensure_ascii=False)[:300] if resp else 'OK'}")

asyncio.run(main())
