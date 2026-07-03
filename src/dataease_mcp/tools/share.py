from ..client import de_client


async def get_share_info(resource_id: int = 0) -> dict:
    if resource_id:
        status = await de_client.get(f"/share/status/{resource_id}")
        detail = await de_client.get(f"/share/detail/{resource_id}")
        return {"status": status, "detail": detail}
    resp = await de_client.post("/share/query", {})
    return resp


async def configure_share(
    resource_id: int,
    action: str = "toggle",
    expiry_timestamp: int = 0,
    password: str = "",
) -> None:
    if action == "toggle":
        await de_client.post(f"/share/switcher/{resource_id}")
    elif action == "expiry":
        await de_client.post(
            "/share/editExp",
            {"resourceId": resource_id, "exp": expiry_timestamp},
        )
    elif action == "password":
        await de_client.post(
            "/share/editPwd",
            {"resourceId": resource_id, "pwd": password, "autoPwd": False},
        )
    return None
