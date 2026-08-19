from __future__ import annotations

import logging
from datetime import UTC, datetime

from app.domain.models import (
    EventType,
    MatchEvent,
    Player,
    PlayerMatchStats,
    SeasonTotals,
)
from app.infrastructure.http.rate_limit import RateLimitedClient
from app.infrastructure.providers.api_football_helpers import (
    API_FOOTBALL_FREE_SEASONS,
    season_accessible_on_free_tier,
    season_start_year,
)
from app.infrastructure.providers.api_football_fixtures import fixture_item_matches_clubs
from app.infrastructure.providers.contracts.api_football import (
    ApiFootballEventsResponse,
    ApiFootballFixturePlayersResponse,
    ApiFootballFixturesResponse,
    ApiFootballPlayersResponse,
    ApiFootballSquadsResponse,
)

logger = logging.getLogger(__name__)


class ApiFootballProvider:
    name = "api-football"

    def __init__(
        self,
        client: RateLimitedClient,
        api_key: str,
        team_id: int,
        base_url: str,
    ) -> None:
        self._client = client
        self._api_key = api_key
        self._team_id = team_id
        self._base = base_url.rstrip("/")

    def _headers(self) -> dict[str, str]:
        return {"x-apisports-key": self._api_key}

    async def stats_for_match(self, match) -> list[PlayerMatchStats]:
        if not self._api_key:
            return []
        if not season_accessible_on_free_tier(match.utc_kickoff):
            logger.debug(
                "api-football player stats skipped for %s (season %s outside free tier)",
                match.id,
                season_start_year(match.utc_kickoff),
            )
            return []
        fixture_id = await self._resolve_fixture_id(match)
        if fixture_id is None:
            return []
        response = await self._client.request(
            "GET",
            f"{self._base}/fixtures/players",
            headers=self._headers(),
            params={"fixture": str(fixture_id)},
        )
        if response.status_code in (401, 403, 429):
            logger.warning("api-football fixtures/players HTTP %s for fixture %s", response.status_code, fixture_id)
            return []
        if response.status_code >= 400:
            return []
        payload = ApiFootballFixturePlayersResponse.model_validate(response.json())
        if payload.plan_error():
            logger.info("api-football player stats blocked: %s", payload.plan_error())
            return []
        stats: list[PlayerMatchStats] = []
        for team_block in payload.response:
            team_id = (team_block.team.id if team_block.team else None)
            team_name = (team_block.team.name if team_block.team else "") or ""
            if team_id not in (self._team_id, None) and "Chelsea" not in team_name:
                continue
            for entry in team_block.players:
                mapped = _map_player_fixture(entry)
                if mapped:
                    stats.append(mapped)
        stats.sort(key=lambda stat: (stat.rating is None, -(stat.rating or 0)))
        return stats[:12]

    async def events_for_match(self, match) -> list[MatchEvent]:
        if not self._api_key:
            return []
        fixture_id = await self._resolve_fixture_id(match)
        if fixture_id is None:
            return []
        response = await self._client.request(
            "GET",
            f"{self._base}/fixtures/events",
            headers=self._headers(),
            params={"fixture": str(fixture_id)},
        )
        if response.status_code >= 400:
            return []
        payload = ApiFootballEventsResponse.model_validate(response.json())
        if payload.plan_error():
            logger.info("api-football events blocked: %s", payload.plan_error())
            return []
        events: list[MatchEvent] = []
        for item in payload.response:
            mapped = _map_event(item)
            events.extend(mapped)
        return events[:20]

    async def season_totals(
        self,
        *,
        player_id: str,
        season_from: str | None,
        season_to: str | None,
    ) -> list[SeasonTotals]:
        if not self._api_key:
            return []
        if not player_id.startswith("af-"):
            return []
        external_id = player_id.removeprefix("af-")
        from_year = _season_start_year(season_from) if season_from else 2023
        to_year = _season_start_year(season_to) if season_to else 2024
        if from_year > to_year:
            from_year, to_year = to_year, from_year
        seasons = [year for year in range(from_year, to_year + 1) if year in API_FOOTBALL_FREE_SEASONS]
        if not seasons:
            seasons = [2024]
        rows: list[SeasonTotals] = []
        for season in seasons:
            response = await self._client.request(
                "GET",
                f"{self._base}/players",
                headers=self._headers(),
                params={"id": external_id, "season": str(season)},
            )
            if response.status_code >= 400:
                continue
            payload = ApiFootballPlayersResponse.model_validate(response.json())
            if payload.plan_error():
                continue
            for block in payload.response:
                player = _player_from_af(block.player.model_dump() if block.player else {})
                if player is None:
                    continue
                for stat in block.statistics:
                    rows.append(
                        _season_from_af(
                            player,
                            stat.model_dump(),
                            f"{season}/{str(season + 1)[-2:]}",
                        )
                    )
        return rows

    async def search_players(self, query: str) -> list[Player]:
        if not self._api_key:
            return []
        q = query.strip()
        if len(q) < 2:
            return await self._list_squad()
        season = _season_start_year(None)
        if season not in API_FOOTBALL_FREE_SEASONS:
            season = 2024
        response = await self._client.request(
            "GET",
            f"{self._base}/players",
            headers=self._headers(),
            params={"search": q, "team": str(self._team_id), "season": str(season)},
        )
        if response.status_code >= 400:
            return await self._list_squad(q)
        payload = ApiFootballPlayersResponse.model_validate(response.json())
        if payload.plan_error():
            return await self._list_squad(q)
        players: list[Player] = []
        for block in payload.response:
            player = _player_from_af(block.player.model_dump() if block.player else {})
            if player:
                players.append(player)
        return players[:20] if players else await self._list_squad(q)

    async def _list_squad(self, query: str = "") -> list[Player]:
        response = await self._client.request(
            "GET",
            f"{self._base}/players/squads",
            headers=self._headers(),
            params={"team": str(self._team_id)},
        )
        if response.status_code >= 400:
            return []
        payload = ApiFootballSquadsResponse.model_validate(response.json())
        if payload.plan_error() or not payload.response:
            return []
        q = query.lower().strip()
        players: list[Player] = []
        for block in payload.response:
            for raw in block.players:
                if raw.id is None or not raw.name:
                    continue
                if q and q not in raw.name.lower():
                    continue
                players.append(
                    Player(
                        id=f"af-{raw.id}",
                        name=raw.name,
                        position=raw.position,
                        shirt_number=raw.number,
                    )
                )
        return players[:40]

    async def _resolve_fixture_id(self, match) -> int | None:
        raw_id = match.id
        if raw_id.startswith("af-"):
            try:
                return int(raw_id.removeprefix("af-"))
            except ValueError:
                return None
        season = season_start_year(match.utc_kickoff)
        date = match.utc_kickoff.date().isoformat()
        response = await self._client.request(
            "GET",
            f"{self._base}/fixtures",
            headers=self._headers(),
            params={
                "team": str(self._team_id),
                "season": str(season),
                "from": date,
                "to": date,
            },
        )
        if response.status_code >= 400:
            return None
        payload = ApiFootballFixturesResponse.model_validate(response.json())
        if payload.plan_error():
            logger.info("api-football fixture lookup blocked for %s: %s", match.id, payload.plan_error())
            return None
        for item in payload.response:
            if fixture_item_matches_clubs(item, match.home.name, match.away.name):
                return item.fixture.id
        return None


def _season_start_year(label: str | None) -> int:
    if label:
        try:
            return int(label.split("/")[0])
        except (ValueError, AttributeError):
            pass
    now = datetime.now(UTC)
    return now.year if now.month >= 7 else now.year - 1


def _player_from_af(raw: dict) -> Player | None:
    pid = raw.get("id")
    name = raw.get("name")
    if pid is None or not name:
        return None
    return Player(
        id=f"af-{pid}",
        name=name,
        position=None,
        nationality=raw.get("nationality"),
        shirt_number=None,
    )


def _map_player_fixture(entry) -> PlayerMatchStats | None:
    player_raw = entry.player.model_dump() if entry.player else {}
    player = _player_from_af(player_raw)
    if player is None:
        return None
    stats_list = entry.statistics or []
    st = stats_list[0] if stats_list else None
    games = st.games if st and st.games else None
    goals = st.goals if st and st.goals else None
    shots = st.shots if st and st.shots else None
    passes = st.passes if st and st.passes else None
    tackles = st.tackles if st and st.tackles else None
    rating_raw = games.rating if games else None
    rating = float(rating_raw) if rating_raw not in (None, "") else None
    return PlayerMatchStats(
        player=player,
        minutes=_int_or_none(games.minutes if games else None),
        goals=_int_or_none(goals.total if goals else None),
        assists=_int_or_none(goals.assists if goals else None),
        rating=rating,
        shots=_int_or_none(shots.total if shots else None),
        key_passes=_int_or_none(passes.key if passes else None),
        tackles=_int_or_none(tackles.total if tackles else None),
        source="api-football",
    )


def _season_from_af(player: Player, stat: dict, season: str) -> SeasonTotals:
    games = stat.get("games") or {}
    goals = stat.get("goals") or {}
    league = (stat.get("league") or {}).get("name")
    rating_raw = games.get("rating")
    return SeasonTotals(
        player=player,
        season=season,
        competition=league,
        appearances=_int_or_none(games.get("appearences") or games.get("appearances")),
        minutes=_int_or_none(games.get("minutes")),
        goals=_int_or_none(goals.get("total")),
        assists=_int_or_none(goals.get("assists")),
        rating=float(rating_raw) if rating_raw not in (None, "") else None,
        source="api-football",
    )


def _map_event(item) -> list[MatchEvent]:
    kind = (item.type or "").lower()
    detail = item.detail
    player_name = item.player.name if item.player else None
    minute = _int_or_none(item.time.elapsed if item.time else None)
    events: list[MatchEvent] = []
    if kind == "goal":
        events.append(MatchEvent(minute, EventType.GOAL, player_name, detail))
        assist_name = item.assist.name if item.assist else None
        if assist_name:
            events.append(MatchEvent(minute, EventType.ASSIST, assist_name, "Assist"))
    elif kind == "card":
        events.append(MatchEvent(minute, EventType.CARD, player_name, detail))
    elif kind in {"subst", "substitution"}:
        events.append(MatchEvent(minute, EventType.SUBSTITUTION, player_name, detail))
    else:
        events.append(MatchEvent(minute, EventType.OTHER, player_name, detail or item.type))
    return events


def _int_or_none(value) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
