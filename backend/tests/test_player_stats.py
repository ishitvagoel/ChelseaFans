from datetime import UTC, datetime

import pytest

from app.application.orchestrator import ProviderOrchestrator
from app.application.registry import ProviderRegistry
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
from app.infrastructure.providers.api_football import _map_event
from app.infrastructure.providers.api_football_helpers import club_names_match, season_accessible_on_free_tier
from app.infrastructure.providers.contracts.api_football import ApiFootballEventRecord


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
async def test_orchestrator_falls_back_to_rated_fixtures() -> None:
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
    assert result[0].id == "af-99"
    assert result[0].player_stats
    assert result[0].player_stats[0].rating == 8.1
    assert result[0].events
    assert result[0].events[0].player_name == "L. Colwill"


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
