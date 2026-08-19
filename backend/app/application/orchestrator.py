from __future__ import annotations

import logging
from datetime import UTC, datetime

from app.application.registry import ProviderRegistry
from app.application.serialization import match_from_dict, match_to_dict
from app.domain.interfaces import ICache, ISnapshotRepository
from app.domain.models import DataConfidence, Match, SnapshotRecord, TeamContext

logger = logging.getLogger(__name__)

JUST_FINISHED_TTL = 6 * 60 * 60
CONTEXT_TTL = 60 * 60
PLAYER_STATS_TTL = 7 * 24 * 60 * 60


class ProviderOrchestrator:
    """Fallback chain + merge. New sources register on the registry; this class stays closed."""

    def __init__(
        self,
        registry: ProviderRegistry,
        cache: ICache,
        snapshots: ISnapshotRepository,
        team_hint: str = "Chelsea",
    ) -> None:
        self._registry = registry
        self._cache = cache
        self._snapshots = snapshots
        self._team_hint = team_hint

    async def just_finished(self, limit: int) -> list[Match]:
        cache_key = f"chelsea:just-finished:{limit}"
        cached = await self._cache.get_json(cache_key)
        if isinstance(cached, list) and cached:
            return [match_from_dict(item) for item in cached]
        snapshot = await self._snapshots.get(cache_key)
        if snapshot and isinstance(snapshot.payload.get("matches"), list):
            matches = [match_from_dict(item) for item in snapshot.payload["matches"]]
            await self._cache.set_json(cache_key, snapshot.payload["matches"], JUST_FINISHED_TTL)
            return matches

        matches = await self._load_fixtures(limit)
        enriched: list[Match] = []
        for match in matches:
            player_stats = await self._enrich_player_stats(match)
            extra_events = await self._enrich_events(match)
            events = match.events + tuple(extra_events)
            sources = match.sources
            if player_stats:
                sources = sources + (
                    DataConfidence(
                        source=player_stats[0].source or "player-stats",
                        score=0.85,
                        coverage_notes="Per-fixture ratings/stats attached",
                    ),
                )
            merged = Match(
                id=match.id,
                utc_kickoff=match.utc_kickoff,
                competition=match.competition,
                home=match.home,
                away=match.away,
                score=match.score,
                status=match.status,
                events=events,
                player_stats=tuple(player_stats) if player_stats else match.player_stats,
                venue=match.venue,
                matchday=match.matchday,
                sources=sources,
            )
            enriched.append(merged)
            await self._snapshots.upsert_match(merged)
        payload = [match_to_dict(m) for m in enriched]
        await self._cache.set_json(cache_key, payload, JUST_FINISHED_TTL)
        await self._snapshots.put(
            SnapshotRecord(key=cache_key, payload={"matches": payload}, stored_at=datetime.now(UTC))
        )
        return enriched

    async def team_context(self) -> TeamContext | None:
        cache_key = "chelsea:context"
        cached = await self._cache.get_json(cache_key)
        if isinstance(cached, dict) and cached.get("team_name"):
            return _context_from_dict(cached)
        for provider in self._registry.team_context:
            try:
                ctx = await provider.chelsea_context()
            except Exception:
                logger.exception("team context failed for %s", provider.name)
                continue
            if ctx is not None:
                await self._cache.set_json(cache_key, _context_to_dict(ctx), CONTEXT_TTL)
                return ctx
        return None

    async def _load_fixtures(self, limit: int) -> list[Match]:
        for provider in self._registry.fixtures:
            try:
                matches = await provider.recent_finished(team_hint=self._team_hint, limit=limit)
            except Exception:
                logger.exception("fixture provider %s failed", provider.name)
                continue
            if matches:
                return matches[:limit]
        return []

    async def _enrich_player_stats(self, match: Match):
        if match.player_stats:
            return list(match.player_stats)
        cache_key = f"fixture:{match.id}:players"
        for provider in self._registry.player_match_stats:
            try:
                stats = await provider.stats_for_match(match)
            except Exception:
                logger.exception("player stats %s failed", provider.name)
                continue
            if stats:
                await self._cache.set_json(
                    cache_key,
                    [{"id": s.player.id, "name": s.player.name} for s in stats],
                    PLAYER_STATS_TTL,
                )
                return stats
        return []

    async def _enrich_events(self, match: Match):
        extra = []
        existing = {(e.minute, e.event_type, e.player_name) for e in match.events}
        for provider in self._registry.historical_events:
            try:
                events = await provider.events_for_match(match)
            except Exception:
                logger.exception("historical events %s failed", provider.name)
                continue
            for event in events:
                key = (event.minute, event.event_type, event.player_name)
                if key not in existing:
                    extra.append(event)
                    existing.add(key)
        return extra


def _context_to_dict(ctx: TeamContext) -> dict:
    return {
        "team_name": ctx.team_name,
        "competition": ctx.competition,
        "position": ctx.position,
        "played": ctx.played,
        "points": ctx.points,
        "form": ctx.form,
        "goal_difference": ctx.goal_difference,
        "sources": [
            {"source": s.source, "score": s.score, "coverage_notes": s.coverage_notes}
            for s in ctx.sources
        ],
    }


def _context_from_dict(raw: dict) -> TeamContext:
    return TeamContext(
        team_name=raw["team_name"],
        competition=raw["competition"],
        position=raw.get("position"),
        played=raw.get("played"),
        points=raw.get("points"),
        form=raw.get("form"),
        goal_difference=raw.get("goal_difference"),
        sources=tuple(
            DataConfidence(
                source=s["source"],
                score=s["score"],
                coverage_notes=s.get("coverage_notes", ""),
            )
            for s in raw.get("sources", [])
        ),
    )
