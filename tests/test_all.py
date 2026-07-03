import asyncio
import json
from dataease_mcp.tools import (
    dashboard,
    dataset,
    datasource,
    chart,
    user,
    share,
    export as export_tools,
    template,
)

TEST_FOLDER = "MCP_TEST"
results = {}


async def run_test(name, coro):
    try:
        result = await coro
        results[name] = {"status": "PASS", "result": result}
        print(f"  [PASS] {name}")
    except Exception as e:
        results[name] = {"status": "FAIL", "error": str(e)}
        print(f"  [FAIL] {name}: {e}")


async def main():
    print("=" * 60)
    print("DataEase MCP Server - 功能测试")
    print("=" * 60)

    print("\n--- 1. 用户管理 ---")
    await run_test("get_current_user", user.get_current_user())
    await run_test("get_user_count", user.get_user_count())
    await run_test("list_users", user.list_users("admin"))

    print("\n--- 2. 数据源管理 ---")
    await run_test("list_datasources", datasource.list_datasources())
    await run_test("get_datasource_types", datasource.list_datasource_types())

    print("\n--- 3. 数据集管理 ---")
    await run_test("list_datasets", dataset.list_datasets())

    print("\n--- 4. 仪表板管理 ---")
    await run_test("list_dashboards", dashboard.list_dashboards())

    print("\n--- 5. 导出中心 ---")
    await run_test("get_export_stats", export_tools.get_export_stats())
    await run_test("list_export_tasks", export_tools.list_export_tasks("all", 1, 10))

    print("\n--- 6. 模板管理 ---")
    await run_test("list_templates", template.list_templates())
    await run_test("list_market_templates", template.list_market_templates())

    print("\n--- 7. 分享管理 ---")
    await run_test("list_shares", share.list_shares())

    print("\n--- 8. 目录结构深度探索 ---")
    datasources = results.get("list_datasources", {}).get("result", [])
    if datasources:
        print(f"  数据源根目录数量: {len(datasources)}")
        for item in datasources[:2]:
            print(f"    - {item.get('name', '?')} (id={item.get('id')}, type={item.get('nodeType')})")

    dashboards = results.get("list_dashboards", {}).get("result", [])
    if dashboards:
        print(f"  仪表板根目录数量: {len(dashboards)}")

    datasets_list = results.get("list_datasets", {}).get("result", [])
    if datasets_list:
        print(f"  数据集根目录数量: {len(datasets_list)}")

    print("\n--- 9. MCP_TEST 目录创建 ---")
    root_panels = results.get("list_dashboards", {}).get("result", [])
    root_ds = results.get("list_datasets", {}).get("result", [])

    if root_panels:
        try:
            panel_folder = await dashboard.create_folder(TEST_FOLDER, 0)
            print(f"  [INFO] 仪表板测试目录创建: {panel_folder}")
        except Exception as e:
            print(f"  [INFO] 仪表板测试目录: {e}")

    if root_ds:
        try:
            ds_folder = await dataset.create_dataset_folder(TEST_FOLDER, 0)
            print(f"  [INFO] 数据集测试目录创建: {ds_folder}")
        except Exception as e:
            print(f"  [INFO] 数据集测试目录: {e}")

    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    passed = sum(1 for r in results.values() if r["status"] == "PASS")
    failed = sum(1 for r in results.values() if r["status"] == "FAIL")
    print(f"通过: {passed}, 失败: {failed}, 总计: {len(results)}")

    for name, r in results.items():
        status_icon = "[OK]" if r["status"] == "PASS" else "[FAIL]"
        print(f"  {status_icon} {name}")

    with open("test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    print("\n结果已保存到 test_results.json")


if __name__ == "__main__":
    asyncio.run(main())
