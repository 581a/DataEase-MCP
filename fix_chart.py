"""Fix chart: add right axis (yAxisExt) for chart-mix combo chart."""
import asyncio
import json
from src.dataease_mcp.client import de_client

async def main():
    chart_id = 1270731968736268288

    # Get existing chart detail
    detail = await de_client.post(f"/chart/getDetail/{chart_id}/snapshot")

    # Define right axis field (批次不良报废率)
    right_axis_field = {
        "id": "7466056608787730432",
        "name": "批次不良报废率",
        "dataeaseName": "f_a057d813d58089f8",
        "groupType": "q",
        "deType": 3,
        "extField": 2,
        "originName": "批次不良报废率",
        "summary": "sum",
        "sort": "none",
        "dateStyle": "y_M_d",
        "datePattern": "date_sub",
        "dateShowFormat": "y_M_d",
        "chartType": "chart-mix",
        "filter": [],
        "compareCalc": {"type": "none"},
        "formatterCfg": {"type": "auto", "unitLanguage": "ch"},
    }

    # Add to yAxisExt
    detail["yAxisExt"] = [right_axis_field]

    # Also add to viewFields if not already present
    existing_ids = {vf.get("id") for vf in detail.get("viewFields", [])}
    if "7466056608787730432" not in existing_ids:
        vf = right_axis_field.copy()
        vf["groupType"] = "q"
        vf["checked"] = True
        vf["extField"] = 2
        detail.get("viewFields", []).append(vf)

    # Save updated chart
    resp = await de_client.post("/chart/save", detail)
    print(f"Chart updated: {json.dumps(resp, indent=2, ensure_ascii=False)[:500]}")
    print(f"yAxisExt: {json.dumps(detail.get('yAxisExt'), ensure_ascii=False)}")

asyncio.run(main())
