from __future__ import annotations

import logging
from datetime import UTC, datetime

from app.application.registry import ProviderRegistry
from app.application.serialization import match_from_dict, match_to_dict, player_stats_from_dict, player_stats_to_dict
from app.domain.interfaces import ICache, ISnapshotRepository
from app.domain.models import DataConfidence, Match, SnapshotRecord, TeamContext

logger = logging.getLogger(__name__)

JUST_FINISHED_TTL = 6 * 60 * 60
CONTEXT_TTL = 60 * 60
PLAYER_STATS_TTL = 7 * 24 * 60 * 60
JUST_FINISHED_CACHE_VERSION = "v3"


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
        cache_key = f"chelsea:just-finished:{JUST_FINISHED_CACHE_VERSION}:{limit}"
        cached = await self._cache.get_json(cache_key)
        if isinstance(cached, list) and cached:
            matches = [match_from_dict(item) for item in cached]
            if self._needs_stats_backfill(matches):
                matches = await self._backfill_player_stats(matches)
                await self._persist_just_finished(cache_key, matches)
            return matches

        snapshot = await self._snapshots.get(cache_key)
        stored = snapshot.payload.get("matches") if snapshot else None
        if isinstance(stored, list) and stored:
            matches = [match_from_dict(item) for item in stored]
            if self._needs_stats_backfill(matches):
                matches = await self._backfill_player_stats(matches)
                await self._persist_just_finished(cache_key, matches)
            else:
                await self._cache.set_json(cache_key, stored, JUST_FINISHED_TTL)
            return matches

        primary = await self._load_primary_fixtures(limit)
        enriched = await self._enrich_matches(primary)
        if primary and not any(match.player_stats for match in enriched):
            rated = await self._load_rated_fixture_fallback(limit)
            if rated:
                enriched = await self._enrich_matches(
                    rated,
                    coverage_note=(
                        "Showing rated fixtures from API-Football free-tier seasons (2022–2024). "
                        "Current-season ratings need a paid API-Football plan."
                    ),
                )

        if enriched:
            await self._persist_just_finished(cache_key, enriched)
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

    async def _load_primary_fixtures(self, limit: int) -> list[Match]:
        for provider in self._registry.fixtures:
            if provider.name == "api-football":
                continue
            try:
                matches = await provider.recent_finished(team_hint=self._team_hint, limit=limit)
            except Exception:
                logger.exception("fixture provider %s failed", provider.name)
                continue
            if matches:
                return matches[:limit]
        return []

    async def _load_rated_fixture_fallback(self, limit: int) -> list[Match]:
        for provider in self._registry.fixtures:
            if provider.name != "api-football":
                continue
            try:
                matches = await provider.recent_finished(team_hint=self._team_hint, limit=limit)
            except Exception:
                logger.exception("rated fixture fallback failed for %s", provider.name)
                continue
            if matches:
                return matches[:limit]
        return []

    async def _enrich_matches(
        self,
        matches: list[Match],
        *,
        coverage_note: str | None = None,
    ) -> list[Match]:
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
            elif coverage_note:
                sources = sources + (
                    DataConfidence(
                        source="api-football",
                        score=0.4,
                        coverage_notes=coverage_note,
                    ),
                )
            enriched.append(
                Match(
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
            )
            try:
                await self._snapshots.upsert_match(enriched[-1])
            except Exception:
                logger.exception("snapshot persist failed for %s", match.id)
        return enriched

    async def _persist_just_finished(self, cache_key: str, matches: list[Match]) -> None:
        payload = [match_to_dict(match) for match in matches]
        try:
            await self._cache.set_json(cache_key, payload, JUST_FINISHED_TTL)
            await self._snapshots.put(
                SnapshotRecord(key=cache_key, payload={"matches": payload}, stored_at=datetime.now(UTC))
            )
        except Exception:
            logger.exception("cache or snapshot write failed for %s", cache_key)

    def _needs_stats_backfill(self, matches: list[Match]) -> bool:
        if not matches:
            return False
        if any(match.player_stats for match in matches):
            return False
        return any(provider.name == "api-football" for provider in self._registry.player_match_stats)

    async def _backfill_player_stats(self, matches: list[Match]) -> list[Match]:
        updated: list[Match] = []
        changed = False
        for match in matches:
            stats = await self._enrich_player_stats(match)
            if stats:
                changed = True
                sources = match.sources + (
                    DataConfidence(
                        source=stats[0].source or "player-stats",
                        score=0.85,
                        coverage_notes="Per-fixture ratings/stats attached",
                    ),
                )
                updated.append(
                    Match(
                        id=match.id,
                        utc_kickoff=match.utc_kickoff,
                        competition=match.competition,
                        home=match.home,
                        away=match.away,
                        score=match.score,
                        status=match.status,
                        events=match.events,
                        player_stats=tuple(stats),
                        venue=match.venue,
                        matchday=match.matchday,
                        sources=sources,
                    )
                )
            else:
                updated.append(match)
        return updated if changed else matches

    async def _enrich_player_stats(self, match: Match):
        if match.player_stats:
            return list(match.player_stats)
        cache_key = f"fixture:{match.id}:player_stats:{JUST_FINISHED_CACHE_VERSION}"
        cached = await self._cache.get_json(cache_key)
        if isinstance(cached, list) and cached:
            return [player_stats_from_dict(item) for item in cached]
        for provider in self._registry.player_match_stats:
            try:
                stats = await provider.stats_for_match(match)
            except Exception:
                logger.exception("player stats %s failed", provider.name)
                continue
            if stats:
                payload = [player_stats_to_dict(stat) for stat in stats]
                await self._cache.set_json(cache_key, payload, PLAYER_STATS_TTL)
                return stats
        return []

    async def _enrich_events(self, match: Match):
        extra = []
        existing = {(event.minute, event.event_type, event.player_name) for event in match.events}
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
            {"source": source.source, "score": source.score, "coverage_notes": source.coverage_notes}
            for source in ctx.sources
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
                source=source["source"],
                score=source["score"],
                coverage_notes=source.get("coverage_notes", ""),
            )
            for source in raw.get("sources", [])
        ),
    )
