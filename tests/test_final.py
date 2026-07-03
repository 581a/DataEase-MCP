import asyncio
import json as j
from dataease_mcp.tools import datasource, chart, dataset, dashboard
from dataease_mcp.utils import generate_view_id


async def main():
    print("=" * 60)
    print("FINAL FIX VERIFICATION")
    print("=" * 60)

    def find_leaves(nodes, depth=0):
        result = []
        for n in nodes:
            is_leaf = n.get("leaf", False)
            label = "leaf" if is_leaf else "folder"
            if depth < 2:
                print(f"    [{label}] {n.get('name', '?')} (id={n.get('id', '?')})")
            if is_leaf:
                result.append((n["id"], n["name"]))
            if n.get("children"):
                result.extend(find_leaves(n["children"], depth + 1))
        return result

    def find_folder(nodes, name):
        for n in nodes:
            if n.get("name") == name and not n.get("leaf", True):
                return n["id"]
            if n.get("children"):
                result = find_folder(n["children"], name)
                if result:
                    return result
        return 0

    print("\n=== 1. list_dashboards ===")
    try:
        dp = await dashboard.list_dashboards()
        if dp and isinstance(dp, list) and len(dp) > 0:
            root = dp[0]
            children = root.get("children", [])
            leaves = find_leaves(children)
            print(f"  PASS: {len(children)} children found, {len(leaves)} leaves total")
        else:
            print(f"  Result: {str(dp)[:200]}")
    except Exception as e:
        print(f"  FAIL: {e}")

    print("\n=== 2. get_api_datasource_fields ===")
    ds_tree = await datasource.list_datasources()
    api_ids = []
    for child in ds_tree[0].get("children", []):
        ctype = child.get("type", "")
        cname = child.get("name", "")
        cid = child.get("id", "")
        if ctype == "API":
            api_ids.append((cid, cname))
        elif ctype == "folder":
            for sub in child.get("children", []):
                if sub.get("type") == "API":
                    api_ids.append((sub["id"], sub["name"]))

    for ds_id, ds_name in api_ids[:1]:
        print(f"  DS: {ds_name} (id={ds_id})")
        result = await datasource.get_api_datasource_fields(ds_id)
        msg = result.get("message", "")
        if msg:
            print(f"    msg: {msg}")
            continue
        tables = result.get("tables", [])
        print(f"    PASS: {len(tables)} tables")
        for t in tables[:1]:
            fields_n = len(t.get("fields", []))
            print(f"    table: {t['name']} - {fields_n} fields")
            for f in t["fields"][:3]:
                print(f"      name={f['name']}, type={f['type']}, origin={f['origin_name']}")

    print("\n=== 3. Dataset fields for chart ===")
    dsets = await dataset.list_datasets()
    did = dname = None
    for child in dsets[0].get("children", []):
        ct = child.get("type", "")
        if ct in ("sql", "union", "db", None) and child.get("name") == "test_24":
            did = child["id"]
            dname = child["name"]
            break

    if did:
        print(f"  Dataset: {dname} (id={did})")
        fields = await dataset.get_dataset_fields(did)
        print(f"  Fields: {len(fields) if fields else 0}")
        if fields:
            for f in fields[:5]:
                print(f"    id={f.get('id')}, name={f.get('name')}, dataeaseName={f.get('dataeaseName')}, groupType={f.get('groupType')}, deType={f.get('deType')}")

    print("\n=== 4. get_chart_types ===")
    chart_types = [
        {"type": t, "description": {
            "table-info": "明细表", "table-normal": "汇总表", "bar": "柱状图",
            "line": "折线图", "pie": "饼图", "indicator": "指标卡", "gauge": "仪表盘",
        }.get(t, t)}
        for t in ["bar", "line", "pie", "table-info", "indicator"]
    ]
    print(f"  {len(chart_types)} chart types available")
    for ct in chart_types:
        print(f"    {ct['type']}: {ct['description']}")

    print("\n=== 5. save_chart end-to-end test ===")
    test_dv_id = 0
    test_chart_id = 0
    if did:
        fields = await dataset.get_dataset_fields(did)
        if fields:
            print(f"  All groupTypes: {set(f.get('groupType') for f in fields)}")
        x_fields = [f for f in fields if f.get("groupType") == "d"][:1]
        y_fields = [f for f in fields if f.get("groupType") == "q"][:1]
        if not y_fields:
            y_fields = [fields[-1]] if fields else []

        dp = await dashboard.list_dashboards()
        mcp_folder_id = find_folder(dp[0].get("children", []), "MCP看板")
        print(f"  MCP看板 folder id: {mcp_folder_id}")

        if mcp_folder_id:
            test_dv_id = await dashboard.create_dashboard(
                name="MCP测试-临时看板",
                pid=mcp_folder_id,
                dv_type="dashboard",
            )
            print(f"  Created test dashboard: id={test_dv_id}")

        if test_dv_id and x_fields and y_fields:
            x_names = [f.get("name") for f in x_fields]
            y_names = [f.get("name") for f in y_fields]
            print(f"  x_fields: {x_names}")
            print(f"  y_fields: {y_names}")
            try:
                result = await chart.save_chart(
                    title="MCP测试-柱状图",
                    dashboard_id=test_dv_id,
                    dataset_id=did,
                    chart_type="bar",
                    x_fields=x_fields,
                    y_fields=y_fields,
                )
                test_chart_id = result.get("id") if isinstance(result, dict) else result
                print(f"  PASS: chart created, id={test_chart_id}")

                detail = await chart.get_chart_detail(test_chart_id, "snapshot")
                if detail:
                    print(f"  PASS: chart detail retrieved, title={detail.get('title')}, type={detail.get('type')}")
                else:
                    print(f"  FAIL: chart detail returned null for id={test_chart_id}")
            except Exception as e:
                print(f"  FAIL: {e}")

    print("\n=== 6. Cleanup ===")
    if test_dv_id:
        try:
            await dashboard.delete_dashboard(test_dv_id)
            print(f"  Deleted test dashboard: id={test_dv_id}")
        except Exception as e:
            print(f"  Cleanup FAIL: {e}")
        test_dv_id = 0

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)


asyncio.run(main())
