import asyncio
import json as j
from dataease_mcp.tools import datasource, dashboard, dataset


async def main():
    print("=== 1. Datasource tree ===")
    ds = await datasource.list_datasources()
    all_ds = []

    if ds:
        for child in ds[0].get("children", []):
            ctype = child.get("type", "")
            cname = child.get("name", "")
            cid = child.get("id", "")
            if ctype == "API" or ctype == "Excel":
                all_ds.append((cid, ctype, cname))
                print(f"  [{ctype}] {cname} (id={cid})")
            elif ctype == "folder":
                for sub in child.get("children", []):
                    stype = sub.get("type", "")
                    sname = sub.get("name", "")
                    sid = sub.get("id", "")
                    if stype == "API" or stype == "Excel":
                        all_ds.append((sid, stype, sname))
                        print(f"  [{stype}] {sname} (id={sid})")

    print(f"\n  Total datasources: {len(all_ds)}")
    api_ds = [(did, dt, dn) for did, dt, dn in all_ds if "API" in dt]
    print(f"  API datasources: {len(api_ds)}")

    print("\n=== 2. get_datasource_full_config for API DS ===")
    for ds_id, ds_type, ds_name in api_ds[:2]:
        print(f"\n  Testing {ds_name} (id={ds_id})")
        try:
            cfg = await datasource.get_datasource_full_config(ds_id)
            print(f"    keys: {list(cfg.keys()) if isinstance(cfg, dict) else type(cfg).__name__}")
            if isinstance(cfg, dict):
                print(f"    type: {cfg.get('type')}")
                configuration = cfg.get("configuration", "")
                print(f"    config type: {type(configuration).__name__}")
                print(f"    config: {str(configuration)[:500]}")
        except Exception as e:
            print(f"    ERROR: {e}")

    print("\n=== 3. get_api_datasource_fields ===")
    for ds_id, ds_type, ds_name in api_ds[:2]:
        print(f"\n  Testing {ds_name} (id={ds_id})")
        try:
            result = await datasource.get_api_datasource_fields(ds_id)
            print(f"    name: {result.get('datasource_name')}")
            print(f"    msg: {result.get('message', 'N/A')}")
            tables = result.get("tables", [])
            print(f"    tables: {len(tables)}")
            for t in tables[:2]:
                print(f"      table: {t['name']}")
                for f in t["fields"][:3]:
                    print(f"        field: {f.get('name')} ({f.get('type')})")
        except Exception as e:
            print(f"    ERROR: {e}")

    print("\n=== 4. Dashboard tree debug ===")
    try:
        dp = await dashboard.list_dashboards()
        print(f"  DP result length: {len(dp) if dp else 0}")
        if dp:
            print(f"  DP type: {type(dp).__name__}")
            if isinstance(dp, list) and len(dp) > 0:
                r = dp[0]
                print(f"  Root keys: {list(r.keys()) if isinstance(r, dict) else type(r)}")
                children = r.get("children", []) if isinstance(r, dict) else []
                print(f"  Children count: {len(children)}")
            else:
                print(f"  DP raw: {str(dp)[:200]}")
    except Exception as e:
        print(f"  ERROR: {e}")

    print("\n=== 5. Dataset detail ===")
    dsets = await dataset.list_datasets()
    if dsets and len(dsets) > 0:
        children = dsets[0].get("children", [])
        dataset_ids = [
            (c["id"], c["name"]) for c in children
            if c.get("type") in ("sql", "union", "db") or c.get("info") is not None
        ][:3]
        for did, dname in dataset_ids:
            print(f"\n  Dataset: {dname} (id={did})")
            try:
                detail = await dataset.get_dataset_detail(did)
                print(f"    keys: {list(detail.keys()) if isinstance(detail, dict) else type(detail).__name__}")
            except Exception as e:
                print(f"    ERROR: {e}")
            try:
                fields = await dataset.get_dataset_fields(did)
                if fields and len(fields) > 0:
                    print(f"    fields count: {len(fields)}")
                    f0 = fields[0]
                    if isinstance(f0, dict):
                        print(f"    Sample field: name={f0.get('name')}, dataeaseName={f0.get('dataeaseName')}, groupType={f0.get('groupType')}, deType={f0.get('deType')}")
            except Exception as e:
                print(f"    field_error: {e}")

    print("\nDONE")


asyncio.run(main())
