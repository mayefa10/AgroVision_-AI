import httpx
import logging

logger = logging.getLogger(__name__)

class BaseClient:
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url
        self.timeout  = timeout

    async def get(self, path: str = "", params: dict = None) -> dict:
        url = f"{self.base_url}{path}" if path else self.base_url
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                r = await client.get(url, params=params or {})
                r.raise_for_status()
                return r.json()
        except Exception as e:
            logger.error(f"GET {url} error: {e}")
            return {}