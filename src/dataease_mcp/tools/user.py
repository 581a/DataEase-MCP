from ..client import de_client


async def list_users(
    keyword: str = "", page: int = 1, page_size: int = 20
) -> dict:
    resp = await de_client.post(
        f"/user/pager/{page}/{page_size}",
        {"keyword": keyword},
    )
    return resp


async def get_user_info(user_id: int = 0) -> dict:
    if user_id:
        detail = await de_client.get(f"/user/queryById/{user_id}")
        return detail
    info = await de_client.get("/user/info")
    count = await de_client.get("/user/userCount")
    info["total_count"] = count
    return info


async def create_user(
    name: str,
    account: str,
    email: str,
    role_ids: list[int],
    enabled: bool = True,
) -> int:
    body = {
        "name": name,
        "account": account,
        "email": email,
        "roleIds": role_ids,
        "enable": enabled,
    }
    resp = await de_client.post("/user/create", body)
    return resp


async def edit_user(
    user_id: int,
    name: str = "",
    email: str = "",
    role_ids: list[int] | None = None,
) -> None:
    body = {"id": user_id}
    if name:
        body["name"] = name
    if email:
        body["email"] = email
    if role_ids is not None:
        body["roleIds"] = role_ids
    await de_client.post("/user/edit", body)
    return None


async def delete_user(user_id: int) -> None:
    await de_client.post(f"/user/delete/{user_id}")
    return None


async def enable_user(user_id: int, enabled: bool) -> None:
    await de_client.post(
        "/user/enable",
        {"id": user_id, "enable": enabled},
    )
    return None
