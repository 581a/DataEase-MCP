import asyncio
import json
import httpx
from dataease_mcp.config import config
from dataease_mcp.auth import auth_manager


async def main():
    async with httpx.AsyncClient() as c:
        token = await auth_manager.ensure_auth(c)

        # Test different busiFlag values and formats
        tests = [
            {"busiFlag": "panel"},
            {"busiFlag": "panel", "type": "dashboard"},
            {"busFlag": "panel"},
            {"busiFlag": "main"},
            {"busiFlag": "panel", "nodeType": "folder"},
            {"busiFlag": "panel", "pid": 0},
        ]
        for i, body in enumerate(tests):
            r = await c.post(
                f"{config.api_url}/dataVisualization/tree",
                headers={"X-DE-TOKEN": token},
                json=body,
            )
            resp = r.json()
            code = resp.get("code")
            msg = resp.get("msg") or ""
            data = resp.get("data")
            has_data = data is not None and (isinstance(data, list) and len(data) > 0)
            print(f"Test {i} body={json.dumps(body)}: code={code}, msg={msg[:100]}, has_data={has_data}")
            if has_data:
                root = data[0]
                children = root.get("children", [])
                print(f"  children count: {len(children)}")
                for ch in children[:2]:
                    print(f"    [{ch.get('nodeType','?')}] {ch.get('name','?')}")

asyncio.run(main())
