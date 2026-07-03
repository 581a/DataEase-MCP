import asyncio
from dataease_mcp.tools import dataset, dashboard


async def main():
    dsets = await dataset.list_datasets()
    if dsets:
        for child in dsets[0].get("children", []):
            if child.get("name") == "MCP_TEST":
                cid = int(child["id"])
                print(f"Deleting MCP_TEST dataset folder (id={cid})")
                await dataset.delete_dataset(cid)
                print("Deleted!")

    panels = await dashboard.list_dashboards()
    if panels:
        for child in panels[0].get("children", []):
            name = child.get("name", "")
            if "MCP_TEST" in str(name):
                print(f"Found MCP_TEST dashboard: {name} (id={child['id']})")
                await dashboard.delete_dashboard(int(child["id"]))
                print("Deleted!")


if __name__ == "__main__":
    asyncio.run(main())
