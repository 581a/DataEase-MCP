from ..client import de_client


async def get_export_info(
    status: str = "", page: int = 1, page_size: int = 20
) -> dict:
    tasks = await de_client.post(
        f"/exportCenter/exportTasks/{status or 'all'}/{page}/{page_size}"
    )
    try:
        stats = await de_client.post("/exportCenter/exportTasks/records")
        tasks["stats"] = stats if isinstance(stats, dict) else {}
    except Exception:
        pass
    return tasks


async def download_export_file(task_id: str) -> str:
    resp = await de_client.get(f"/exportCenter/generateDownloadUri/{task_id}")
    return resp


async def retry_export(task_id: str) -> None:
    await de_client.post(f"/exportCenter/retry/{task_id}")
    return None


async def delete_export_task(task_id: str) -> None:
    await de_client.get(f"/exportCenter/delete/{task_id}")
    return None
