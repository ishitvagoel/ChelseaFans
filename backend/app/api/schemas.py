from __future__ import annotations

from pydantic import BaseModel, Field


class ConfidenceDto(BaseModel):
    source: str
    score: float
    coverage_notes: str = ""


class ClubDto(BaseModel):
    name: str
    short_name: str | None = None
    crest_url: str | None = None


class ScoreDto(BaseModel):
    home: int
    away: int


class EventDto(BaseModel):
    minute: int | None
    event_type: str
    player_name: str | None
    detail: str | None = None


class PlayerDto(BaseModel):
    id: str
    name: str
    position: str | None = None
    nationality: str | None = None
    shirt_number: int | None = None


class PlayerMatchStatsDto(BaseModel):
    player: PlayerDto
    minutes: int | None = None
    goals: int | None = None
    assists: int | None = None
    rating: float | None = None
    shots: int | None = None
    key_passes: int | None = None
    progressive_passes: int | None = None
    progressive_carries: int | None = None
    tackles: int | None = None
    source: str = ""


class MatchDto(BaseModel):
    id: str
    utc_kickoff: str
    competition: str
    home: ClubDto
    away: ClubDto
    score: ScoreDto | None
    status: str
    events: list[EventDto]
    player_stats: list[PlayerMatchStatsDto]
    venue: str | None = None
    matchday: int | None = None
    sources: list[ConfidenceDto]


class TeamContextDto(BaseModel):
    team_name: str
    competition: str
    position: int | None
    played: int | None
    points: int | None
    form: str | None
    goal_difference: int | None = None
    sources: list[ConfidenceDto]


class MetricSliceDto(BaseModel):
    label: str
    goals: float | None
    assists: float | None
    minutes: float | None
    rating: float | None
    progressive_passes: float | None
    progressive_carries: float | None


class PlayerComparisonDto(BaseModel):
    player: PlayerDto
    season: MetricSliceDto
    career: MetricSliceDto
    source_notes: list[str] = Field(default_factory=list)


class ComparisonDto(BaseModel):
    players: list[PlayerComparisonDto]
    season_from: str | None
    season_to: str | None
    sources: list[ConfidenceDto]
