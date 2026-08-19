from __future__ import annotations

from app.api.schemas import (
    ClubDto,
    ComparisonDto,
    ConfidenceDto,
    EventDto,
    MatchDto,
    MetricSliceDto,
    PlayerComparisonDto,
    PlayerDto,
    PlayerMatchStatsDto,
    ScoreDto,
    TeamContextDto,
)
from app.domain.models import (
    ComparisonResult,
    DataConfidence,
    Match,
    Player,
    PlayerComparison,
    TeamContext,
)


def player_dto(player: Player) -> PlayerDto:
    return PlayerDto(
        id=player.id,
        name=player.name,
        position=player.position,
        nationality=player.nationality,
        shirt_number=player.shirt_number,
    )


def confidence_dto(item: DataConfidence) -> ConfidenceDto:
    return ConfidenceDto(
        source=item.source, score=item.score, coverage_notes=item.coverage_notes
    )


def match_dto(match: Match) -> MatchDto:
    return MatchDto(
        id=match.id,
        utc_kickoff=match.utc_kickoff.isoformat(),
        competition=match.competition,
        home=ClubDto(
            name=match.home.name,
            short_name=match.home.short_name,
            crest_url=match.home.crest_url,
        ),
        away=ClubDto(
            name=match.away.name,
            short_name=match.away.short_name,
            crest_url=match.away.crest_url,
        ),
        score=None
        if match.score is None
        else ScoreDto(home=match.score.home, away=match.score.away),
        status=match.status.value,
        events=[
            EventDto(
                minute=e.minute,
                event_type=e.event_type.value,
                player_name=e.player_name,
                detail=e.detail,
            )
            for e in match.events
        ],
        player_stats=[
            PlayerMatchStatsDto(
                player=player_dto(s.player),
                minutes=s.minutes,
                goals=s.goals,
                assists=s.assists,
                rating=s.rating,
                shots=s.shots,
                key_passes=s.key_passes,
                progressive_passes=s.progressive_passes,
                progressive_carries=s.progressive_carries,
                tackles=s.tackles,
                source=s.source,
            )
            for s in match.player_stats
        ],
        venue=match.venue,
        matchday=match.matchday,
        sources=[confidence_dto(s) for s in match.sources],
    )


def context_dto(ctx: TeamContext) -> TeamContextDto:
    return TeamContextDto(
        team_name=ctx.team_name,
        competition=ctx.competition,
        position=ctx.position,
        played=ctx.played,
        points=ctx.points,
        form=ctx.form,
        goal_difference=ctx.goal_difference,
        sources=[confidence_dto(s) for s in ctx.sources],
    )


def comparison_dto(result: ComparisonResult) -> ComparisonDto:
    return ComparisonDto(
        players=[_player_comparison_dto(p) for p in result.players],
        season_from=result.season_from,
        season_to=result.season_to,
        sources=[confidence_dto(s) for s in result.sources],
    )


def _player_comparison_dto(item: PlayerComparison) -> PlayerComparisonDto:
    return PlayerComparisonDto(
        player=player_dto(item.player),
        season=MetricSliceDto(
            label=item.season.label,
            goals=item.season.goals,
            assists=item.season.assists,
            minutes=item.season.minutes,
            rating=item.season.rating,
            progressive_passes=item.season.progressive_passes,
            progressive_carries=item.season.progressive_carries,
        ),
        career=MetricSliceDto(
            label=item.career.label,
            goals=item.career.goals,
            assists=item.career.assists,
            minutes=item.career.minutes,
            rating=item.career.rating,
            progressive_passes=item.career.progressive_passes,
            progressive_carries=item.career.progressive_carries,
        ),
        source_notes=list(item.source_notes),
    )
