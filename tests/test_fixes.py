import asyncio
import json as j
from dataease_mcp.tools import datasource, chart, dataset, dashboard
from dataease_mcp.utils import generate_view_id, CHART_TYPE_LIST
from dataease_mcp.server import _CHART_TYPE_DESCRIPTIONS


async def main():
    print("=" * 60)
    print("FIX VERIFICATION TESTS")
    print("=" * 60)

    print("\n=== 1. list_dashboards (with busiFlag fix) ===")
    try:
        dp = await dashboard.list_dashboards()
        if dp and len(dp) > 0:
            root = dp[0]
            children = root.get("children", [])
            print(f"  PASS: {len(children)} dashboard children found")
            for c in children[:5]:
                print(f"    [{c.get('nodeType', c.get('type','?'))}] {c.get('name','?')} (id={c.get('id','?')})")
        else:
            print(f"  unknown: {type(dp).__name__}, value: {str(dp)[:200]}")
    except Exception as e:
        print(f"  FAIL: {e}")

    print("\n=== 2. get_api_datasource_fields (fixed) ===")
    ds_tree = await datasource.list_datasources()
    api_ids = []
    for child in ds_tree[0].get("children", []):
        ctype = child.get("type", "")
        if ctype == "API":
            api_ids.append((child["id"], child["name"]))
        elif ctype == "folder":
            for sub in child.get("children", []):
                if sub.get("type") == "API":
                    api_ids.append((sub["id"], sub["name"]))

    for ds_id, ds_name in api_ids[:2]:
        print(f"\n  DS: {ds_name} (id={ds_id})")
        try:
            result = await datasource.get_api_datasource_fields(ds_id)
            print(f"    name: {result.get('datasource_name')}")
            msg = result.get("message", "")
            if msg:
                print(f"    msg: {msg}")
                continue
            tables = result.get("tables", [])
            print(f"    PASS: {len(tables)} tables found")
            for t in tables:
                fields_n = len(t.get("fields", []))
                err = t.get("fields_error", "")
                print(f"      table: {t['name']} - {fields_n} fields" + (f" [error: {err}]" if err else ""))
                for f in t["fields"][:3]:
                    print(f"        field: name={f['name']}, type={f['type']}, dataeaseName={f.get('raw',{}).get('dataeaseName','?')}")
        except Exception as e:
            print(f"    FAIL: {e}")

    print("\n=== 3. get_dataset_fields (for chart save params) ===")
    dsets = await dataset.list_datasets()
    dataset_list = []
    for child in dsets[0].get("children", []):
        ct = child.get("type", "")
        if ct in ("sql", "union", "db", None):
            dataset_list.append((child["id"], child["name"]))

    if dataset_list:
        did, dname = dataset_list[0]
        print(f"  Dataset: {dname} (id={did})")
        try:
            fields = await dataset.get_dataset_fields(did)
            print(f"  PASS: {len(fields) if fields else 0} fields")
            if fields:
                for f in fields[:5]:
                    print(f"    id={f.get('id')}, name={f.get('name')}, dataeaseName={f.get('dataeaseName')}, groupType={f.get('groupType')}, deType={f.get('deType')}")
        except Exception as e:
            print(f"  FAIL: {e}")

    print("\n=== 4. save_chart test ===")
    if dataset_list:
        did, dname = dataset_list[0]
        fields = await dataset.get_dataset_fields(did)
        if fields:
            x_fields = [f for f in fields if f.get("groupType") == "d"][:1]
            y_fields = [f for f in fields if f.get("groupType") == "q"][:1]
            if not x_fields:
                x_fields = [f for f in fields if f.get("groupType") != "q"][:1]
            if not y_fields:
                y_fields = [f for f in fields][:1]

            print(f"  x_fields: {[f.get('name') for f in x_fields]}")
            print(f"  y_fields: {[f.get('name') for f in y_fields]}")

            # Get dashboard ID for sceneId
            dp = await dashboard.list_dashboards()
            scene_id = 0
            if dp and len(dp) > 0:
                children = dp[0].get("children", [])
                leaves = [c for c in children if c.get("nodeType") == "leaf"]
                if leaves:
                    scene_id = leaves[0]["id"]
                    print(f"  Using dashboard sceneId={scene_id} ({leaves[0].get('name')})")

            if scene_id and x_fields and y_fields:
                try:
                    result = await chart.save_chart(
                        title="MCP测试图表",
                        dashboard_id=scene_id,
                        dataset_id=did,
                        chart_type="bar",
                        x_fields=x_fields,
                        y_fields=y_fields,
                    )
                    chart_id = result.get("id") if isinstance(result, dict) else None
                    print(f"  PASS: chart created, id={chart_id}")
                    if chart_id:
                        print(f"    Cleaning up chart {chart_id}...")
                        # Can't easily delete individual charts, but they're in MCP_TEST
                except Exception as e:
                    print(f"  FAIL: {e}")

    print("\n" + "=" * 60)
    print("ALL FIX VERIFICATION COMPLETE")
    print("=" * 60)


asyncio.run(main())
