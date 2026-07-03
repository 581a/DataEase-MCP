from ..client import de_client


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
        {"id": dv_id, "resourceTable": "core", "source": "main_edit"},
    )
    return resp


import json as _json

_DEFAULT_CANVAS_STYLE = _json.dumps(_json.loads(
    '{"width":1920,"height":1080,"scale":100,"scaleWidth":1920,"scaleHeight":1080,'
    '"refreshBrowserEnable":false,"refreshBrowserUnit":"minute","refreshBrowserTime":5,'
    '"refreshViewEnable":false,"refreshViewLoading":true,"refreshUnit":"minute",'
    '"refreshTime":5,"popupAvailable":true,"popupButtonAvailable":true,'
    '"suspensionButtonAvailable":false,"screenAdaptor":true,"bgColorSet":false,'
    '"bgColor":"rgba(20,20,22,0)","bgPictureSet":false,"bgPictureUrl":"",'
    '"auxiliaryMatrix":false,"openCommonStyle":false,"commonStyle":{},'
    '"showWatermark":false,"watermarkInfo":{}}'
))


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
            "canvasStyleData": _DEFAULT_CANVAS_STYLE,
            "componentData": "[]",
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
                int(c["id"])
                for c in components
                if c.get("component") == "UserView"
                and isinstance(c.get("id"), (int, str))
            ]
            ctx["activeViewIds"] = active_ids
            ctx["mobileLayout"] = snap.get("mobileLayout", False)
    except Exception:
        pass
    await de_client.post("/dataVisualization/updatePublishStatus", ctx)
    if status == 1:
        await _de_client.post(
            "/dataVisualization/findById",
            {"id": dv_id, "resourceTable": "snapshot", "source": "main_edit"},
        )
    return None


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
