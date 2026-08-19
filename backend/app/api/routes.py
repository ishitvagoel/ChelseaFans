from __future__ import annotations

from fastapi import APIRouter, Query, Request

from app.api.mappers import comparison_dto, context_dto, match_dto, player_dto
from app.api.schemas import ComparisonDto, MatchDto, MetaDto, PlayerDto, TeamContextDto
from app.application.comparison import ComparisonService
from app.application.just_finished import JustFinishedService

router = APIRouter(prefix="/v1")


def _just(request: Request) -> JustFinishedService:
    return request.app.state.container.just_finished


def _compare(request: Request) -> ComparisonService:
    return request.app.state.container.comparison


@router.get("/meta", response_model=MetaDto)
async def meta(request: Request) -> MetaDto:
    demo = bool(request.app.state.container.demo)
    if demo:
        message = "Sample data is enabled (USE_DEMO_DATA=true). Live sports APIs are not called."
    else:
        message = "Live providers are enabled. Set USE_DEMO_DATA=true to force sample data."
    return MetaDto(demo=demo, message=message)


@router.get("/chelsea/just-finished", response_model=list[MatchDto])
async def just_finished(
    request: Request,
    limit: int = Query(8, ge=1, le=10),
) -> list[MatchDto]:
    matches = await _just(request).execute(limit)
    return [match_dto(m) for m in matches]


@router.get("/chelsea/context", response_model=TeamContextDto | None)
async def chelsea_context(request: Request) -> TeamContextDto | None:
    ctx = await _just(request).team_context()
    if ctx is None:
        return None
    return context_dto(ctx)


@router.get("/players/search", response_model=list[PlayerDto])
async def search_players(
    request: Request,
    q: str = Query("", max_length=80),
) -> list[PlayerDto]:
    players = await _compare(request).search(q)
    return [player_dto(p) for p in players]


@router.get("/compare", response_model=ComparisonDto)
async def compare(
    request: Request,
    player_ids: str = Query(..., description="Comma-separated player ids (1-4)"),
    season_from: str | None = None,
    season_to: str | None = None,
) -> ComparisonDto:
    ids = [part.strip() for part in player_ids.split(",") if part.strip()]
    result = await _compare(request).compare(ids, season_from, season_to)
    return comparison_dto(result)
