from __future__ import annotations

import logging
from dataclasses import dataclass

from redis.asyncio import from_url as redis_from_url

from app.application.comparison import ComparisonService
from app.application.just_finished import JustFinishedService
from app.application.orchestrator import ProviderOrchestrator
from app.application.registry import ProviderRegistry
from app.domain.interfaces import ICache, ISnapshotRepository
from app.infrastructure.cache.memory import InMemoryCache
from app.infrastructure.cache.redis_cache import RedisCache
from app.infrastructure.cache.upstash import UpstashRestCache
from app.infrastructure.db.engine import create_schema, make_engine, make_session_factory
from app.infrastructure.db.null_repository import NullSnapshotRepository
from app.infrastructure.db.repository import SqlModelSnapshotRepository
from app.infrastructure.demo.data import PLAYERS
from app.infrastructure.demo.provider import DemoProvider
from app.infrastructure.directory import CompositePlayerDirectory
from app.infrastructure.http.rate_limit import RateLimitedClient
from app.infrastructure.providers.api_football import ApiFootballProvider
from app.infrastructure.providers.api_football_fixtures import ApiFootballFixtureProvider
from app.infrastructure.providers.football_data import FootballDataProvider
from app.infrastructure.providers.openfootball import OpenFootballProvider
from app.infrastructure.providers.statsbomb import StatsBombProvider
from app.settings import Settings

logger = logging.getLogger(__name__)


@dataclass
class AppContainer:
    settings: Settings
    cache: ICache
    snapshots: ISnapshotRepository
    registry: ProviderRegistry
    just_finished: JustFinishedService
    comparison: ComparisonService
    http_clients: list[RateLimitedClient]
    demo: bool
    persistence: bool


async def build_container(settings: Settings) -> AppContainer:
    cache = await _build_cache(settings)
    snapshots, engine = await _build_snapshots(settings)
    registry = ProviderRegistry()
    http_clients: list[RateLimitedClient] = []

    if settings.use_demo_data:
        _register_demo(registry)
    else:
        http_clients = _register_live(registry, settings)

    orchestrator = ProviderOrchestrator(registry, cache, snapshots)
    if not settings.use_demo_data:
        try:
            removed = await snapshots.purge_prefix("demo-")
            if removed:
                logger.info("purged %s leftover demo snapshot rows", removed)
        except Exception:
            logger.exception("failed to purge leftover demo snapshot rows")
    directory = CompositePlayerDirectory(
        snapshots,
        extra=list(PLAYERS.values()) if settings.use_demo_data else [],
    )
    return AppContainer(
        settings=settings,
        cache=cache,
        snapshots=snapshots,
        registry=registry,
        just_finished=JustFinishedService(orchestrator),
        comparison=ComparisonService(registry, directory, allow_demo=settings.use_demo_data),
        http_clients=http_clients,
        demo=settings.use_demo_data,
        persistence=engine is not None,
    )


def _register_demo(registry: ProviderRegistry) -> None:
    demo = DemoProvider()
    registry.register_fixtures(demo)
    registry.register_player_match_stats(demo)
    registry.register_season_stats(demo)
    registry.register_historical_events(demo)
    registry.register_team_context(demo)


def _register_live(registry: ProviderRegistry, settings: Settings) -> list[RateLimitedClient]:
    fd_http = RateLimitedClient(min_interval_seconds=6.5)
    af_http = RateLimitedClient(min_interval_seconds=2.0)
    open_http = RateLimitedClient(min_interval_seconds=2.0)
    football_data = FootballDataProvider(
        fd_http, settings.football_data_api_key, settings.chelsea_football_data_team_id
    )
    api_football = ApiFootballProvider(
        af_http,
        settings.api_football_key,
        settings.chelsea_api_football_team_id,
        settings.api_football_base_url,
    )
    statsbomb = StatsBombProvider(open_http)
    openfootball = OpenFootballProvider(open_http)
    if settings.football_data_api_key:
        registry.register_fixtures(football_data)
        registry.register_team_context(football_data)
    registry.register_fixtures(openfootball)
    if settings.api_football_key:
        registry.register_fixtures(
            ApiFootballFixtureProvider(
                af_http,
                settings.api_football_key,
                settings.chelsea_api_football_team_id,
                settings.api_football_base_url,
            )
        )
        registry.register_player_match_stats(api_football)
        registry.register_season_stats(api_football)
        registry.register_historical_events(api_football)
    registry.register_historical_events(statsbomb)
    return [fd_http, af_http, open_http]


async def _build_cache(settings: Settings) -> ICache:
    if settings.upstash_redis_rest_url and settings.upstash_redis_rest_token:
        return UpstashRestCache(
            settings.upstash_redis_rest_url, settings.upstash_redis_rest_token
        )
    if settings.redis_url:
        client = redis_from_url(settings.redis_url, decode_responses=True)
        return RedisCache(client)
    return InMemoryCache()


async def _build_snapshots(settings: Settings) -> tuple[ISnapshotRepository, object | None]:
    if not settings.database_url:
        return NullSnapshotRepository(), None
    try:
        engine = make_engine(settings.database_url)
        await create_schema(engine)
        factory = make_session_factory(engine)
        return SqlModelSnapshotRepository(factory), engine
    except Exception:
        logger.exception("database snapshot repository failed to initialize")
        return NullSnapshotRepository(), None
