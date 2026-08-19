"""Pydantic contracts for openfootball/football.json season dumps (GitHub, no auth).

Source: https://github.com/openfootball/football.json
Free: public JSON; schema varies by season file.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class OpenFootballMatchRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")

    date: str | None = None
    team1: str | None = None
    team2: str | None = None
    home: str | None = None
    away: str | None = None
    score1: int | None = None
    score2: int | None = None
    ft1: int | None = None
    ft2: int | None = None


class OpenFootballRoundBlock(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str | None = None
    matches: list[OpenFootballMatchRecord] = Field(default_factory=list)


class OpenFootballSeasonFile(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str | None = None
    matches: list[OpenFootballMatchRecord] = Field(default_factory=list)
    rounds: list[OpenFootballRoundBlock] = Field(default_factory=list)
