from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Column, UniqueConstraint
from sqlmodel import Field, SQLModel


class SnapshotRecordTable(SQLModel, table=True):
    __tablename__ = "raw_snapshots"

    key: str = Field(primary_key=True, max_length=255)
    payload: dict[str, Any] = Field(sa_column=Column(JSON, nullable=False))
    stored_at: datetime


class PlayerRecordTable(SQLModel, table=True):
    __tablename__ = "players"

    id: str = Field(primary_key=True, max_length=64)
    name: str = Field(max_length=128)
    position: str | None = Field(default=None, max_length=64)
    nationality: str | None = Field(default=None, max_length=64)
    shirt_number: int | None = None


class MatchRecordTable(SQLModel, table=True):
    __tablename__ = "matches"

    id: str = Field(primary_key=True, max_length=128)
    payload: dict[str, Any] = Field(sa_column=Column(JSON, nullable=False))
    kickoff: datetime


class ExternalIdRecordTable(SQLModel, table=True):
    __tablename__ = "external_ids"
    __table_args__ = (UniqueConstraint("provider", "entity_type", "external_id"),)

    id: int | None = Field(default=None, primary_key=True)
    provider: str = Field(max_length=64)
    entity_type: str = Field(max_length=32)
    external_id: str = Field(max_length=128)
    internal_id: str = Field(max_length=64)
    notes: str | None = None
