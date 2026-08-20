from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta

from app.domain.models import (
    ClubRef,
    DataConfidence,
    EventType,
    Match,
    MatchEvent,
    MatchStatus,
    Score,
    TeamContext,
)
from app.infrastructure.http.rate_limit import RateLimitedClient
from app.infrastructure.providers.contracts.football_data import (
    FootballDataMatchListResponse,
    FootballDataStandingsResponse,
)

logger = logging.getLogger(__name__)

FINISHED_LOOKBACK_DAYS = 400


def finished_match_query_params() -> dict[str, str]:
    end = datetime.now(UTC).date()
    start = end - timedelta(days=FINISHED_LOOKBACK_DAYS)
    return {
        "status": "FINISHED",
        "dateFrom": start.isoformat(),
        "dateTo": end.isoformat(),
    }


class FootballDataProvider:
    name = "football-data.org"

    def __init__(
        self,
        client: RateLimitedClient,
        api_key: str,
        team_id: int,
    ) -> None:
        self._client = client
        self._api_key = api_key
        self._team_id = team_id

    async def recent_finished(self, *, team_hint: str, limit: int) -> list[Match]:
        _ = team_hint
        if not self._api_key:
            return []
        url = f"https://api.football-data.org/v4/teams/{self._team_id}/matches"
        response = await self._client.request(
            "GET",
            url,
            headers={"X-Auth-Token": self._api_key},
            params=finished_match_query_params(),
        )
        if response.status_code >= 400:
            logger.warning("football-data.org matches HTTP %s", response.status_code)
            return []
        payload = FootballDataMatchListResponse.model_validate(response.json())
        if payload.message:
            logger.info("football-data.org: %s", payload.message)
        matches = []
        for item in payload.matches:
            mapped = _map_match(item)
            if mapped is not None and mapped.status == MatchStatus.FINISHED:
                matches.append(mapped)
        matches.sort(key=lambda match: match.utc_kickoff, reverse=True)
        return matches[:limit]

    async def chelsea_context(self) -> TeamContext | None:
        if not self._api_key:
            return None
        url = "https://api.football-data.org/v4/competitions/PL/standings"
        response = await self._client.request(
            "GET", url, headers={"X-Auth-Token": self._api_key}
        )
        if response.status_code >= 400:
            return None
        payload = FootballDataStandingsResponse.model_validate(response.json())
        if not payload.standings:
            return None
        for row in payload.standings[0].table:
            team = row.team
            if team is None:
                continue
            if team.id == self._team_id or team.name == "Chelsea FC":
                return TeamContext(
                    team_name="Chelsea",
                    competition="Premier League",
                    position=row.position,
                    played=row.played_games,
                    points=row.points,
                    form=row.form,
                    goal_difference=row.goal_difference,
                    sources=(
                        DataConfidence(
                            self.name,
                            0.9,
                            "Premier League table from football-data.org",
                        ),
                    ),
                )
        return None


def _map_match(item) -> Match | None:
    try:
        utc = datetime.fromisoformat(item.utc_date.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None
    home = item.home_team
    away = item.away_team
    score_full = item.score.full_time if item.score else None
    home_goals = score_full.home if score_full else None
    away_goals = score_full.away if score_full else None
    events = []
    for ev in item.goals or []:
        minute = ev.minute if isinstance(ev.minute, int) else None
        scorer = ev.scorer.name if ev.scorer else None
        events.append(MatchEvent(minute, EventType.GOAL, scorer, ev.type))
    competition = item.competition.name if item.competition else "Unknown"
    status_raw = item.status or "UNKNOWN"
    try:
        status = MatchStatus(status_raw)
    except ValueError:
        status = MatchStatus.UNKNOWN
    return Match(
        id=f"fd-{item.id}",
        utc_kickoff=utc,
        competition=competition,
        home=ClubRef(home.name or "Home", home.tla, home.crest),
        away=ClubRef(away.name or "Away", away.tla, away.crest),
        score=None
        if home_goals is None or away_goals is None
        else Score(int(home_goals), int(away_goals)),
        status=status,
        events=tuple(events),
        venue=item.venue,
        matchday=item.matchday,
        sources=(
            DataConfidence("football-data.org", 0.92, "Fixtures and scores"),
        ),
    )
