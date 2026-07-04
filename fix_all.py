"""Build canvasViewInfo avoiding extField=2 issue."""
import asyncio
import json
from src.dataease_mcp.client import de_client
from src.dataease_mcp.tools.canvas import _load_dashboard_canvas, _parse_component_data, _save_dashboard_canvas

async def main():
    dv_id = 1270737895161991168
    chart_id = 1270737991249301504
    cid_str = str(chart_id)

    # Step 1: Fix chart - add right axis 
    print("Step 1: Adding right axis yAxisExt...")
    detail = await de_client.post(f"/chart/getDetail/{chart_id}/snapshot")
    
    right_axis_field = {
        "id": "7466056608787730432", "name": "批次不良报废率",
        "dataeaseName": "f_a057d813d58089f8", "groupType": "q",
        "deType": 3, "extField": 2, "originName": "批次不良报废率",
        "summary": "sum", "sort": "none", "dateStyle": "y_M_d",
        "datePattern": "date_sub", "dateShowFormat": "y_M_d",
        "chartType": "chart-mix", "filter": [],
        "compareCalc": {"type": "none"},
        "formatterCfg": {"type": "auto", "unitLanguage": "ch"},
    }
    detail["yAxisExt"] = [right_axis_field]
    existing_ids = {vf.get("id") for vf in detail.get("viewFields", [])}
    if "7466056608787730432" not in existing_ids:
        vf = right_axis_field.copy()
        vf["checked"] = True
        detail["viewFields"].append(vf)
    await de_client.post("/chart/save", detail)
    print("  Chart yAxisExt set OK")

    # Step 2: Load dashboard, add component
    print("Step 2: Adding chart to canvas...")
    dashboard = await _load_dashboard_canvas(dv_id)
    components = _parse_component_data(dashboard)
    
    new_comp = {
        "animations":[],"canvasId":"canvas-main",
        "events":{"checked":False,"showTips":False,"type":"jump","typeList":[{"key":"jump","label":"jump"},{"key":"download","label":"download"}]},
        "carousel":{"enable":False,"time":10},
        "multiDimensional":{"enable":False,"x":0,"y":0,"z":0},
        "groupStyle":{},"isLock":False,"maintainRadio":False,"aspectRatio":1,
        "isShow":True,"dashboardHidden":False,"category":"base",
        "dragging":False,"resizing":False,
        "collapseName":["position","background","style","picture","frameLinks","videoLinks","streamLinks","carouselInfo","events","decoration_style"],
        "linkage":{"duration":0,"data":[{"id":"","label":"","event":"","style":[{"key":"","value":""}]}]},
        "component":"UserView","name":"批次不良报废组合图","label":"组合图",
        "propValue":{},"icon":"chart-mix","innerType":"chart-mix",
        "editing":False,"canvasActive":False,"actionSelection":{"linkageActive":"custom"},
        "x":1,"y":1,"sizeX":50,"sizeY":30,
        "style":{"rotate":0,"opacity":1,"borderActive":False,"borderWidth":1,"borderRadius":5,"borderStyle":"solid","borderColor":"rgba(204,204,204,1)"},
        "matrixStyle":{},
        "commonBackground":{"backgroundColorSelect":True,"backdropFilterEnable":False,"backgroundImageEnable":False,"backgroundType":"innerImage","innerImage":"board/board_1280_720.png"},
        "state":"ready","render":"antv","isPlugin":False,
        "id":cid_str,"_dragId":0,"show":True,"linkageFilters":[],"expand":False,
        "resizeInnerKeep":False,"title":"批次不良报废组合图",
    }
    components.append(new_comp)

    # Override _save_dashboard_canvas behavior: strip extField>=2 from yAxisExt in canvasViewInfo
    cd = await de_client.post(f"/chart/getDetail/{chart_id}/snapshot")
    canvas_view_info = {}
    if cd:
        cvi_data = {
            "id": chart_id, "title": cd.get("title", "批次不良报废组合图"),
            "sceneId": dv_id, "tableId": cd.get("tableId"),
            "type": cd.get("type", "chart-mix"), "render": cd.get("render", "antv"),
            "xAxis": cd.get("xAxis", []), "yAxis": cd.get("yAxis", []),
            "xAxisExt": cd.get("xAxisExt", []),
            "extStack": cd.get("extStack", []), "extBubble": cd.get("extBubble", []),
            "extLabel": cd.get("extLabel", []), "extTooltip": cd.get("extTooltip", []),
            "extColor": cd.get("extColor", []), "drillFields": cd.get("drillFields", []),
            "customAttr": cd.get("customAttr", {}), "customStyle": cd.get("customStyle", {}),
            "senior": cd.get("senior", {}), "stylePriority": "view",
            "isPlugin": False, "refreshViewEnable": False,
            "linkageActive": False, "jumpActive": False, "aggregate": False,
            "dataFrom": "dataset", "resultMode": "custom", "resultCount": 1000,
        }
        # Strip extField>=2 fields from yAxisExt to avoid backend base64 error
        yae = cd.get("yAxisExt", [])
        if yae:
            cleaned = []
            for f in yae:
                if isinstance(f, dict) and f.get("extField", 0) >= 2:
                    # Replace with a clean version: set extField=0 and keep dataeaseName clean
                    clean_f = dict(f)
                    clean_f["extField"] = 0
                    cleaned.append(clean_f)
                else:
                    cleaned.append(f)
            cvi_data["yAxisExt"] = cleaned
        else:
            cvi_data["yAxisExt"] = []
        canvas_view_info[cid_str] = cvi_data

    # Build body manually with cleaned canvasViewInfo
    import json as _json
    dv_type = dashboard.get("type", "dashboard")
    canvas_style = dashboard.get("canvasStyleData") or "{}"
    if isinstance(canvas_style, dict):
        canvas_style = _json.dumps(canvas_style, ensure_ascii=False)
    
    body = {
        "id": dashboard.get("id", dv_id), "pid": dashboard.get("pid", 0),
        "name": dashboard.get("name", ""), "nodeType": dashboard.get("nodeType", "leaf"),
        "type": dv_type, "busiFlag": dv_type,
        "status": dashboard.get("status", 1),
        "selfWatermarkStatus": dashboard.get("selfWatermarkStatus", False),
        "mobileLayout": dashboard.get("mobileLayout", False),
        "contentId": dashboard.get("contentId") or "",
        "componentData": _json.dumps(components, separators=(",",":"), ensure_ascii=False),
        "canvasStyleData": canvas_style,
        "canvasViewInfo": canvas_view_info,
        "orgId": dashboard.get("orgId", 0), "level": dashboard.get("level", 0),
        "extFlag": dashboard.get("extFlag", 0),
    }
    
    result = await de_client.post("/dataVisualization/updateCanvas", body)
    print(f"  Canvas save: {'OK' if result else 'FAILED'}")
    if not result:
        return
    
    # Verify
    dash2 = await _load_dashboard_canvas(dv_id)
    cvi = dash2.get("canvasViewInfo", {})
    print(f"  canvasViewInfo has chart: {cid_str in cvi}")

    # Step 3: Publish
    print("Step 3: Publishing...")
    pub_ctx = {
        "id": dv_id, "status": 1, "name": "MCP-测试",
        "activeViewIds": [chart_id],
        "mobileLayout": dashboard.get("mobileLayout", False),
    }
    result2 = await de_client.post("/dataVisualization/updatePublishStatus", pub_ctx)
    print(f"  Published: {result2}")

asyncio.run(main())
