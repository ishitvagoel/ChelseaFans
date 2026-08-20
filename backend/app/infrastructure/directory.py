from __future__ import annotations

from app.domain.interfaces import ISnapshotRepository
from app.domain.models import Player
from app.infrastructure.demo.data import PLAYERS


class CompositePlayerDirectory:
    def __init__(self, snapshots: ISnapshotRepository, extra: list[Player] | None = None) -> None:
        self._snapshots = snapshots
        self._extra = list(PLAYERS.values()) if extra is None else extra
        self._allow_demo = any(player.id.startswith("demo-") for player in self._extra)

    def _visible(self, player: Player) -> bool:
        return self._allow_demo or not player.id.startswith("demo-")

    async def search(self, query: str) -> list[Player]:
        q = query.lower().strip()
        merged: dict[str, Player] = {p.id: p for p in self._extra if self._visible(p)}
        for player in await self._snapshots.list_players():
            if self._visible(player):
                merged[player.id] = player
        players = list(merged.values())
        if not q:
            return players
        return [p for p in players if q in p.name.lower() or q in p.id.lower()]

    async def get(self, player_id: str) -> Player | None:
        if player_id.startswith("demo-") and not self._allow_demo:
            return None
        for player in self._extra:
            if player.id == player_id:
                return player
        for player in await self._snapshots.list_players():
            if player.id == player_id:
                return player
        return None
