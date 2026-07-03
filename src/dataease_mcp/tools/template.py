from ..client import de_client


async def list_templates(keyword: str = "", source: str = "local") -> dict:
    if source == "market":
        resp = await de_client.get("/templateMarket/search")
    else:
        resp = await de_client.post(
            "/templateManage/templateList",
            {"keyword": keyword, "withChildren": True},
        )
    return resp


async def get_template_detail(
    template_id: str, preview: bool = False
) -> dict:
    if preview:
        resp = await de_client.get("/templateMarket/searchPreview")
    else:
        resp = await de_client.get(f"/templateManage/findOne/{template_id}")
    return resp


async def apply_template(
    template_id: str, target_pid: int, new_name: str
) -> str:
    resp = await de_client.post(
        "/dataVisualization/decompression",
        {
            "id": template_id,
            "pid": target_pid,
            "name": new_name,
            "optType": "insert",
            "newFrom": "new_inner_template",
        },
    )
    return resp
