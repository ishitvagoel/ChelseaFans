from datetime import UTC, datetime

import pytest

from app.application.orchestrator import ProviderOrchestrator
from app.application.registry import ProviderRegistry
from app.domain.models import SnapshotRecord
from app.infrastructure.cache.memory import InMemoryCache
from app.infrastructure.db.null_repository import NullSnapshotRepository
from app.infrastructure.demo.provider import DemoProvider
from tests.fakes import CountingFixtureProvider


@pytest.mark.asyncio
async def test_orchestrator_uses_cache() -> None:
    registry = ProviderRegistry()
    demo = DemoProvider()
    registry.register_fixtures(demo)
    registry.register_player_match_stats(demo)
    cache = InMemoryCache()
    orch = ProviderOrchestrator(registry, cache, NullSnapshotRepository())
    first = await orch.just_finished(3)
    cached = await cache.get_json("chelsea:just-finished:v6")
    assert cached is not None
    second = await orch.just_finished(3)
    assert [m.id for m in first] == [m.id for m in second]


@pytest.mark.asyncio
async def test_empty_snapshot_does_not_block_live_fetch() -> None:
    demo = DemoProvider()
    matches = await demo.recent_finished(team_hint="Chelsea", limit=2)
    registry = ProviderRegistry()
    counter = CountingFixtureProvider(matches)
    registry.register_fixtures(counter)
    registry.register_player_match_stats(demo)
    snaps = NullSnapshotRepository()
    await snaps.put(
        SnapshotRecord(
            key="chelsea:just-finished:v6",
            payload={"matches": []},
            stored_at=datetime.now(UTC),
        )
    )
    orch = ProviderOrchestrator(registry, InMemoryCache(), snaps)
    result = await orch.just_finished(2)
    assert counter.calls == 1
    assert len(result) == 2


@pytest.mark.asyncio
async def test_empty_fixture_result_is_not_snapshotted() -> None:
    registry = ProviderRegistry()
    counter = CountingFixtureProvider([])
    registry.register_fixtures(counter)
    snaps = NullSnapshotRepository()
    orch = ProviderOrchestrator(registry, InMemoryCache(), snaps)
    result = await orch.just_finished(3)
    assert result == []
    assert await snaps.get("chelsea:just-finished:v6") is None
