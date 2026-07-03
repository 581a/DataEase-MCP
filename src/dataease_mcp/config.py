import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    BASE_URL: str = os.getenv("DE_BASE_URL", "http://10.40.9.211:8100").rstrip("/")
    API_PREFIX: str = os.getenv("DE_API_PREFIX", "/de2api")
    USERNAME: str = os.getenv("DE_USERNAME", "admin")
    PASSWORD: str = os.getenv("DE_PASSWORD", "123456!a@Reliance")
    TOKEN_KEY: str = "X-DE-TOKEN"
    REQUEST_TIMEOUT: float = float(os.getenv("DE_REQUEST_TIMEOUT", "60.0"))

    @property
    def api_url(self) -> str:
        return f"{self.BASE_URL}{self.API_PREFIX}"


config = Config()
