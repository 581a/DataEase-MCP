"""Create dashboard mimicking frontend saveCanvas exactly."""
import asyncio
import json
from src.dataease_mcp.client import de_client

async def main():
    # Create a dashboard the way the frontend would
    # 1. Use saveCanvas (which MCP create_dashboard already does)
    # 2. Get an existing working dashboard and compare its structure
    
    # Get a working dashboard
    working_id = 1231692208034418688  # 物料利用率-看板-beta-v1.0
    working = await de_client.post(
        "/dataVisualization/findById",
        {"id": working_id, "resourceTable": "snapshot", "source": "main_edit"},
    )
    
    # Get MCP dashboard
    mcp_id = 1270744877457608704
    mcp = await de_client.post(
        "/dataVisualization/findById",
        {"id": mcp_id, "resourceTable": "snapshot", "source": "main_edit"},
    )
    
    print("=== KEY DIFFERENCES ===")
    
    # Compare top-level fields
    for key in set(list(working.keys()) + list(mcp.keys())):
        wv = working.get(key)
        mv = mcp.get(key)
        if str(wv) != str(mv):
            print(f"\n{key}:")
            print(f"  WORKING: {str(wv)[:100]}")
            print(f"  MCP:     {str(mv)[:100]}")
    
    # Compare canvasStyleData structure
    w_cs = json.loads(working.get("canvasStyleData", "{}"))
    m_cs = json.loads(mcp.get("canvasStyleData", "{}"))
    
    w_keys = set(w_cs.keys())
    m_keys = set(m_cs.keys())
    
    print(f"\n\n=== canvasStyleData key diff ===")
    print(f"Working only: {w_keys - m_keys}")
    print(f"MCP only: {m_keys - m_keys}")
    
    # Check all working fields that don't exist in MCP
    for k in sorted(w_keys - m_keys):
        print(f"  WORKING ONLY: {k} = {w_cs[k]}")
    
    # Check componentData structure  
    w_comps = json.loads(working.get("componentData", "[]"))
    m_comps = json.loads(mcp.get("componentData", "[]"))
    
    print(f"\n=== componentData ===")
    print(f"Working: {len(w_comps)} components")
    print(f"MCP: {len(m_comps)} components")
    
    if w_comps and m_comps:
        w_comp = w_comps[0]
        m_comp = m_comps[0]
        w_comp_keys = set(w_comp.keys())
        m_comp_keys = set(m_comp.keys())
        print(f"\nWorking comp keys only: {w_comp_keys - m_comp_keys}")
        print(f"MCP comp keys only: {m_comp_keys - w_comp_keys}")

asyncio.run(main())
