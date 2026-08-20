import pytest

from app.application.comparison import FREE_TIER_CAREER_FROM, FREE_TIER_CAREER_TO, ComparisonService
from app.application.registry import ProviderRegistry
from app.domain.models import Player, SeasonTotals
from app.infrastructure.db.null_repository import NullSnapshotRepository
from app.infrastructure.demo.data import PLAYERS
from app.infrastructure.directory import CompositePlayerDirectory


class RecordingSeasonProvider:
    name = "api-football"

    def __init__(self) -> None:
        self.calls: list[tuple[str, str | None, str | None]] = []

    async def season_totals(
        self,
        *,
        player_id: str,
        season_from: str | None,
        season_to: str | None,
    ) -> list[SeasonTotals]:
        self.calls.append((player_id, season_from, season_to))
        player = Player(id=player_id, name="C. Palmer")
        return [
            SeasonTotals(player=player, season="2022/23", competition="PL", goals=1, source="api-football"),
            SeasonTotals(player=player, season="2023/24", competition="PL", goals=22, source="api-football"),
            SeasonTotals(player=player, season="2024/25", competition="PL", goals=15, source="api-football"),
        ]

    async def search_players(self, query: str) -> list[Player]:
        _ = query
        return [Player(id="demo-palmer", name="Cole Palmer"), Player(id="af-1", name="C. Palmer")]


@pytest.mark.asyncio
async def test_live_search_drops_demo_players_even_with_query() -> None:
    snaps = NullSnapshotRepository()
    await snaps.upsert_player(PLAYERS["demo-palmer"])
    directory = CompositePlayerDirectory(snaps, extra=[])
    registry = ProviderRegistry()
    registry.register_season_stats(RecordingSeasonProvider())
    service = ComparisonService(registry, directory, allow_demo=False)
    found = await service.search("palmer")
    assert all(not player.id.startswith("demo-") for player in found)
    assert any(player.id == "af-1" for player in found)


@pytest.mark.asyncio
async def test_compare_fetches_free_tier_career_window() -> None:
    directory = CompositePlayerDirectory(NullSnapshotRepository(), extra=[])
    registry = ProviderRegistry()
    provider = RecordingSeasonProvider()
    registry.register_season_stats(provider)
    service = ComparisonService(registry, directory, allow_demo=False)
    result = await service.compare(["af-1"], "2024/25", "2024/25")
    assert provider.calls == [("af-1", FREE_TIER_CAREER_FROM, FREE_TIER_CAREER_TO)]
    assert result.players[0].season.goals == 15
    assert result.players[0].career.goals == 38


@pytest.mark.asyncio
async def test_live_compare_ignores_demo_player_ids() -> None:
    directory = CompositePlayerDirectory(NullSnapshotRepository(), extra=[])
    registry = ProviderRegistry()
    service = ComparisonService(registry, directory, allow_demo=False)
    result = await service.compare(["demo-palmer"], "2024/25", "2024/25")
    assert result.players == ()
