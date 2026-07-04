"""Verify dashboard canvas."""
import asyncio
import json
from src.dataease_mcp.client import de_client

async def main():
    dv_id = 1270730479120814080
    chart_id = 1270731968736268288

    detail = await de_client.post(
        "/dataVisualization/findById",
        {"id": dv_id, "resourceTable": "snapshot", "source": "main_edit"},
    )
    
    print(f"Dashboard: {detail.get('name')}")
    print(f"Status: {detail.get('status')}")
    
    # Check componentData
    comp_data_str = detail.get("componentData", "[]")
    components = json.loads(comp_data_str) if isinstance(comp_data_str, str) else (comp_data_str or [])
    print(f"\nTotal components: {len(components)}")
    
    cid_str = str(chart_id)
    chart_comp = [c for c in components if str(c.get("id")) == cid_str]
    if chart_comp:
        print(f"Chart found on canvas: x={chart_comp[0].get('x')}, y={chart_comp[0].get('y')}, sizeX={chart_comp[0].get('sizeX')}, sizeY={chart_comp[0].get('sizeY')}")
    else:
        print("ERROR: Chart NOT found on canvas!")
        for c in components:
            print(f"  Component: id={c.get('id')}, name={c.get('name')}, type={c.get('component')}")
    
    # Check canvasViewInfo
    cvi = detail.get("canvasViewInfo", {})
    if cvi and cid_str in cvi:
        print(f"\nCanvasViewInfo OK for chart {chart_id}")
    else:
        print(f"\nWARNING: Chart not in canvasViewInfo")
        print(f"CanvasViewInfo keys: {list(cvi.keys()) if cvi else 'EMPTY'}")

asyncio.run(main())
