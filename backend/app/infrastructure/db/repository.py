from __future__ import annotations

from sqlalchemy import delete, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.application.serialization import match_to_dict
from app.domain.models import Match, Player, SnapshotRecord
from app.infrastructure.db.models import MatchRecordTable, PlayerRecordTable, SnapshotRecordTable


class SqlModelSnapshotRepository:
    def __init__(self, factory) -> None:
        self._factory = factory

    async def get(self, key: str) -> SnapshotRecord | None:
        async with self._factory() as session:
            row = await session.get(SnapshotRecordTable, key)
            if row is None:
                return None
            return SnapshotRecord(key=row.key, payload=row.payload, stored_at=row.stored_at)

    async def put(self, record: SnapshotRecord) -> None:
        async with self._factory() as session:
            existing = await session.get(SnapshotRecordTable, record.key)
            if existing is None:
                session.add(
                    SnapshotRecordTable(
                        key=record.key,
                        payload=record.payload,
                        stored_at=record.stored_at,
                    )
                )
            else:
                existing.payload = record.payload
                existing.stored_at = record.stored_at
            await session.commit()

    async def list_players(self) -> list[Player]:
        async with self._factory() as session:
            result = await session.scalars(select(PlayerRecordTable))
            return [
                Player(
                    id=row.id,
                    name=row.name,
                    position=row.position,
                    nationality=row.nationality,
                    shirt_number=row.shirt_number,
                )
                for row in result
            ]

    async def upsert_player(self, player: Player) -> None:
        async with self._factory() as session:
            existing = await session.get(PlayerRecordTable, player.id)
            if existing is None:
                session.add(
                    PlayerRecordTable(
                        id=player.id,
                        name=player.name,
                        position=player.position,
                        nationality=player.nationality,
                        shirt_number=player.shirt_number,
                    )
                )
            else:
                existing.name = player.name
                existing.position = player.position
                existing.nationality = player.nationality
                existing.shirt_number = player.shirt_number
            await session.commit()

    async def upsert_match(self, match: Match) -> None:
        payload = match_to_dict(match)
        async with self._factory() as session:
            existing = await session.get(MatchRecordTable, match.id)
            if existing is None:
                session.add(
                    MatchRecordTable(id=match.id, payload=payload, kickoff=match.utc_kickoff)
                )
            else:
                existing.payload = payload
                existing.kickoff = match.utc_kickoff
            for stats in match.player_stats:
                if stats.player.id.startswith("demo-"):
                    continue
                prow = await session.get(PlayerRecordTable, stats.player.id)
                if prow is None:
                    session.add(
                        PlayerRecordTable(
                            id=stats.player.id,
                            name=stats.player.name,
                            position=stats.player.position,
                            nationality=stats.player.nationality,
                            shirt_number=stats.player.shirt_number,
                        )
                    )
            await session.commit()

    async def purge_prefix(self, prefix: str) -> int:
        pattern = f"{prefix}%"
        async with self._factory() as session:
            players = await session.execute(
                delete(PlayerRecordTable).where(PlayerRecordTable.id.like(pattern))
            )
            matches = await session.execute(
                delete(MatchRecordTable).where(MatchRecordTable.id.like(pattern))
            )
            await session.commit()
            return int(players.rowcount or 0) + int(matches.rowcount or 0)
