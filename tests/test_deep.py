import asyncio
import json
from dataease_mcp.tools import (
    dashboard,
    dataset,
    datasource,
    chart,
)

results = {}


async def run_test(name, coro):
    try:
        result = await coro
        results[name] = {"status": "PASS", "result": result}
        print(f"  [PASS] {name}")
        return result
    except Exception as e:
        results[name] = {"status": "FAIL", "error": str(e)}
        print(f"  [FAIL] {name}: {e}")
        return None


async def main():
    print("=" * 60)
    print("DataEase MCP Server - 深度功能测试")
    print("=" * 60)

    print("\n--- 1. 探索数据源 ---")
    ds_tree = await run_test("list_datasources", datasource.list_datasources())
    if ds_tree and len(ds_tree) > 0:
        children = ds_tree[0].get("children", []) if ds_tree else []
        print(f"  数据源子节点数量: {len(children)}")
        for child in children[:5]:
            ctype = child.get("nodeType", "?")
            cname = child.get("name", "?")
            cid = child.get("id", "?")
            print(f"    [{ctype}] {cname} (id={cid})")

        datasource_items = [
            c for c in children if c.get("nodeType") == "datasource"
        ]
        if datasource_items:
            ds_id = datasource_items[0]["id"]
            print(f"\n  测试数据源详情 (ds_id={ds_id})")
            await run_test("get_datasource_detail", datasource.get_datasource_detail(ds_id))
            await run_test("get_datasource_tables", datasource.get_datasource_tables(ds_id))
            await run_test("test_connection", datasource.test_datasource_connection(ds_id))

    print("\n--- 2. 探索数据集 ---")
    dsets = await run_test("list_datasets", dataset.list_datasets())
    if dsets and len(dsets) > 0:
        children = dsets[0].get("children", []) if dsets else []
        print(f"  数据集子节点数量: {len(children)}")
        for child in children[:5]:
            ctype = child.get("nodeType", "?")
            cname = child.get("name", "?")
            cid = child.get("id", "?")
            print(f"    [{ctype}] {cname} (id={cid})")

        dataset_items = [
            c for c in children if c.get("nodeType") == "dataset"
        ]
        if dataset_items:
            d_id = dataset_items[0]["id"]
            print(f"\n  测试数据集详情 (dataset_id={d_id})")
            await run_test("get_dataset_detail", dataset.get_dataset_detail(d_id))
            await run_test("get_dataset_fields", dataset.get_dataset_fields(d_id))
            await run_test("get_dataset_count", dataset.get_dataset_count(d_id))

    print("\n--- 3. 探索仪表板 ---")
    panels = await run_test(
        "list_dashboards_all",
        dashboard.list_dashboards("", "dashboard"),
    )
    if panels and len(panels) > 0:
        children = panels[0].get("children", []) if panels else []
        print(f"  仪表板子节点数量: {len(children)}")
        for child in children[:5]:
            ctype = child.get("nodeType", "?")
            cname = child.get("name", "?")
            cid = child.get("id", "?")
            print(f"    [{ctype}] {cname} (id={cid})")

        leaf_items = [c for c in children if c.get("nodeType") == "leaf"]
        if leaf_items:
            dv_id = leaf_items[0]["id"]
            print(f"\n  测试仪表板详情 (dv_id={dv_id})")
            await run_test("get_dashboard_detail", dashboard.get_dashboard_detail(dv_id))
            await run_test("get_dashboard_views", chart.get_dashboard_views(dv_id))

    print("\n--- 4. 数据预览测试 ---")
    ds_tree2 = await datasource.list_datasources()
    if ds_tree2:
        children = ds_tree2[0].get("children", []) if ds_tree2 else []
        ds_items = [c for c in children if c.get("nodeType") == "datasource"]
        if ds_items:
            ds_id = ds_items[0]["id"]
            tables = await datasource.get_datasource_tables(ds_id)
            if tables and len(tables) > 0:
                table_name = tables[0].get("name", tables[0].get("tableName", ""))
                if table_name:
                    print(f"  预览表 {table_name}")
                    await run_test("preview_table_data", datasource.preview_table_data(ds_id, table_name))
                    await run_test("get_table_fields", datasource.get_table_fields(ds_id, table_name))

    print("\n" + "=" * 60)
    print("深度测试结果汇总")
    print("=" * 60)
    passed = sum(1 for r in results.values() if r["status"] == "PASS")
    failed = sum(1 for r in results.values() if r["status"] == "FAIL")
    print(f"通过: {passed}, 失败: {failed}, 总计: {len(results)}")

    for name, r in results.items():
        icon = "[OK]" if r["status"] == "PASS" else "[FAIL]"
        print(f"  {icon} {name}")

    with open("test_deep_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)


if __name__ == "__main__":
    asyncio.run(main())
