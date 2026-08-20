from __future__ import annotations

from pydantic import TypeAdapter

from app.domain.models import EventType, Match, MatchEvent
from app.infrastructure.http.rate_limit import RateLimitedClient
from app.infrastructure.providers.contracts.statsbomb import StatsBombEventRecord


class StatsBombProvider:
    """Open data enrichment. Coverage is sparse; returns empty rather than inventing events."""

    name = "statsbomb"

    def __init__(self, client: RateLimitedClient) -> None:
        self._client = client

    async def events_for_match(self, match: Match) -> list[MatchEvent]:
        if not match.id.startswith("sb-"):
            return []
        match_id = match.id.removeprefix("sb-")
        url = (
            "https://raw.githubusercontent.com/statsbomb/open-data/master/data/events/"
            f"{match_id}.json"
        )
        response = await self._client.request("GET", url)
        if response.status_code >= 400:
            return []
        adapter = TypeAdapter(list[StatsBombEventRecord])
        records = adapter.validate_python(response.json()[:80])
        events: list[MatchEvent] = []
        for item in records:
            etype = item.type.name if item.type else None
            mapped = _map_event_type(etype)
            if mapped is None:
                continue
            player = item.player.name if item.player else None
            events.append(MatchEvent(item.minute, mapped, player, etype))
        return events[:20]


def _map_event_type(name: str | None) -> EventType | None:
    if not name:
        return None
    lowered = name.lower()
    if lowered == "shot" or lowered == "goal":
        return EventType.GOAL
    if "card" in lowered:
        return EventType.CARD
    if "substitution" in lowered:
        return EventType.SUBSTITUTION
    return None
