from __future__ import annotations

import logging

from app.domain.models import ClubRef, DataConfidence, Match, MatchStatus, Score
from app.infrastructure.http.rate_limit import RateLimitedClient
from app.infrastructure.providers.api_football_helpers import (
    accessible_seasons_descending,
    club_names_match,
)
from app.infrastructure.providers.contracts.api_football import (
    ApiFootballFixtureItem,
    ApiFootballFixturesResponse,
)

logger = logging.getLogger(__name__)

ALLOWED_LEAGUES = frozenset({"Premier League", "FA Cup", "UEFA Champions League"})


class ApiFootballFixtureProvider:
    """Finished Chelsea fixtures from API-Football seasons available on the free tier."""

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

    async def recent_finished(self, *, team_hint: str, limit: int) -> list[Match]:
        _ = team_hint
        if not self._api_key:
            return []
        for season in accessible_seasons_descending():
            matches = await self._finished_for_season(season, limit)
            if matches:
                return matches[:limit]
        return []

    async def _finished_for_season(self, season: int, limit: int) -> list[Match]:
        response = await self._client.request(
            "GET",
            f"{self._base}/fixtures",
            headers=self._headers(),
            params={
                "team": str(self._team_id),
                "season": str(season),
                "status": "FT",
            },
        )
        if response.status_code >= 400:
            return []
        payload = ApiFootballFixturesResponse.model_validate(response.json())
        if payload.plan_error():
            logger.info("api-football fixtures skipped for season %s: %s", season, payload.plan_error())
            return []
        matches: list[Match] = []
        for item in payload.response:
            league_name = item.league.name if item.league else None
            if league_name and league_name not in ALLOWED_LEAGUES:
                continue
            mapped = _map_fixture(item)
            if mapped is not None:
                matches.append(mapped)
        matches.sort(key=lambda match: match.utc_kickoff, reverse=True)
        return matches[:limit]


def _map_fixture(item: ApiFootballFixtureItem) -> Match | None:
    fixture_id = item.fixture.id
    date_raw = item.fixture.date
    if not date_raw:
        return None
    try:
        from datetime import datetime

        utc = datetime.fromisoformat(str(date_raw).replace("Z", "+00:00"))
    except ValueError:
        return None
    teams = item.teams or {}
    home = teams.get("home")
    away = teams.get("away")
    home_name = home.name if home else "Home"
    away_name = away.name if away else "Away"
    league = item.league.name if item.league else "Unknown"
    goals = item.goals
    home_goals = goals.home if goals else None
    away_goals = goals.away if goals else None
    return Match(
        id=f"af-{fixture_id}",
        utc_kickoff=utc,
        competition=league,
        home=ClubRef(home_name, None, home.logo if home else None),
        away=ClubRef(away_name, None, away.logo if away else None),
        score=None
        if home_goals is None or away_goals is None
        else Score(int(home_goals), int(away_goals)),
        status=MatchStatus.FINISHED,
        sources=(
            DataConfidence(
                "api-football",
                0.88,
                "Rated fixtures from API-Football free-tier seasons (2022–2024)",
            ),
        ),
    )


def fixture_item_matches_clubs(item: ApiFootballFixtureItem, home_name: str, away_name: str) -> bool:
    teams = item.teams or {}
    home = teams.get("home")
    away = teams.get("away")
    home_api = home.name if home else ""
    away_api = away.name if away else ""
    direct = club_names_match(home_name, home_api) and club_names_match(away_name, away_api)
    swapped = club_names_match(home_name, away_api) and club_names_match(away_name, home_api)
    return direct or swapped
