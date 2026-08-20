from __future__ import annotations

from app.domain.models import Match, Player, SnapshotRecord


class NullSnapshotRepository:
    """No-op persistence when DATABASE_URL is unset."""

    def __init__(self) -> None:
        self._snaps: dict[str, SnapshotRecord] = {}
        self._players: dict[str, Player] = {}

    async def get(self, key: str) -> SnapshotRecord | None:
        return self._snaps.get(key)

    async def put(self, record: SnapshotRecord) -> None:
        self._snaps[record.key] = record

    async def list_players(self) -> list[Player]:
        return list(self._players.values())

    async def upsert_player(self, player: Player) -> None:
        self._players[player.id] = player

    async def upsert_match(self, match: Match) -> None:
        for stats in match.player_stats:
            self._players[stats.player.id] = stats.player

    async def purge_prefix(self, prefix: str) -> int:
        removed = [player_id for player_id in self._players if player_id.startswith(prefix)]
        for player_id in removed:
            del self._players[player_id]
        return len(removed)
