import pytest

from app.application.orchestrator import ProviderOrchestrator
from app.application.registry import ProviderRegistry
from app.infrastructure.cache.memory import InMemoryCache
from app.infrastructure.db.null_repository import NullSnapshotRepository
from app.infrastructure.demo.provider import DemoProvider


@pytest.mark.asyncio
async def test_orchestrator_uses_cache() -> None:
    registry = ProviderRegistry()
    demo = DemoProvider()
    registry.register_fixtures(demo)
    registry.register_player_match_stats(demo)
    cache = InMemoryCache()
    orch = ProviderOrchestrator(registry, cache, NullSnapshotRepository())
    first = await orch.just_finished(3)
    cached = await cache.get_json("chelsea:just-finished:3")
    assert cached is not None
    second = await orch.just_finished(3)
    assert [m.id for m in first] == [m.id for m in second]
