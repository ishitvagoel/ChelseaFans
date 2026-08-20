from datetime import UTC, datetime

import httpx
import pytest

from app.application.orchestrator import JUST_FINISHED_CACHE_VERSION, ProviderOrchestrator
from app.application.registry import ProviderRegistry
from app.application.serialization import match_to_dict
from app.domain.models import (
    ClubRef,
    DataConfidence,
    EventType,
    Match,
    MatchEvent,
    MatchStatus,
    Player,
    PlayerMatchStats,
    Score,
)
from app.infrastructure.cache.memory import InMemoryCache
from app.infrastructure.db.null_repository import NullSnapshotRepository
from app.infrastructure.providers.api_football import ApiFootballProvider, _map_event
from app.infrastructure.providers.api_football_helpers import club_names_match, season_accessible_on_free_tier
from app.infrastructure.providers.contracts.api_football import ApiFootballEventRecord
from tests.fakes import CountingFixtureProvider


def test_club_names_match_normalizes_suffixes() -> None:
    assert club_names_match("Chelsea FC", "Chelsea")
    assert club_names_match("Tottenham Hotspur FC", "Tottenham")


def test_season_accessible_on_free_tier() -> None:
    assert season_accessible_on_free_tier(datetime(2024, 11, 1, tzinfo=UTC))
    assert not season_accessible_on_free_tier(datetime(2025, 8, 1, tzinfo=UTC))


class RatedFixtureProvider:
    name = "api-football"

    def __init__(self, matches: list[Match]) -> None:
        self.matches = matches

    async def recent_finished(self, *, team_hint: str, limit: int) -> list[Match]:
        _ = team_hint
        return self.matches[:limit]


class PrimaryFixtureProvider:
    name = "football-data.org"

    async def recent_finished(self, *, team_hint: str, limit: int) -> list[Match]:
        _ = team_hint
        return [
            Match(
                id="fd-1",
                utc_kickoff=datetime(2026, 5, 19, tzinfo=UTC),
                competition="Premier League",
                home=ClubRef("Chelsea FC"),
                away=ClubRef("Tottenham Hotspur FC"),
                score=Score(2, 1),
                status=MatchStatus.FINISHED,
                sources=(DataConfidence("football-data.org", 0.9),),
            )
        ]


class StatsProvider:
    name = "api-football"

    async def stats_for_match(self, match: Match) -> list[PlayerMatchStats]:
        if match.id.startswith("af-"):
            player = Player(id="af-1", name="Cole Palmer")
            return [
                PlayerMatchStats(
                    player=player,
                    minutes=90,
                    rating=8.1,
                    source="api-football",
                )
            ]
        return []

    async def events_for_match(self, match: Match) -> list[MatchEvent]:
        if match.id.startswith("af-"):
            return [MatchEvent(50, EventType.GOAL, "L. Colwill", "Normal Goal")]
        return []


@pytest.mark.asyncio
async def test_orchestrator_prefers_current_season_scores_over_rated_fixtures() -> None:
    rated_match = Match(
        id="af-99",
        utc_kickoff=datetime(2025, 5, 4, tzinfo=UTC),
        competition="Premier League",
        home=ClubRef("Chelsea"),
        away=ClubRef("Liverpool"),
        score=Score(3, 1),
        status=MatchStatus.FINISHED,
        sources=(DataConfidence("api-football", 0.88),),
    )
    registry = ProviderRegistry()
    registry.register_fixtures(PrimaryFixtureProvider())
    registry.register_fixtures(RatedFixtureProvider([rated_match]))
    registry.register_player_match_stats(StatsProvider())
    registry.register_historical_events(StatsProvider())
    orch = ProviderOrchestrator(registry, InMemoryCache(), NullSnapshotRepository())
    result = await orch.just_finished(1)
    assert len(result) == 1
    assert result[0].id == "fd-1"
    assert not result[0].player_stats
    assert any("Current-season" in source.coverage_notes for source in result[0].sources)


@pytest.mark.asyncio
async def test_orchestrator_uses_rated_fixtures_only_when_primary_empty() -> None:
    rated_match = Match(
        id="af-99",
        utc_kickoff=datetime(2025, 5, 4, tzinfo=UTC),
        competition="Premier League",
        home=ClubRef("Chelsea"),
        away=ClubRef("Liverpool"),
        score=Score(3, 1),
        status=MatchStatus.FINISHED,
        sources=(DataConfidence("api-football", 0.88),),
    )
    registry = ProviderRegistry()
    registry.register_fixtures(RatedFixtureProvider([rated_match]))
    registry.register_player_match_stats(StatsProvider())
    registry.register_historical_events(StatsProvider())
    orch = ProviderOrchestrator(registry, InMemoryCache(), NullSnapshotRepository())
    result = await orch.just_finished(1)
    assert len(result) == 1
    assert result[0].id == "af-99"
    assert result[0].player_stats
    assert result[0].player_stats[0].rating == 8.1
    assert result[0].events
    assert result[0].events[0].player_name == "L. Colwill"


@pytest.mark.asyncio
async def test_backfill_fills_matches_that_are_still_missing_stats() -> None:
    filled = Match(
        id="af-has",
        utc_kickoff=datetime(2024, 11, 9, tzinfo=UTC),
        competition="Premier League",
        home=ClubRef("Chelsea"),
        away=ClubRef("Arsenal"),
        score=Score(1, 1),
        status=MatchStatus.FINISHED,
        player_stats=(
            PlayerMatchStats(
                player=Player(id="af-1", name="Cole Palmer"),
                minutes=90,
                rating=7.4,
                source="api-football",
            ),
        ),
        sources=(DataConfidence("api-football", 0.88),),
    )
    missing = Match(
        id="af-missing",
        utc_kickoff=datetime(2024, 10, 20, tzinfo=UTC),
        competition="Premier League",
        home=ClubRef("Liverpool"),
        away=ClubRef("Chelsea"),
        score=Score(2, 1),
        status=MatchStatus.FINISHED,
        sources=(DataConfidence("api-football", 0.88),),
    )
    cache = InMemoryCache()
    await cache.set_json(
        f"chelsea:just-finished:{JUST_FINISHED_CACHE_VERSION}",
        [match_to_dict(filled), match_to_dict(missing)],
        60,
    )
    stats = CountingStatsProvider()
    registry = ProviderRegistry()
    registry.register_player_match_stats(stats)
    orch = ProviderOrchestrator(registry, cache, NullSnapshotRepository())
    result = await orch.just_finished(2)
    assert [match.id for match in result] == ["af-has", "af-missing"]
    assert result[0].player_stats
    assert result[1].player_stats
    assert result[1].player_stats[0].rating == 8.1
    assert stats.calls == ["af-missing"]


@pytest.mark.asyncio
async def test_empty_stats_are_negatively_cached() -> None:
    match = Match(
        id="fd-2024",
        utc_kickoff=datetime(2024, 11, 9, tzinfo=UTC),
        competition="Premier League",
        home=ClubRef("Chelsea"),
        away=ClubRef("Arsenal"),
        score=Score(1, 1),
        status=MatchStatus.FINISHED,
        sources=(DataConfidence("football-data.org", 0.9),),
    )
    stats = CountingStatsProvider()
    registry = ProviderRegistry()
    registry.register_fixtures(CountingFixtureProvider([match]))
    registry.register_player_match_stats(stats)
    orch = ProviderOrchestrator(registry, InMemoryCache(), NullSnapshotRepository())
    first = await orch.just_finished(1)
    second = await orch.just_finished(1)
    assert first[0].id == "fd-2024"
    assert not first[0].player_stats
    assert not second[0].player_stats
    assert stats.calls == ["fd-2024"]


class CountingStatsProvider:
    name = "api-football"

    def __init__(self) -> None:
        self.calls: list[str] = []

    async def stats_for_match(self, match: Match) -> list[PlayerMatchStats]:
        self.calls.append(match.id)
        if match.id == "af-missing":
            return [
                PlayerMatchStats(
                    player=Player(id="af-2", name="Moisés Caicedo"),
                    minutes=90,
                    rating=8.1,
                    source="api-football",
                )
            ]
        return []


def test_map_api_football_goal_event() -> None:
    record = ApiFootballEventRecord.model_validate(
        {
            "time": {"elapsed": 50},
            "player": {"id": 1, "name": "L. Colwill"},
            "assist": {"id": 2, "name": "C. Palmer"},
            "type": "Goal",
            "detail": "Normal Goal",
        }
    )
    events = _map_event(record)
    assert events[0].event_type == EventType.GOAL
    assert events[1].event_type == EventType.ASSIST


class RecordingClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict | None]] = []

    async def request(self, method: str, url: str, *, headers=None, params=None):
        self.calls.append((url, params))
        return httpx.Response(200, json={"response": []})


def _current_season_match() -> Match:
    return Match(
        id="fd-now",
        utc_kickoff=datetime(2025, 8, 17, tzinfo=UTC),
        competition="Premier League",
        home=ClubRef("Chelsea FC"),
        away=ClubRef("West Ham United FC"),
        score=Score(2, 0),
        status=MatchStatus.FINISHED,
        sources=(DataConfidence("football-data.org", 0.9),),
    )


@pytest.mark.asyncio
async def test_season_totals_outside_free_tier_do_not_call_api() -> None:
    client = RecordingClient()
    provider = ApiFootballProvider(client, "key", 49, "https://v3.football.api-sports.io")
    rows = await provider.season_totals(player_id="af-123", season_from="2025/26", season_to="2025/26")
    assert rows == []
    assert client.calls == []


@pytest.mark.asyncio
async def test_events_for_current_season_do_not_call_api() -> None:
    client = RecordingClient()
    provider = ApiFootballProvider(client, "key", 49, "https://v3.football.api-sports.io")
    events = await provider.events_for_match(_current_season_match())
    assert events == []
    assert client.calls == []


@pytest.mark.asyncio
async def test_fixture_lookup_for_current_season_does_not_call_api() -> None:
    client = RecordingClient()
    provider = ApiFootballProvider(client, "key", 49, "https://v3.football.api-sports.io")
    stats = await provider.stats_for_match(_current_season_match())
    assert stats == []
    assert client.calls == []
