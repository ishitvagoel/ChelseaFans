"""Pydantic contracts for API-Football (API-Sports) v3 responses.

Docs: https://www.api-football.com/documentation-v3
Free tier: 100 req/day, 10 req/min; seasons limited (typically 2022–2024).
Auth header: x-apisports-key
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ApiFootballEnvelope(BaseModel):
    model_config = ConfigDict(extra="ignore")

    errors: dict[str, str] | list[Any] | None = None
    results: int | None = None

    def plan_error(self) -> str | None:
        if not self.errors:
            return None
        if isinstance(self.errors, dict):
            return self.errors.get("plan") or next(iter(self.errors.values()), None)
        return str(self.errors)


class ApiFootballFixtureInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    date: str | None = None
    status: dict[str, str | None] | None = None


class ApiFootballTeamInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int | None = None
    name: str | None = None
    logo: str | None = None


class ApiFootballGoals(BaseModel):
    model_config = ConfigDict(extra="ignore")

    home: int | None = None
    away: int | None = None


class ApiFootballLeagueInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int | None = None
    name: str | None = None
    season: int | None = None


class ApiFootballFixtureItem(BaseModel):
    model_config = ConfigDict(extra="ignore")

    fixture: ApiFootballFixtureInfo
    league: ApiFootballLeagueInfo | None = None
    teams: dict[str, ApiFootballTeamInfo] | None = None
    goals: ApiFootballGoals | None = None


class ApiFootballFixturesResponse(ApiFootballEnvelope):
    response: list[ApiFootballFixtureItem] = Field(default_factory=list)


class ApiFootballPlayerRef(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int | None = None
    name: str | None = None
    nationality: str | None = None


class ApiFootballPlayerGameStats(BaseModel):
    model_config = ConfigDict(extra="ignore")

    minutes: int | None = None
    rating: str | float | None = None
    appearences: int | None = None
    appearances: int | None = None


class ApiFootballPlayerGoalStats(BaseModel):
    model_config = ConfigDict(extra="ignore")

    total: int | None = None
    assists: int | None = None


class ApiFootballPlayerShotStats(BaseModel):
    model_config = ConfigDict(extra="ignore")

    total: int | None = None


class ApiFootballPlayerPassStats(BaseModel):
    model_config = ConfigDict(extra="ignore")

    key: int | None = None


class ApiFootballPlayerTackleStats(BaseModel):
    model_config = ConfigDict(extra="ignore")

    total: int | None = None


class ApiFootballPlayerStatisticsBlock(BaseModel):
    model_config = ConfigDict(extra="ignore")

    games: ApiFootballPlayerGameStats | None = None
    goals: ApiFootballPlayerGoalStats | None = None
    shots: ApiFootballPlayerShotStats | None = None
    passes: ApiFootballPlayerPassStats | None = None
    tackles: ApiFootballPlayerTackleStats | None = None


class ApiFootballFixturePlayerEntry(BaseModel):
    model_config = ConfigDict(extra="ignore")

    player: ApiFootballPlayerRef | None = None
    statistics: list[ApiFootballPlayerStatisticsBlock] = Field(default_factory=list)


class ApiFootballFixturePlayersTeamBlock(BaseModel):
    model_config = ConfigDict(extra="ignore")

    team: ApiFootballTeamInfo | None = None
    players: list[ApiFootballFixturePlayerEntry] = Field(default_factory=list)


class ApiFootballFixturePlayersResponse(ApiFootballEnvelope):
    response: list[ApiFootballFixturePlayersTeamBlock] = Field(default_factory=list)


class ApiFootballPlayerSeasonStatistics(BaseModel):
    model_config = ConfigDict(extra="ignore")

    league: ApiFootballLeagueInfo | None = None
    games: ApiFootballPlayerGameStats | None = None
    goals: ApiFootballPlayerGoalStats | None = None


class ApiFootballPlayerBlock(BaseModel):
    model_config = ConfigDict(extra="ignore")

    player: ApiFootballPlayerRef | None = None
    statistics: list[ApiFootballPlayerSeasonStatistics] = Field(default_factory=list)


class ApiFootballPlayersResponse(ApiFootballEnvelope):
    response: list[ApiFootballPlayerBlock] = Field(default_factory=list)


class ApiFootballSubscription(BaseModel):
    model_config = ConfigDict(extra="ignore")

    plan: str | None = None
    active: bool | None = None


class ApiFootballRequestQuota(BaseModel):
    model_config = ConfigDict(extra="ignore")

    current: int | None = None
    limit_day: int | None = Field(default=None, alias="limit_day")


class ApiFootballStatusPayload(BaseModel):
    model_config = ConfigDict(extra="ignore")

    subscription: ApiFootballSubscription | None = None
    requests: ApiFootballRequestQuota | None = None


class ApiFootballStatusResponse(ApiFootballEnvelope):
    response: ApiFootballStatusPayload | None = None
