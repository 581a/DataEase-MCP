"""Find exact culprit field in canvasViewInfo."""
import asyncio
import json
import httpx
from src.dataease_mcp.client import de_client
from src.dataease_mcp.auth import auth_manager
from src.dataease_mcp.config import config

async def test_cvi(cvi, label):
    dv_id = 1270737895161991168
    detail = await de_client.post("/dataVisualization/findById", {"id": dv_id, "resourceTable": "snapshot", "source": "main_edit"})
    cs = detail.get("canvasStyleData", "{}")
    if isinstance(cs, dict): cs = json.dumps(cs, ensure_ascii=False)
    base = {"id": dv_id, "pid": 0, "name": "MCP-测试", "nodeType": "leaf",
            "type": "dashboard", "busiFlag": "dashboard", "status": 2,
            "selfWatermarkStatus": False, "mobileLayout": False, "contentId": "0",
            "canvasStyleData": cs, "componentData": "[]",
            "orgId": 0, "level": 0, "extFlag": 0}

    client = httpx.AsyncClient(timeout=30)
    try:
        token = await auth_manager.ensure_auth(client)
        headers = {config.TOKEN_KEY: token, "Content-Type": "application/json"}
        resp = await client.post("http://10.40.9.211:8100/de2api/dataVisualization/updateCanvas", headers=headers, json={**base, "canvasViewInfo": cvi})
        ok = resp.status_code == 200 and '"code":0' in resp.text
        print(f"  {label}: {'OK' if ok else 'FAIL'} {resp.text[:100]}")
        return ok
    finally:
        await client.aclose()

async def main():
    chart_id = 1270737991249301504
    cid_str = str(chart_id)
    cd = await de_client.post(f"/chart/getDetail/{chart_id}/snapshot")

    # Test: minimal + each problematic field individually  
    base_cvi = {"id": chart_id, "title": "test", "type": "chart-mix", "tableId": "1257777977563942912", "render": "antv",
                "xAxis": cd.get("xAxis", []), "yAxis": cd.get("yAxis", [])}

    # Test 1: base only
    await test_cvi({cid_str: base_cvi}, "base")

    # Test 2: base + yAxisExt with extField=2
    yae2 = [{"id": "7466056608787730432", "name": "批次不良报废率","dataeaseName": "f_a057d813d58089f8","groupType":"q","deType":3,"extField":2}]
    await test_cvi({cid_str: {**base_cvi, "yAxisExt": yae2}}, "+yAxisExt(extField=2)")

    # Test 3: base + yAxisExt with extField=0
    yae0 = [{"id": "7466056608787730432", "name": "批次不良报废率","dataeaseName": "f_a057d813d58089f8","groupType":"q","deType":3,"extField":0}]
    await test_cvi({cid_str: {**base_cvi, "yAxisExt": yae0}}, "+yAxisExt(extField=0)")

    # Test 4: base + yAxisExt without extField
    yaen = [{"id": "7466056608787730432", "name": "批次不良报废率","dataeaseName": "f_a057d813d58089f8","groupType":"q","deType":3}]
    await test_cvi({cid_str: {**base_cvi, "yAxisExt": yaen}}, "+yAxisExt(no extField)")

    # Test 5: base + extStack
    await test_cvi({cid_str: {**base_cvi, "extStack": [1,2,3]}}, "+extStack")

    # Test 6: what if we also pass dataeaseName in yAxisExt
    yaen2 = [{"id": "7466056608787730432", "name": "批次不良报废率","dataeaseName": "f_a057d813d58089f8","extField": 2}]
    await test_cvi({cid_str: {**base_cvi, "yAxisExt": yaen2}}, "+yAxisExt(extField=2,no groupType)")

asyncio.run(main())
