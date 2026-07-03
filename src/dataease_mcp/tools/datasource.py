import json as json_mod

from ..client import de_client


async def list_datasources(keyword: str = "") -> list:
    resp = await de_client.post("/datasource/tree", {"keyword": keyword})
    return resp


async def list_datasource_types() -> list:
    resp = await de_client.get("/datasource/types")
    return resp


async def get_datasource_detail(ds_id: int, full: bool = False) -> dict:
    if full:
        resp = await de_client.get(f"/datasource/get/{ds_id}")
    else:
        resp = await de_client.get(f"/datasource/hidePw/{ds_id}")
    return resp


async def get_datasource_tables(
    ds_id: int, include_fields: bool = False
) -> list:
    resp = await de_client.post("/datasource/getTables", {"datasourceId": ds_id})
    if not include_fields or not resp or not isinstance(resp, list):
        return resp
    config = await de_client.get(f"/datasource/hidePw/{ds_id}")
    for table in resp:
        tname = table.get("tableName", table.get("name", ""))
        if not tname:
            continue
        try:
            fields = await get_table_fields(ds_id, tname)
            if isinstance(fields, list):
                table["fields"] = [
                    {
                        "name": f.get("name") or f.get("originName", "?"),
                        "type": f.get("type") or f.get("deType", "?"),
                        "origin_name": f.get("originName") or f.get("name", ""),
                        "raw": {k: v for k, v in f.items()
                                if k in ("id", "name", "originName", "type",
                                         "deType", "dataeaseName", "groupType",
                                         "description", "dateFormat", "precision",
                                         "scale", "extField", "checked")},
                    }
                    for f in fields
                ]
            else:
                table["fields"] = []
        except Exception:
            table["fields"] = ["unavailable"]
    return resp


async def get_table_fields(ds_id: int, table_name: str) -> list:
    resp = await de_client.post(
        "/datasource/getTableField",
        {"tableName": table_name, "datasourceId": str(ds_id)},
    )
    return resp


async def preview_table_data(ds_id: int, table_name: str) -> dict:
    resp = await de_client.post(
        "/datasource/previewData",
        {"table": table_name, "id": str(ds_id)},
    )
    return resp


async def test_datasource_connection(ds_id: int) -> dict:
    resp = await de_client.get(f"/datasource/validate/{ds_id}")
    return resp


async def create_datasource_folder(name: str, pid: int = 0) -> dict:
    resp = await de_client.post(
        "/datasource/createFolder",
        {"name": name, "pid": pid, "nodeType": "folder"},
    )
    return resp


async def rename_datasource(ds_id: int, new_name: str) -> dict:
    resp = await de_client.post(
        "/datasource/reName",
        {"id": ds_id, "name": new_name},
    )
    return resp


async def delete_datasource(ds_id: int) -> None:
    await de_client.get(f"/datasource/delete/{ds_id}")
    return None


async def create_datasource(
    name: str,
    pid: int,
    ds_type: str,
    configuration: str,
    description: str = "",
) -> dict:
    body = {
        "name": name,
        "pid": pid,
        "nodeType": "datasource",
        "type": ds_type,
        "configuration": configuration,
        "description": description,
    }
    resp = await de_client.post("/datasource/save", body)
    return resp


async def update_datasource(
    ds_id: int,
    configuration: str,
    ds_type: str,
    name: str = "",
) -> dict:
    body = {
        "id": ds_id,
        "nodeType": "datasource",
        "type": ds_type,
        "configuration": configuration,
    }
    if name:
        body["name"] = name
    resp = await de_client.post("/datasource/update", body)
    return resp
