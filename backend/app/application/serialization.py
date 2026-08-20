from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from app.domain.models import (
    ClubRef,
    DataConfidence,
    EventType,
    Match,
    MatchEvent,
    MatchStatus,
    Player,
    PlayerMatchStats,
    Score,
)


def match_to_dict(match: Match) -> dict:
    return {
        "id": match.id,
        "utc_kickoff": match.utc_kickoff.isoformat(),
        "competition": match.competition,
        "home": {
            "name": match.home.name,
            "short_name": match.home.short_name,
            "crest_url": match.home.crest_url,
        },
        "away": {
            "name": match.away.name,
            "short_name": match.away.short_name,
            "crest_url": match.away.crest_url,
        },
        "score": None
        if match.score is None
        else {"home": match.score.home, "away": match.score.away},
        "status": match.status.value,
        "venue": match.venue,
        "matchday": match.matchday,
        "events": [
            {
                "minute": e.minute,
                "event_type": e.event_type.value,
                "player_name": e.player_name,
                "detail": e.detail,
            }
            for e in match.events
        ],
        "player_stats": [_player_stats_to_dict(s) for s in match.player_stats],
        "sources": [
            {"source": c.source, "score": c.score, "coverage_notes": c.coverage_notes}
            for c in match.sources
        ],
    }


def player_stats_to_dict(s: PlayerMatchStats) -> dict:
    return _player_stats_to_dict(s)


def player_stats_from_dict(raw: dict) -> PlayerMatchStats:
    return _player_stats_from_dict(raw)


def _player_stats_to_dict(s: PlayerMatchStats) -> dict:
    return {
        "player": {
            "id": s.player.id,
            "name": s.player.name,
            "position": s.player.position,
            "nationality": s.player.nationality,
            "shirt_number": s.player.shirt_number,
        },
        "minutes": s.minutes,
        "goals": s.goals,
        "assists": s.assists,
        "rating": s.rating,
        "shots": s.shots,
        "key_passes": s.key_passes,
        "progressive_passes": s.progressive_passes,
        "progressive_carries": s.progressive_carries,
        "tackles": s.tackles,
        "source": s.source,
    }


def events_to_dicts(events: Sequence[MatchEvent]) -> list[dict]:
    return [
        {
            "minute": event.minute,
            "event_type": event.event_type.value,
            "player_name": event.player_name,
            "detail": event.detail,
        }
        for event in events
    ]


def events_from_dicts(raw: list) -> list[MatchEvent]:
    return [
        MatchEvent(
            minute=item.get("minute"),
            event_type=EventType(item.get("event_type", "OTHER")),
            player_name=item.get("player_name"),
            detail=item.get("detail"),
        )
        for item in raw
    ]


def match_from_dict(raw: dict) -> Match:
    score = raw.get("score")
    return Match(
        id=raw["id"],
        utc_kickoff=datetime.fromisoformat(raw["utc_kickoff"]),
        competition=raw["competition"],
        home=ClubRef(**{k: raw["home"].get(k) for k in ("name", "short_name", "crest_url")}),
        away=ClubRef(**{k: raw["away"].get(k) for k in ("name", "short_name", "crest_url")}),
        score=None if not score else Score(home=score["home"], away=score["away"]),
        status=MatchStatus(raw.get("status", "FINISHED")),
        events=tuple(
            MatchEvent(
                minute=e.get("minute"),
                event_type=EventType(e.get("event_type", "OTHER")),
                player_name=e.get("player_name"),
                detail=e.get("detail"),
            )
            for e in raw.get("events", [])
        ),
        player_stats=tuple(_player_stats_from_dict(s) for s in raw.get("player_stats", [])),
        venue=raw.get("venue"),
        matchday=raw.get("matchday"),
        sources=tuple(
            DataConfidence(
                source=c["source"],
                score=c["score"],
                coverage_notes=c.get("coverage_notes", ""),
            )
            for c in raw.get("sources", [])
        ),
    )


def _player_stats_from_dict(s: dict) -> PlayerMatchStats:
    p = s["player"]
    return PlayerMatchStats(
        player=Player(
            id=p["id"],
            name=p["name"],
            position=p.get("position"),
            nationality=p.get("nationality"),
            shirt_number=p.get("shirt_number"),
        ),
        minutes=s.get("minutes"),
        goals=s.get("goals"),
        assists=s.get("assists"),
        rating=s.get("rating"),
        shots=s.get("shots"),
        key_passes=s.get("key_passes"),
        progressive_passes=s.get("progressive_passes"),
        progressive_carries=s.get("progressive_carries"),
        tackles=s.get("tackles"),
        source=s.get("source") or "",
    )
