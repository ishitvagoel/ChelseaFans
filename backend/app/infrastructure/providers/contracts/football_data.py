"""Pydantic contracts for football-data.org v4 responses (free tier).

Docs: https://docs.football-data.org/general/v4/index.html
Free tier: 10 req/min, 12 competitions, delayed scores; no lineups/goals on base free.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class FootballDataTeamRef(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int | None = None
    name: str | None = None
    tla: str | None = None
    crest: str | None = None


class FootballDataScoreDetail(BaseModel):
    model_config = ConfigDict(extra="ignore")

    home: int | None = None
    away: int | None = None


class FootballDataScore(BaseModel):
    model_config = ConfigDict(extra="ignore")

    full_time: FootballDataScoreDetail | None = Field(default=None, alias="fullTime")
    half_time: FootballDataScoreDetail | None = Field(default=None, alias="halfTime")
    winner: str | None = None


class FootballDataGoal(BaseModel):
    model_config = ConfigDict(extra="ignore")

    minute: int | None = None
    type: str | None = None
    scorer: FootballDataTeamRef | None = None


class FootballDataCompetitionRef(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int | None = None
    name: str | None = None
    code: str | None = None


class FootballDataMatch(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    utc_date: str = Field(alias="utcDate")
    status: str
    home_team: FootballDataTeamRef = Field(alias="homeTeam")
    away_team: FootballDataTeamRef = Field(alias="awayTeam")
    score: FootballDataScore | None = None
    competition: FootballDataCompetitionRef | None = None
    venue: str | None = None
    matchday: int | None = None
    goals: list[FootballDataGoal] | None = None


class FootballDataResultSet(BaseModel):
    model_config = ConfigDict(extra="ignore")

    count: int | None = None
    competitions: str | None = None
    first: str | None = None
    last: str | None = None


class FootballDataMatchListResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    matches: list[FootballDataMatch] = Field(default_factory=list)
    result_set: FootballDataResultSet | None = Field(default=None, alias="resultSet")
    message: str | None = None


class FootballDataTableRow(BaseModel):
    model_config = ConfigDict(extra="ignore")

    position: int | None = None
    played_games: int | None = Field(default=None, alias="playedGames")
    points: int | None = None
    form: str | None = None
    goal_difference: int | None = Field(default=None, alias="goalDifference")
    team: FootballDataTeamRef | None = None


class FootballDataStandingBlock(BaseModel):
    model_config = ConfigDict(extra="ignore")

    table: list[FootballDataTableRow] = Field(default_factory=list)


class FootballDataStandingsResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    standings: list[FootballDataStandingBlock] = Field(default_factory=list)
    message: str | None = None


class FootballDataTeamResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int | None = None
    name: str | None = None
    message: str | None = None
