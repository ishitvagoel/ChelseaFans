from __future__ import annotations

from app.infrastructure.demo.data import (
    PLAYERS,
    demo_matches,
    demo_season_totals,
    demo_team_context,
)
from app.domain.models import Match, MatchEvent, Player, PlayerMatchStats, SeasonTotals, TeamContext


class DemoProvider:
    """Implements every provider port so missing API keys still yield a working product."""

    name = "demo"

    async def recent_finished(self, *, team_hint: str, limit: int) -> list[Match]:
        _ = team_hint
        return demo_matches()[:limit]

    async def stats_for_match(self, match: Match) -> list[PlayerMatchStats]:
        return list(match.player_stats)

    async def season_totals(
        self,
        *,
        player_id: str,
        season_from: str | None,
        season_to: str | None,
    ) -> list[SeasonTotals]:
        _ = season_from, season_to
        return [row for row in demo_season_totals() if row.player.id == player_id]

    async def search_players(self, query: str) -> list[Player]:
        q = query.lower().strip()
        players = list(PLAYERS.values())
        if not q:
            return players
        return [p for p in players if q in p.name.lower()]

    async def events_for_match(self, match: Match) -> list[MatchEvent]:
        return list(match.events)

    async def chelsea_context(self) -> TeamContext | None:
        return demo_team_context()
