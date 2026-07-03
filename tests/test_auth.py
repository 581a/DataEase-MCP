import asyncio
import httpx
from dataease_mcp.auth import auth_manager
from dataease_mcp.client import de_client
from dataease_mcp.config import config


async def test_auth():
    async with httpx.AsyncClient(timeout=config.REQUEST_TIMEOUT) as client:
        token = await auth_manager.login(client)
        print(f"Token obtained: {token[:50]}...")
        print("Login SUCCESS")

    result = await de_client.get("/user/info")
    print(f"User info: {result}")
    print("API access test SUCCESS")


if __name__ == "__main__":
    asyncio.run(test_auth())
