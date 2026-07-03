from typing import Any

import httpx

from .auth import auth_manager
from .config import config


class DEClient:
    def __init__(self):
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=config.REQUEST_TIMEOUT)
        return self._client

    async def _headers(self) -> dict[str, str]:
        client = await self._get_client()
        token = await auth_manager.ensure_auth(client)
        return {config.TOKEN_KEY: token}

    async def get(self, path: str, **kwargs) -> Any:
        client = await self._get_client()
        headers = await self._headers()
        resp = await client.get(
            f"{config.api_url}{path}", headers=headers, **kwargs
        )
        resp.raise_for_status()
        return self._parse_response(resp)

    async def post(
        self,
        path: str,
        json_data: dict[str, Any] | list[Any] | None = None,
        **kwargs,
    ) -> Any:
        client = await self._get_client()
        headers = await self._headers()
        resp = await client.post(
            f"{config.api_url}{path}",
            headers=headers,
            json=json_data,
            **kwargs,
        )
        resp.raise_for_status()
        return self._parse_response(resp)

    def _parse_response(self, resp: httpx.Response) -> Any:
        content_type = resp.headers.get("content-type", "")
        is_json = "application/json" in content_type

        raw_text = resp.text
        if not raw_text:
            return None

        if is_json or raw_text.strip().startswith("{"):
            try:
                body = resp.json()
            except Exception:
                return raw_text
            if isinstance(body, dict) and "code" in body:
                code = body.get("code", 0)
                if code != 0:
                    msg = body.get("msg", "Unknown error")
                    raise RuntimeError(f"API error code={code}: {msg}")
                return body.get("data")
            return body
        return raw_text

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None


de_client = DEClient()
