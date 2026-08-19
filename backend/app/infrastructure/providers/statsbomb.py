from __future__ import annotations

from app.domain.models import EventType, Match, MatchEvent
from app.infrastructure.http.rate_limit import RateLimitedClient


class StatsBombProvider:
    """Open data enrichment. Coverage is sparse; returns empty rather than inventing events."""

    name = "statsbomb"

    def __init__(self, client: RateLimitedClient) -> None:
        self._client = client
        self._index: list[dict] | None = None

    async def events_for_match(self, match: Match) -> list[MatchEvent]:
        _ = match
        # Mapping StatsBomb match IDs to live fixtures requires a full index download.
        # Free-tier: only attempt if we already know a statsbomb id (prefix sb-).
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
        events: list[MatchEvent] = []
        for item in response.json()[:80]:
            etype = (item.get("type") or {}).get("name")
            minute = item.get("minute")
            player = (item.get("player") or {}).get("name")
            mapped = _map_event_type(etype)
            if mapped is None:
                continue
            events.append(MatchEvent(minute, mapped, player, etype))
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
