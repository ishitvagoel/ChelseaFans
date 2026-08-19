from __future__ import annotations

import json

from redis.asyncio import Redis


class RedisCache:
    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def get_json(self, key: str) -> dict | list | None:
        raw = await self._redis.get(key)
        if raw is None:
            return None
        if isinstance(raw, bytes):
            raw = raw.decode()
        return json.loads(raw)

    async def set_json(self, key: str, value: dict | list, ttl_seconds: int) -> None:
        await self._redis.set(key, json.dumps(value, default=str), ex=ttl_seconds)
