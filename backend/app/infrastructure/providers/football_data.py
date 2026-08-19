from __future__ import annotations

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

# football-data.org defaults /teams/{id}/matches to a future window when
# dateFrom/dateTo are omitted, so FINISHED returns nothing in-season.
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
            return []
        data = response.json()
        matches = []
        for item in data.get("matches", []):
            mapped = _map_match(item)
            if mapped is not None and mapped.status == MatchStatus.FINISHED:
                matches.append(mapped)
        matches.sort(key=lambda m: m.utc_kickoff, reverse=True)
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
        data = response.json()
        tables = data.get("standings") or []
        if not tables:
            return None
        for row in tables[0].get("table", []):
            team = row.get("team") or {}
            if team.get("id") == self._team_id or team.get("name") == "Chelsea FC":
                return TeamContext(
                    team_name="Chelsea",
                    competition="Premier League",
                    position=row.get("position"),
                    played=row.get("playedGames"),
                    points=row.get("points"),
                    form=row.get("form"),
                    goal_difference=row.get("goalDifference"),
                    sources=(
                        DataConfidence(
                            self.name,
                            0.9,
                            "Premier League table from football-data.org",
                        ),
                    ),
                )
        return None


def _map_match(item: dict) -> Match | None:
    try:
        utc = datetime.fromisoformat(item["utcDate"].replace("Z", "+00:00"))
    except (KeyError, ValueError):
        return None
    home = item.get("homeTeam") or {}
    away = item.get("awayTeam") or {}
    score_full = (item.get("score") or {}).get("fullTime") or {}
    home_goals = score_full.get("home")
    away_goals = score_full.get("away")
    events = []
    for ev in item.get("goals") or []:
        minute = (ev.get("minute") if isinstance(ev.get("minute"), int) else None)
        scorer = (ev.get("scorer") or {}).get("name")
        events.append(MatchEvent(minute, EventType.GOAL, scorer, ev.get("type")))
    competition = (item.get("competition") or {}).get("name") or "Unknown"
    status_raw = item.get("status") or "UNKNOWN"
    try:
        status = MatchStatus(status_raw)
    except ValueError:
        status = MatchStatus.UNKNOWN
    return Match(
        id=f"fd-{item.get('id')}",
        utc_kickoff=utc,
        competition=competition,
        home=ClubRef(home.get("name") or "Home", home.get("tla"), home.get("crest")),
        away=ClubRef(away.get("name") or "Away", away.get("tla"), away.get("crest")),
        score=None
        if home_goals is None or away_goals is None
        else Score(int(home_goals), int(away_goals)),
        status=status,
        events=tuple(events),
        venue=(item.get("venue")),
        matchday=item.get("matchday"),
        sources=(
            DataConfidence("football-data.org", 0.92, "Fixtures, scores, goals"),
        ),
    )
