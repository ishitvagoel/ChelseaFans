from __future__ import annotations

import asyncio
import time

import httpx


class RateLimitedClient:
    """Shared HTTP helper — min interval between calls (free-tier respect)."""

    def __init__(self, min_interval_seconds: float, timeout: float = 20.0) -> None:
        self._min_interval = min_interval_seconds
        self._lock = asyncio.Lock()
        self._last = 0.0
        self._client = httpx.AsyncClient(timeout=timeout)

    async def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict | None = None,
    ) -> httpx.Response:
        async with self._lock:
            wait = self._min_interval - (time.monotonic() - self._last)
            if wait > 0:
                await asyncio.sleep(wait)
            response = await self._client.request(method, url, headers=headers, params=params)
            self._last = time.monotonic()
            return response

    async def aclose(self) -> None:
        await self._client.aclose()
