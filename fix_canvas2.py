"""Add chart to canvas using _save_dashboard_canvas logic."""
import asyncio
import json
from src.dataease_mcp.tools.canvas import _load_dashboard_canvas, _parse_component_data, _save_dashboard_canvas
from src.dataease_mcp.tools import chart as chart_tools

async def main():
    dv_id = 1270730479120814080
    chart_id = 1270731968736268288
    cid_str = str(chart_id)

    # Load dashboard
    detail = await _load_dashboard_canvas(dv_id)
    if not detail:
        print("Dashboard not found")
        return

    components = _parse_component_data(detail)
    
    # Check if chart already in components
    existing = [c for c in components if str(c.get("id")) == cid_str]
    if not existing:
        # Read chart detail to get type info
        cd = await chart_tools.get_chart_detail(chart_id, "snapshot")
        chart_type = cd.get("type", "chart-mix") if cd else "chart-mix"
        
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
            "propValue": {}, "icon": "chart-mix", "innerType": chart_type,
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
        print(f"Added chart {chart_id} to components")

    # Save using _save_dashboard_canvas which properly builds canvasViewInfo
    result = await _save_dashboard_canvas(dv_id, components, detail)
    print(f"Save result: {json.dumps(result, ensure_ascii=False)[:200] if result else 'OK'}")
    
    # Verify
    detail2 = await _load_dashboard_canvas(dv_id)
    cvi = detail2.get("canvasViewInfo", {})
    if cid_str in cvi:
        print(f"SUCCESS: canvasViewInfo has chart {chart_id}")
    else:
        print(f"FAILED: canvasViewInfo missing chart. Keys: {list(cvi.keys()) if cvi else 'EMPTY'}")

asyncio.run(main())
