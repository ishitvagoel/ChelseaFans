from __future__ import annotations

import re
from datetime import UTC, datetime

# API-Football free tier season window (see /status and plan errors in responses).
API_FOOTBALL_FREE_SEASONS = frozenset(range(2022, 2025))


def season_start_year(kickoff: datetime) -> int:
    return kickoff.year if kickoff.month >= 7 else kickoff.year - 1


def normalize_club_name(name: str) -> str:
    lowered = name.lower()
    lowered = re.sub(r"\b(fc|afc|cf|sc)\b", "", lowered)
    lowered = re.sub(r"[^a-z0-9]+", " ", lowered)
    return " ".join(lowered.split())


def club_names_match(left: str, right: str) -> bool:
    a = normalize_club_name(left)
    b = normalize_club_name(right)
    if not a or not b:
        return False
    return a == b or a in b or b in a


def season_accessible_on_free_tier(kickoff: datetime) -> bool:
    return season_start_year(kickoff) in API_FOOTBALL_FREE_SEASONS


def accessible_seasons_descending(*, now: datetime | None = None) -> list[int]:
    current = season_start_year(now or datetime.now(UTC))
    seasons = [year for year in sorted(API_FOOTBALL_FREE_SEASONS, reverse=True) if year <= current]
    return seasons or sorted(API_FOOTBALL_FREE_SEASONS, reverse=True)
