from ..client import de_client


async def list_datasets(keyword: str = "", pid: int = 0) -> list:
    resp = await de_client.post(
        "/datasetTree/tree", {"keyword": keyword, "pid": pid}
    )
    return resp


async def get_dataset_info(dataset_id: int) -> dict:
    detail = await de_client.post(f"/datasetTree/details/{dataset_id}")
    if not detail:
        return {}
    result = {
        "id": detail.get("id"),
        "name": detail.get("name"),
        "pid": detail.get("pid"),
        "nodeType": detail.get("nodeType"),
        "type": detail.get("type"),
        "mode": detail.get("mode"),
        "status": detail.get("status"),
    }
    try:
        fields = await de_client.post(f"/datasetField/listByDatasetGroup/{dataset_id}")
        result["fields"] = fields if isinstance(fields, list) else []
    except Exception:
        result["fields"] = []
    try:
        count = await de_client.post("/datasetData/getDatasetCount", {"id": dataset_id})
        result["data_count"] = count
    except Exception:
        result["data_count"] = None
    return result


async def get_field_enum_values(
    dataset_id: int, field_ids: list[int]
) -> list:
    resp = await de_client.post(
        "/datasetData/enumValue",
        {"datasetId": dataset_id, "fieldIds": field_ids},
    )
    return resp


async def preview_dataset_data(
    dataset_id: int, limit: int = 100
) -> dict:
    import json as _json

    detail = await de_client.post(f"/datasetTree/details/{dataset_id}")
    if not detail:
        return {"error": "数据集不存在"}

    def _fix_ids(obj):
        if isinstance(obj, dict):
            result = {}
            for k, v in obj.items():
                if k == "info" and isinstance(v, dict):
                    result[k] = _json.dumps(_fix_ids(v), ensure_ascii=False)
                elif k == "info" and isinstance(v, list):
                    result[k] = _json.dumps(_fix_ids(v), ensure_ascii=False)
                else:
                    result[k] = _fix_ids(v)
            if "id" in result and isinstance(result["id"], str):
                try:
                    result["id"] = int(result["id"])
                except (ValueError, TypeError):
                    pass
            if "datasourceId" in result and isinstance(result["datasourceId"], str):
                try:
                    result["datasourceId"] = int(result["datasourceId"])
                except (ValueError, TypeError):
                    pass
            if "datasetTableId" in result and isinstance(result["datasetTableId"], str):
                try:
                    result["datasetTableId"] = int(result["datasetTableId"])
                except (ValueError, TypeError):
                    pass
            if "datasetId" in result and isinstance(result["datasetId"], str):
                try:
                    result["datasetId"] = int(result["datasetId"])
                except (ValueError, TypeError):
                    pass
            return result
        elif isinstance(obj, list):
            return [_fix_ids(item) for item in obj]
        return obj

    raw_info = detail.get("info", "")
    if isinstance(raw_info, str):
        info_str = raw_info
    else:
        info_str = _json.dumps(_fix_ids(raw_info), ensure_ascii=False)

    all_fields = _fix_ids(detail.get("allFields") or detail.get("allfields") or [])
    if isinstance(all_fields, list):
        for f in all_fields:
            if isinstance(f, dict):
                if f.get("extField") is None:
                    f["extField"] = 0
                if f.get("originName") is None:
                    f["originName"] = f.get("dataeaseName") or f.get("name", "")
                if f.get("dataeaseName") is None:
                    f["dataeaseName"] = f.get("name", "")
                if f.get("deType") is None:
                    f["deType"] = 0

    body = {
        "id": detail.get("id"),
        "pid": detail.get("pid", 0),
        "name": detail.get("name", ""),
        "nodeType": detail.get("nodeType", "dataset"),
        "type": detail.get("type", "db"),
        "mode": detail.get("mode", 0),
        "info": info_str,
        "allFields": all_fields,
        "sql": detail.get("sql", ""),
        "union": _fix_ids(detail.get("union", [])),
        "isCross": detail.get("isCross", False),
        "data": {"pageSize": limit, "currentPage": 1},
    }
    resp = await de_client.post("/datasetData/previewData", body)
    return resp


async def preview_sql(datasource_id: int, sql: str) -> dict:
    import base64

    body = {
        "datasourceId": datasource_id,
        "sql": base64.b64encode(sql.encode("utf-8")).decode("utf-8"),
        "isCross": False,
    }
    resp = await de_client.post("/datasetData/previewSql", body)
    return resp


async def create_dataset(
    name: str,
    pid: int,
    node_type: str = "dataset",
    datasource_id: int = 0,
    sql: str = "",
) -> dict:
    if node_type == "folder" or (not sql and not datasource_id):
        resp = await de_client.post(
            "/datasetTree/create",
            {"name": name, "pid": pid, "nodeType": "folder"},
        )
        return resp
    import base64
    body = {
        "name": name,
        "pid": pid,
        "nodeType": "dataset",
        "type": "sql",
        "sql": sql,
        "union": [
            {
                "tableId": str(datasource_id),
                "datasourceId": str(datasource_id),
                "sql": base64.b64encode(sql.encode("utf-8")).decode("utf-8"),
            }
        ],
    }
    resp = await de_client.post("/datasetTree/save", body)
    return resp


async def delete_dataset(dataset_id: int) -> None:
    await de_client.post(f"/datasetTree/delete/{dataset_id}")
    return None


async def rename_dataset(dataset_id: int, new_name: str) -> dict:
    resp = await de_client.post(
        "/datasetTree/rename", {"id": dataset_id, "name": new_name}
    )
    return resp


async def export_dataset(dataset_id: int) -> dict:
    resp = await de_client.post(
        "/datasetTree/exportDataset",
        {"id": dataset_id},
    )
    return resp
