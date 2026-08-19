from __future__ import annotations

from app.application.comparison_engine import compare_players
from app.application.registry import ProviderRegistry
from app.domain.interfaces import IPlayerDirectory
from app.domain.models import ComparisonResult, DataConfidence, Player, SeasonTotals


class ComparisonService:
    def __init__(self, registry: ProviderRegistry, directory: IPlayerDirectory) -> None:
        self._registry = registry
        self._directory = directory

    async def search(self, query: str) -> list[Player]:
        q = query.strip()
        if len(q) < 1:
            return await self._directory.search("")
        found: dict[str, Player] = {}
        for player in await self._directory.search(q):
            found[player.id] = player
        for provider in self._registry.season_stats:
            try:
                for player in await provider.search_players(q):
                    found.setdefault(player.id, player)
            except Exception:
                continue
        return list(found.values())[:20]

    async def compare(
        self,
        player_ids: list[str],
        season_from: str | None,
        season_to: str | None,
    ) -> ComparisonResult:
        unique = list(dict.fromkeys(player_ids))[:4]
        comparisons = []
        sources: list[DataConfidence] = []
        for pid in unique:
            player = await self._directory.get(pid)
            totals: list[SeasonTotals] = []
            for provider in self._registry.season_stats:
                try:
                    rows = await provider.season_totals(
                        player_id=pid, season_from=season_from, season_to=season_to
                    )
                except Exception:
                    continue
                totals.extend(rows)
                if rows:
                    sources.append(
                        DataConfidence(
                            source=provider.name,
                            score=0.8,
                            coverage_notes="Season aggregates",
                        )
                    )
                    if player is None and rows:
                        player = rows[0].player
            if player is None:
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
