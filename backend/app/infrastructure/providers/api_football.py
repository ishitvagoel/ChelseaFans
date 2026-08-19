from __future__ import annotations

from datetime import UTC, datetime

from app.domain.models import (
    Player,
    PlayerMatchStats,
    SeasonTotals,
)
from app.infrastructure.http.rate_limit import RateLimitedClient


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
        fixture_id = await self._resolve_fixture_id(match)
        if fixture_id is None:
            return []
        response = await self._client.request(
            "GET",
            f"{self._base}/fixtures/players",
            headers=self._headers(),
            params={"fixture": str(fixture_id)},
        )
        if response.status_code >= 400:
            return []
        payload = response.json().get("response") or []
        stats: list[PlayerMatchStats] = []
        for team_block in payload:
            team = (team_block.get("team") or {}).get("id")
            if team not in (self._team_id, None):
                # still include if name is Chelsea
                name = (team_block.get("team") or {}).get("name") or ""
                if "Chelsea" not in name:
                    continue
            for entry in team_block.get("players") or []:
                mapped = _map_player_fixture(entry)
                if mapped:
                    stats.append(mapped)
        stats.sort(key=lambda s: (s.rating is None, -(s.rating or 0)))
        return stats[:12]

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
        season = _season_start_year(season_to or season_from)
        response = await self._client.request(
            "GET",
            f"{self._base}/players",
            headers=self._headers(),
            params={"id": external_id, "season": str(season)},
        )
        if response.status_code >= 400:
            return []
        rows: list[SeasonTotals] = []
        for block in response.json().get("response") or []:
            player = _player_from_af(block.get("player") or {})
            for stat in block.get("statistics") or []:
                rows.append(_season_from_af(player, stat, f"{season}/{str(season + 1)[-2:]}"))
        return rows

    async def search_players(self, query: str) -> list[Player]:
        if not self._api_key or len(query.strip()) < 3:
            return []
        response = await self._client.request(
            "GET",
            f"{self._base}/players",
            headers=self._headers(),
            params={"search": query.strip(), "team": str(self._team_id)},
        )
        if response.status_code >= 400:
            return []
        players = []
        for block in response.json().get("response") or []:
            player = _player_from_af(block.get("player") or {})
            if player:
                players.append(player)
        return players[:10]

    async def _resolve_fixture_id(self, match) -> int | None:
        raw_id = match.id
        if raw_id.startswith("af-"):
            try:
                return int(raw_id.removeprefix("af-"))
            except ValueError:
                return None
        date = match.utc_kickoff.date().isoformat()
        response = await self._client.request(
            "GET",
            f"{self._base}/fixtures",
            headers=self._headers(),
            params={"team": str(self._team_id), "date": date},
        )
        if response.status_code >= 400:
            return None
        items = response.json().get("response") or []
        if not items:
            return None
        return (items[0].get("fixture") or {}).get("id")


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


def _map_player_fixture(entry: dict) -> PlayerMatchStats | None:
    player_raw = entry.get("player") or {}
    player = _player_from_af(player_raw)
    if player is None:
        return None
    stats_list = entry.get("statistics") or [{}]
    st = stats_list[0] if stats_list else {}
    games = st.get("games") or {}
    goals = st.get("goals") or {}
    shots = st.get("shots") or {}
    passes = st.get("passes") or {}
    tackles = st.get("tackles") or {}
    rating_raw = games.get("rating")
    rating = float(rating_raw) if rating_raw not in (None, "") else None
    return PlayerMatchStats(
        player=player,
        minutes=_int_or_none(games.get("minutes")),
        goals=_int_or_none(goals.get("total")),
        assists=_int_or_none(goals.get("assists")),
        rating=rating,
        shots=_int_or_none(shots.get("total")),
        key_passes=_int_or_none(passes.get("key")),
        tackles=_int_or_none(tackles.get("total")),
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


def _int_or_none(value) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
