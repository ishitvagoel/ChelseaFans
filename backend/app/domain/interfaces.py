from __future__ import annotations

from typing import Protocol

from app.domain.models import (
    Match,
    MatchEvent,
    Player,
    PlayerMatchStats,
    SeasonTotals,
    SnapshotRecord,
    TeamContext,
)


class IFixtureProvider(Protocol):
    name: str

    async def recent_finished(self, *, team_hint: str, limit: int) -> list[Match]:
        """Return recently finished matches for Chelsea (or team_hint)."""


class IPlayerMatchStatsProvider(Protocol):
    name: str

    async def stats_for_match(self, match: Match) -> list[PlayerMatchStats]:
        """Per-fixture player stats. Empty list if this source cannot enrich."""


class ISeasonStatsProvider(Protocol):
    name: str

    async def season_totals(
        self,
        *,
        player_id: str,
        season_from: str | None,
        season_to: str | None,
    ) -> list[SeasonTotals]:
        ...

    async def search_players(self, query: str) -> list[Player]:
        ...


class IHistoricalEventProvider(Protocol):
    name: str

    async def events_for_match(self, match: Match) -> list[MatchEvent]:
        ...


class ITeamContextProvider(Protocol):
    name: str

    async def chelsea_context(self) -> TeamContext | None:
        ...


class ICache(Protocol):
    async def get_json(self, key: str) -> dict | list | None:
        ...

    async def set_json(self, key: str, value: dict | list, ttl_seconds: int) -> None:
        ...


class ISnapshotRepository(Protocol):
    async def get(self, key: str) -> SnapshotRecord | None:
        ...

    async def put(self, record: SnapshotRecord) -> None:
        ...

    async def list_players(self) -> list[Player]:
        ...

    async def upsert_player(self, player: Player) -> None:
        ...

    async def upsert_match(self, match: Match) -> None:
        ...


class IPlayerDirectory(Protocol):
    async def search(self, query: str) -> list[Player]:
        ...

    async def get(self, player_id: str) -> Player | None:
        ...
