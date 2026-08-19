from __future__ import annotations

from dataclasses import dataclass, field

from app.application.registry import ProviderRegistry
from app.domain.models import Match


class CountingFixtureProvider:
    name = "counter"

    def __init__(self, matches: list[Match]) -> None:
        self.matches = matches
        self.calls = 0

    async def recent_finished(self, *, team_hint: str, limit: int) -> list[Match]:
        self.calls += 1
        _ = team_hint
        return self.matches[:limit]


@dataclass
class FakeRegistryState:
    registry: ProviderRegistry = field(default_factory=ProviderRegistry)
