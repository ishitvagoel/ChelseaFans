"""Provider registry — Open/Closed extension point. Register adapters; do not fork orchestrators."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.interfaces import (
    IFixtureProvider,
    IHistoricalEventProvider,
    IPlayerMatchStatsProvider,
    ISeasonStatsProvider,
    ITeamContextProvider,
)


@dataclass
class ProviderRegistry:
    fixtures: list[IFixtureProvider] = field(default_factory=list)
    player_match_stats: list[IPlayerMatchStatsProvider] = field(default_factory=list)
    season_stats: list[ISeasonStatsProvider] = field(default_factory=list)
    historical_events: list[IHistoricalEventProvider] = field(default_factory=list)
    team_context: list[ITeamContextProvider] = field(default_factory=list)

    def register_fixtures(self, provider: IFixtureProvider) -> None:
        self.fixtures.append(provider)

    def register_player_match_stats(self, provider: IPlayerMatchStatsProvider) -> None:
        self.player_match_stats.append(provider)

    def register_season_stats(self, provider: ISeasonStatsProvider) -> None:
        self.season_stats.append(provider)

    def register_historical_events(self, provider: IHistoricalEventProvider) -> None:
        self.historical_events.append(provider)

    def register_team_context(self, provider: ITeamContextProvider) -> None:
        self.team_context.append(provider)
