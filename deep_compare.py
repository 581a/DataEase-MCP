"""Deep compare MCP dashboard vs frontend dashboard."""
import asyncio
import json
from src.dataease_mcp.client import de_client

async def main():
    mcp_id = 1270775805580021760  # MCP-测试 (just created)
    fe_id = 1270731970686619648   # 仪表板测试 (frontend created)
    
    mcp = await de_client.post("/dataVisualization/findById", {"id": mcp_id, "resourceTable": "snapshot", "source": "main_edit"})
    fe = await de_client.post("/dataVisualization/findById", {"id": fe_id, "resourceTable": "snapshot", "source": "main_edit"})
    
    print("=== TOP-LEVEL FIELD COMPARISON ===")
    all_keys = set(list(mcp.keys()) + list(fe.keys()))
    for k in sorted(all_keys):
        mv = mcp.get(k)
        fv = fe.get(k)
        if str(mv) != str(fv):
            print(f"\n{k}:")
            print(f"  MCP: {json.dumps(mv, ensure_ascii=False, default=str)[:200]}")
            print(f"  FE:  {json.dumps(fv, ensure_ascii=False, default=str)[:200]}")
    
    # Deep compare canvasStyleData
    mcp_cs = json.loads(mcp.get("canvasStyleData", "{}"))
    fe_cs = json.loads(fe.get("canvasStyleData", "{}"))
    
    print("\n\n=== canvasStyleData: MCP vs FE ===")
    compare_dict(mcp_cs, fe_cs, "cs")
    
    # Deep compare componentData (first component)
    mcp_comps = json.loads(mcp.get("componentData", "[]"))
    fe_comps = json.loads(fe.get("componentData", "[]"))
    
    print("\n\n=== componentData[0] COMPARISON ===")
    if mcp_comps and fe_comps:
        compare_dict(mcp_comps[0], fe_comps[0], "comp")

def compare_dict(d1, d2, path=""):
    """Recursively compare two dicts."""
    all_keys = set(list(d1.keys()) + list(d2.keys()))
    for k in sorted(all_keys):
        curr = f"{path}.{k}"
        v1 = d1.get(k, "<MISSING>")
        v2 = d2.get(k, "<MISSING>")
        
        # Skip known non-critical differences
        if k in ('ids',):
            continue
        
        if isinstance(v1, dict) and isinstance(v2, dict):
            compare_dict(v1, v2, curr)
        elif isinstance(v1, list) and isinstance(v2, list):
            if len(v1) != len(v2) or (len(v1) > 0 and not (isinstance(v1[0], dict) and isinstance(v2[0], dict))):
                if str(v1) != str(v2):
                    print(f"  DIFF {curr}: len={len(v1)} vs len={len(v2)}")
                    print(f"    MCP: {json.dumps(v1, ensure_ascii=False, default=str)[:150]}")
                    print(f"    FE:  {json.dumps(v2, ensure_ascii=False, default=str)[:150]}")
            elif len(v1) > 0 and isinstance(v1[0], dict):
                for i in range(max(len(v1), len(v2))):
                    d1_item = v1[i] if i < len(v1) else {}
                    d2_item = v2[i] if i < len(v2) else {}
                    compare_dict(d1_item, d2_item, f"{curr}[{i}]")
        elif str(v1) != str(v2):
            t1 = f"({type(v1).__name__})" 
            t2 = f"({type(v2).__name__})"
            print(f"  DIFF {curr}: {t1} {json.dumps(v1, ensure_ascii=False, default=str)[:100]} vs {t2} {json.dumps(v2, ensure_ascii=False, default=str)[:100]}")

asyncio.run(main())
