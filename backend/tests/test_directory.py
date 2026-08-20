import pytest

from app.infrastructure.db.null_repository import NullSnapshotRepository
from app.infrastructure.demo.data import PLAYERS
from app.infrastructure.directory import CompositePlayerDirectory


@pytest.mark.asyncio
async def test_empty_extra_does_not_load_demo_players() -> None:
    directory = CompositePlayerDirectory(NullSnapshotRepository(), extra=[])
    players = await directory.search("")
    assert players == []
    assert await directory.get("demo-palmer") is None


@pytest.mark.asyncio
async def test_default_extra_loads_demo_players() -> None:
    directory = CompositePlayerDirectory(NullSnapshotRepository())
    players = await directory.search("")
    assert {player.id for player in players} == set(PLAYERS)
    assert await directory.get("demo-palmer") is not None
