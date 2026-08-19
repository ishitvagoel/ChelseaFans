from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.sqlite import JSON as SQLITE_JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import JSON


class Base(DeclarativeBase):
    pass


JSONType = JSON().with_variant(SQLITE_JSON, "sqlite")


class SnapshotRow(Base):
    __tablename__ = "raw_snapshots"

    key: Mapped[str] = mapped_column(String(255), primary_key=True)
    payload: Mapped[dict] = mapped_column(JSONType, nullable=False)
    stored_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class PlayerRow(Base):
    __tablename__ = "players"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    position: Mapped[str | None] = mapped_column(String(64), nullable=True)
    nationality: Mapped[str | None] = mapped_column(String(64), nullable=True)
    shirt_number: Mapped[int | None] = mapped_column(Integer, nullable=True)


class MatchRow(Base):
    __tablename__ = "matches"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    payload: Mapped[dict] = mapped_column(JSONType, nullable=False)
    kickoff: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class ExternalIdRow(Base):
    __tablename__ = "external_ids"
    __table_args__ = (UniqueConstraint("provider", "entity_type", "external_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(32), nullable=False)
    external_id: Mapped[str] = mapped_column(String(128), nullable=False)
    internal_id: Mapped[str] = mapped_column(String(64), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
