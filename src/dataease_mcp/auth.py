import httpx

from .config import config
from .utils import parse_dekey, rsa_encrypt


class AuthManager:
    def __init__(self):
        self._token: str | None = None

    def invalidate(self):
        self._token = None

    async def ensure_auth(self, client: httpx.AsyncClient) -> str:
        if self._token:
            return self._token
        return await self.login(client)

    async def login(self, client: httpx.AsyncClient) -> str:
        try:
            resp = await client.get(f"{config.api_url}/dekey")
            resp.raise_for_status()
            payload = resp.json()
            dekey_data = payload.get("data", payload)
            if isinstance(dekey_data, dict):
                dekey_data = dekey_data.get("data", str(dekey_data))
            public_key_pem = parse_dekey(str(dekey_data))
            encrypted_name = rsa_encrypt(config.USERNAME, public_key_pem)
            encrypted_pwd = rsa_encrypt(config.PASSWORD, public_key_pem)
            login_resp = await client.post(
                f"{config.api_url}/login/localLogin",
                json={"name": encrypted_name, "pwd": encrypted_pwd},
            )
            login_resp.raise_for_status()
            login_data = login_resp.json()
            login_result = login_data.get("data", login_data)
            token = login_result.get("token") if isinstance(login_result, dict) else None
            if not token:
                msg = login_data.get("msg", str(login_data))
                raise RuntimeError(f"Login failed: {msg}")
            self._token = token
            return token
        except httpx.HTTPStatusError as e:
            raise RuntimeError(
                f"Login HTTP error: {e.response.status_code} - {e.response.text}"
            )
        except Exception as e:
            raise RuntimeError(f"Login failed: {e}")

    def invalidate(self):
        self._token = None


auth_manager = AuthManager()
