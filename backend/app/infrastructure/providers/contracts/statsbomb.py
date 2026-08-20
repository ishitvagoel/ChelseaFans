"""Pydantic contracts for StatsBomb Open Data event files (GitHub, no auth).

Source: https://github.com/statsbomb/open-data
Free: CC BY 4.0; sparse Chelsea coverage in open sets.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class StatsBombEventType(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str | None = None


class StatsBombEventPlayer(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str | None = None


class StatsBombEventRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")

    minute: int | None = None
    type: StatsBombEventType | None = None
    player: StatsBombEventPlayer | None = None
