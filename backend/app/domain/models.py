from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from enum import StrEnum
from typing import Any


class MatchStatus(StrEnum):
    FINISHED = "FINISHED"
    SCHEDULED = "SCHEDULED"
    LIVE = "LIVE"
    UNKNOWN = "UNKNOWN"


class EventType(StrEnum):
    GOAL = "GOAL"
    ASSIST = "ASSIST"
    CARD = "CARD"
    SUBSTITUTION = "SUBSTITUTION"
    OTHER = "OTHER"


@dataclass(frozen=True, slots=True)
class DataConfidence:
    source: str
    score: float
    coverage_notes: str = ""

    def __post_init__(self) -> None:
        if not 0.0 <= self.score <= 1.0:
            raise ValueError("confidence score must be in [0, 1]")


@dataclass(frozen=True, slots=True)
class Score:
    home: int
    away: int


@dataclass(frozen=True, slots=True)
class ClubRef:
    name: str
    short_name: str | None = None
    crest_url: str | None = None


@dataclass(frozen=True, slots=True)
class MatchEvent:
    minute: int | None
    event_type: EventType
    player_name: str | None
    detail: str | None = None


@dataclass(frozen=True, slots=True)
class Player:
    id: str
    name: str
    position: str | None = None
    nationality: str | None = None
    shirt_number: int | None = None


@dataclass(frozen=True, slots=True)
class PlayerMatchStats:
    player: Player
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


@dataclass(frozen=True, slots=True)
class Match:
    id: str
    utc_kickoff: datetime
    competition: str
    home: ClubRef
    away: ClubRef
    score: Score | None
    status: MatchStatus
    events: tuple[MatchEvent, ...] = ()
    player_stats: tuple[PlayerMatchStats, ...] = ()
    venue: str | None = None
    matchday: int | None = None
    sources: tuple[DataConfidence, ...] = ()


@dataclass(frozen=True, slots=True)
class SeasonTotals:
    player: Player
    season: str
    competition: str | None
    appearances: int | None = None
    minutes: int | None = None
    goals: int | None = None
    assists: int | None = None
    rating: float | None = None
    progressive_passes: int | None = None
    progressive_carries: int | None = None
    source: str = ""


@dataclass(frozen=True, slots=True)
class TeamContext:
    team_name: str
    competition: str
    position: int | None
    played: int | None
    points: int | None
    form: str | None
    goal_difference: int | None = None
    sources: tuple[DataConfidence, ...] = ()


@dataclass(frozen=True, slots=True)
class MetricSlice:
    label: str
    goals: float | None
    assists: float | None
    minutes: float | None
    rating: float | None
    progressive_passes: float | None
    progressive_carries: float | None


@dataclass(frozen=True, slots=True)
class PlayerComparison:
    player: Player
    season: MetricSlice
    career: MetricSlice
    source_notes: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ComparisonResult:
    players: tuple[PlayerComparison, ...]
    season_from: str | None
    season_to: str | None
    sources: tuple[DataConfidence, ...] = ()


@dataclass
class SnapshotRecord:
    key: str
    payload: dict[str, Any]
    stored_at: datetime = field(default_factory=lambda: datetime.now(UTC))


def season_label(d: date) -> str:
    start = d.year if d.month >= 7 else d.year - 1
    return f"{start}/{str(start + 1)[-2:]}"
