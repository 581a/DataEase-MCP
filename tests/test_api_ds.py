import asyncio
import json as j
from dataease_mcp.tools import datasource


async def main():
    ds = await datasource.list_datasources()
    all_ds = []
    for child in ds[0].get("children", []):
        ctype = child.get("type", "")
        if ctype == "API" or ctype == "Excel":
            all_ds.append((child["id"], ctype, child["name"]))
        elif ctype == "folder":
            for sub in child.get("children", []):
                if sub.get("type") in ("API", "Excel"):
                    all_ds.append((sub["id"], sub["type"], sub["name"]))

    api_ids = [(did, dt, dn) for did, dt, dn in all_ds if "API" in dt]

    for ds_id, ds_type, ds_name in api_ids[:3]:
        print(f"\n=== {ds_name} (id={ds_id}) ===")

        print(f"  [getTables]:")
        try:
            tables = await datasource.get_datasource_tables(ds_id)
            print(f"    type: {type(tables).__name__}")
            if isinstance(tables, list):
                print(f"    count: {len(tables)}")
                for t in tables[:2]:
                    print(f"    - name={t.get('name')}, tableName={t.get('tableName')}, datasourceId={t.get('datasourceId')}")
            elif isinstance(tables, dict):
                print(f"    keys: {list(tables.keys())}")
                print(f"    records count: {len(tables.get('records', tables.get('data', [])))}")
                for r in tables.get('records', tables.get('data', []))[:2]:
                    print(f"    - {r.get('name', r.get('tableName', r))}")
            else:
                print(f"    raw: {str(tables)[:300]}")
        except Exception as e:
            print(f"    ERROR: {e}")

        print(f"  [getTableField] using first table:")
        try:
            tables_raw = await datasource.get_datasource_tables(ds_id)
            if isinstance(tables_raw, list) and tables_raw:
                tn = tables_raw[0].get("tableName") or tables_raw[0].get("name")
                if tn:
                    fields = await datasource.get_table_fields(ds_id, tn)
                    print(f"    count: {len(fields) if isinstance(fields, list) else 'not list'}")
                    if isinstance(fields, list) and fields:
                        for f in fields[:5]:
                            print(f"    - {f.get('name') or f.get('originName')} ({f.get('type') or f.get('deType')})")
        except Exception as e:
            print(f"    ERROR: {e}")

        print(f"  [get_datasource_detail]:")
        try:
            detail = await datasource.get_datasource_detail(ds_id)
            print(f"    keys: {list(detail.keys()) if isinstance(detail, dict) else type(detail).__name__}")
        except Exception as e:
            print(f"    ERROR: {e}")


asyncio.run(main())
