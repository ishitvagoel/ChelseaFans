from __future__ import annotations

from app.application.orchestrator import ProviderOrchestrator
from app.domain.models import Match, TeamContext


class JustFinishedService:
    def __init__(self, orchestrator: ProviderOrchestrator) -> None:
        self._orchestrator = orchestrator

    async def execute(self, limit: int = 8) -> list[Match]:
        bounded = min(max(limit, 1), 10)
        return await self._orchestrator.just_finished(bounded)

    async def team_context(self) -> TeamContext | None:
        return await self._orchestrator.team_context()
