import asyncio
from dataease_mcp.tools import datasource, chart, dataset, dashboard
from dataease_mcp.utils import generate_view_id, CHART_TYPE_LIST
from dataease_mcp.server import _CHART_TYPE_DESCRIPTIONS


async def main():
    print("=== 1. List datasources with types ===")
    ds_tree = await datasource.list_datasources()
    all_ds_ids = []
    if ds_tree:
        for child in ds_tree[0].get("children", []):
            if child.get("nodeType") == "datasource":
                ds_id = child["id"]
                ds_name = child.get("name", "?")
                # Use full config to get type
                try:
                    cfg = await datasource.get_datasource_full_config(ds_id)
                    ds_type = str(cfg.get("type", ""))
                except Exception:
                    ds_type = "unknown"
                print(f"  DS: {ds_name} (id={ds_id}, type={ds_type})")
                all_ds_ids.append((ds_id, ds_type))

    print()
    print("=== 2. Test get_api_datasource_fields ===")
    api_ids = [(did, dt) for did, dt in all_ds_ids if "API" in dt]
    if api_ids:
        ds_id = api_ids[0][0]
        result = await datasource.get_api_datasource_fields(ds_id)
        print(f"  datasource: {result.get('datasource_name')}")
        print(f"  message: {result.get('message', 'N/A')}")
        tables = result.get("tables", [])
        print(f"  tables count: {len(tables)}")
        for t in tables[:2]:
            print(f"  table: {t['name']} (de_name: {t['de_table_name']})")
            for f in t["fields"][:5]:
                print(f"    field: {f}")
    else:
        print("  No API datasources found - checking all types:")
        for did, dt in all_ds_ids:
            cfg = await datasource.get_datasource_full_config(did)
            print(f"    id={did}: type={dt}, config_type={cfg.get('type')}")
            result = await datasource.get_api_datasource_fields(did)
            print(f"      api_fields: {result.get('message', result)}")

    print()
    print("=== 3. get_chart_types ===")
    types = [{"type": t, "desc": _CHART_TYPE_DESCRIPTIONS.get(t, t)} for t in CHART_TYPE_LIST[:5]]
    print(f"  First 5: {types}")
    print(f"  Total: {len(CHART_TYPE_LIST)}")

    print()
    print("=== 4. Snowflake IDs ===")
    id1 = generate_view_id()
    id2 = generate_view_id()
    print(f"  ID1: {id1}, ID2: {id2}, Unique: {id1 != id2}")

    print()
    print("=== 5. Dataset list ===")
    dsets = await dataset.list_datasets()
    if dsets:
        for child in dsets[0].get("children", [])[:5]:
            ctype = child.get("nodeType", "")
            cname = child.get("name", "")
            cid = child.get("id", "")
            print(f"  [{ctype}] {cname} (id={cid})")

    print()
    print("=== 6. Dashboard list ===")
    panels = await dashboard.list_dashboards()
    if panels:
        for child in panels[0].get("children", [])[:5]:
            ctype = child.get("nodeType", "")
            cname = child.get("name", "")
            cid = child.get("id", "")
            print(f"  [{ctype}] {cname} (id={cid})")

    print()
    print("ALL TESTS DONE")


if __name__ == "__main__":
    asyncio.run(main())
