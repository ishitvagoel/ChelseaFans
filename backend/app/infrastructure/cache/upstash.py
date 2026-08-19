from __future__ import annotations

import json
from urllib.parse import quote

import httpx


class UpstashRestCache:
    """Upstash Redis REST adapter. Values are JSON strings."""

    def __init__(self, base_url: str, token: str) -> None:
        self._base = base_url.rstrip("/")
        self._headers = {"Authorization": f"Bearer {token}"}
        self._client = httpx.AsyncClient(timeout=10.0)

    async def get_json(self, key: str) -> dict | list | None:
        response = await self._client.get(
            f"{self._base}/get/{quote(key, safe='')}",
            headers=self._headers,
        )
        if response.status_code >= 400:
            return None
        result = response.json().get("result")
        if result is None:
            return None
        return json.loads(result)

    async def set_json(self, key: str, value: dict | list, ttl_seconds: int) -> None:
        payload = json.dumps(value, default=str)
        path = f"/set/{quote(key, safe='')}/{quote(payload, safe='')}/EX/{ttl_seconds}"
        await self._client.get(f"{self._base}{path}", headers=self._headers)
