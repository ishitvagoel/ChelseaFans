from __future__ import annotations

import json
import time
from typing import Any


class InMemoryCache:
    def __init__(self) -> None:
        self._store: dict[str, tuple[float, str]] = {}

    async def get_json(self, key: str) -> dict | list | None:
        row = self._store.get(key)
        if row is None:
            return None
        expires, raw = row
        if expires < time.time():
            self._store.pop(key, None)
            return None
        return json.loads(raw)

    async def set_json(self, key: str, value: dict | list, ttl_seconds: int) -> None:
        self._store[key] = (time.time() + ttl_seconds, json.dumps(value, default=str))
