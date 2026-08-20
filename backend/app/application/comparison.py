from __future__ import annotations

import logging

from app.application.comparison_engine import compare_players
from app.application.registry import ProviderRegistry
from app.domain.interfaces import IPlayerDirectory
from app.domain.models import ComparisonResult, DataConfidence, Player, SeasonTotals

logger = logging.getLogger(__name__)

FREE_TIER_CAREER_FROM = "2022/23"
FREE_TIER_CAREER_TO = "2024/25"


class ComparisonService:
    def __init__(
        self,
        registry: ProviderRegistry,
        directory: IPlayerDirectory,
        *,
        allow_demo: bool = False,
    ) -> None:
        self._registry = registry
        self._directory = directory
        self._allow_demo = allow_demo

    def _visible(self, player: Player) -> bool:
        return self._allow_demo or not player.id.startswith("demo-")

    async def search(self, query: str) -> list[Player]:
        q = query.strip()
        found: dict[str, Player] = {}
        for player in await self._directory.search(q):
            if self._visible(player):
                found[player.id] = player
        for provider in self._registry.season_stats:
            try:
                for player in await provider.search_players(q):
                    if self._visible(player):
                        found.setdefault(player.id, player)
            except Exception:
                logger.exception("player search failed for %s", provider.name)
                continue
        return list(found.values())[:40]

    async def compare(
        self,
        player_ids: list[str],
        season_from: str | None,
        season_to: str | None,
    ) -> ComparisonResult:
        unique = list(dict.fromkeys(player_ids))[:4]
        if not self._allow_demo:
            unique = [pid for pid in unique if not pid.startswith("demo-")]
        comparisons = []
        sources: list[DataConfidence] = []
        for pid in unique:
            player = await self._directory.get(pid)
            totals: list[SeasonTotals] = []
            for provider in self._registry.season_stats:
                try:
                    rows = await provider.season_totals(
                        player_id=pid,
                        season_from=FREE_TIER_CAREER_FROM,
                        season_to=FREE_TIER_CAREER_TO,
                    )
                except Exception:
                    logger.exception("season totals failed for %s (%s)", provider.name, pid)
                    continue
                totals.extend(rows)
                if rows:
                    sources.append(
                        DataConfidence(
                            source=provider.name,
                            score=0.8,
                            coverage_notes="Season aggregates from API-Football free-tier seasons 2022–2024",
                        )
                    )
                    if player is None:
                        player = rows[0].player
            if player is None or not self._visible(player):
                continue
            comparisons.append(
                compare_players(
                    player=player,
                    all_totals=totals,
                    season_from=season_from,
                    season_to=season_to,
                )
            )
        return ComparisonResult(
            players=tuple(comparisons),
            season_from=season_from,
            season_to=season_to,
            sources=tuple(sources),
        )
