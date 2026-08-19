from __future__ import annotations

from datetime import UTC, datetime

from app.domain.models import ClubRef, DataConfidence, Match, MatchStatus, Score
from app.infrastructure.http.rate_limit import RateLimitedClient

# English Premier League JSON dumps (openfootball). Path may change by season.
OPENFOOTBALL_PL = (
    "https://raw.githubusercontent.com/openfootball/football.json/master/{season}/en.1.json"
)


class OpenFootballProvider:
    name = "openfootball"

    def __init__(self, client: RateLimitedClient) -> None:
        self._client = client

    async def recent_finished(self, *, team_hint: str, limit: int) -> list[Match]:
        season = _current_season_path()
        url = OPENFOOTBALL_PL.format(season=season)
        response = await self._client.request("GET", url)
        if response.status_code >= 400:
            return []
        data = response.json()
        matches: list[Match] = []
        for round_block in data.get("matches") or data.get("rounds") or []:
            games = round_block.get("matches") if isinstance(round_block, dict) and "matches" in round_block else None
            iterable = games if games is not None else ([round_block] if "team1" in round_block or "score1" in round_block else [])
            if not iterable and isinstance(round_block, dict) and round_block.get("date"):
                iterable = [round_block]
            for game in iterable or []:
                mapped = _map_game(game, team_hint, data.get("name") or "Premier League")
                if mapped:
                    matches.append(mapped)
        # Alternative schema: top-level list of matches
        if not matches:
            for game in data.get("matches") or []:
                mapped = _map_game(game, team_hint, "Premier League")
                if mapped:
                    matches.append(mapped)
        matches.sort(key=lambda m: m.utc_kickoff, reverse=True)
        return [m for m in matches if m.status == MatchStatus.FINISHED][:limit]


def _current_season_path() -> str:
    now = datetime.now(UTC)
    start = now.year if now.month >= 7 else now.year - 1
    return f"{start}-{start + 1}"


def _map_game(game: dict, team_hint: str, competition: str) -> Match | None:
    team1 = game.get("team1") or game.get("home")
    team2 = game.get("team2") or game.get("away")
    if not isinstance(team1, str) or not isinstance(team2, str):
        return None
    hint = team_hint.lower()
    if hint not in team1.lower() and hint not in team2.lower():
        return None
    date_raw = game.get("date")
    if not date_raw:
        return None
    try:
        utc = datetime.fromisoformat(str(date_raw)[:10])
    except ValueError:
        return None
    s1 = game.get("score1") or game.get("ft1")
    s2 = game.get("score2") or game.get("ft2")
    finished = s1 is not None and s2 is not None
    return Match(
        id=f"of-{date_raw}-{team1}-{team2}",
        utc_kickoff=utc,
        competition=competition,
        home=ClubRef(team1),
        away=ClubRef(team2),
        score=None if not finished else Score(int(s1), int(s2)),
        status=MatchStatus.FINISHED if finished else MatchStatus.SCHEDULED,
        sources=(
            DataConfidence("openfootball", 0.55, "Open football.json scores; no player ratings"),
        ),
    )
