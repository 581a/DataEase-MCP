import asyncio
import json as j
import httpx
from dataease_mcp.config import config
from dataease_mcp.auth import auth_manager


async def main():
    async with httpx.AsyncClient() as c:
        token = await auth_manager.ensure_auth(c)

        flags = ["panel", "main", "report", "", None]
        for flag in flags:
            body = {"type": "dashboard"}
            if flag is not None:
                body["busiFlag"] = flag
            r = await c.post(
                f"{config.api_url}/dataVisualization/tree",
                headers={"X-DE-TOKEN": token},
                json=body,
            )
            print(f"busiFlag={flag!r}: code={r.json().get('code')}, msg={r.json().get('msg','')[:80]}")
            data = r.json().get("data")
            if data and isinstance(data, list) and len(data) > 0:
                root = data[0]
                children = root.get("children", [])
                print(f"  children: {len(children)}")
                for c in children[:3]:
                    print(f"    [{c.get('nodeType', c.get('type','?'))}] {c.get('name')} (id={c.get('id')})")

        # Also try with dvType in tree
        print()
        for dv_type in ["dashboard", "dataV"]:
            r = await c.post(
                f"{config.api_url}/dataVisualization/tree",
                headers={"X-DE-TOKEN": token},
                json={"busiFlag": "panel", "type": dv_type},
            )
            data = r.json().get("data")
            print(f"type={dv_type}: code={r.json().get('code')}, msg={r.json().get('msg','')[:80]}")
            if data and isinstance(data, list) and len(data) > 0:
                root = data[0]
                children = root.get("children", [])
                print(f"  children: {len(children)}")


asyncio.run(main())
