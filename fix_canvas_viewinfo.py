"""Verify and fix canvasViewInfo."""
import asyncio
import json
from src.dataease_mcp.client import de_client

async def main():
    dv_id = 1270730479120814080
    chart_id = 1270731968736268288
    cid_str = str(chart_id)

    # Get dashboard snapshot detail 
    detail = await de_client.post(
        "/dataVisualization/findById",
        {"id": dv_id, "resourceTable": "snapshot", "source": "main_edit"},
    )
    
    print(f"Dashboard: {detail.get('name')}, status={detail.get('status')}")
    
    # Check canvasViewInfo
    cvi = detail.get("canvasViewInfo", {})
    print(f"canvasViewInfo type: {type(cvi).__name__}, value: {json.dumps(cvi, ensure_ascii=False)[:200] if cvi else 'EMPTY'}")
    
    if not cvi or cid_str not in cvi:
        print("Fixing canvasViewInfo...")
        detail["canvasViewInfo"] = {
            cid_str: {
                "id": cid_str,
                "name": "批次不良报废组合图",
                "title": "批次不良报废组合图",
                "tableId": "1257777977563942912",
                "type": "chart-mix",
                "render": "antv",
                "resultMode": "custom",
                "resultCount": 1000,
            }
        }
        resp = await de_client.post("/dataVisualization/updateCanvas", detail)
        print(f"updateCanvas result: status={resp.get('status') if resp else 'OK'}")
        
        # Re-read to confirm
        detail2 = await de_client.post(
            "/dataVisualization/findById",
            {"id": dv_id, "resourceTable": "snapshot", "source": "main_edit"},
        )
        cvi2 = detail2.get("canvasViewInfo", {})
        print(f"After fix - canvasViewInfo: {json.dumps(cvi2, ensure_ascii=False)[:300] if cvi2 else 'STILL EMPTY!'}")

asyncio.run(main())
