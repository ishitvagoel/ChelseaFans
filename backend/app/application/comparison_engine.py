from __future__ import annotations

from app.domain.models import MetricSlice, Player, PlayerComparison, SeasonTotals


def _sum_int(values: list[int | None]) -> float | None:
    present = [v for v in values if v is not None]
    if not present:
        return None
    return float(sum(present))


def _avg(values: list[float | None | int]) -> float | None:
    present = [float(v) for v in values if v is not None]
    if not present:
        return None
    return round(sum(present) / len(present), 2)


def totals_to_slice(label: str, rows: list[SeasonTotals]) -> MetricSlice:
    return MetricSlice(
        label=label,
        goals=_sum_int([r.goals for r in rows]),
        assists=_sum_int([r.assists for r in rows]),
        minutes=_sum_int([r.minutes for r in rows]),
        rating=_avg([r.rating for r in rows]),
        progressive_passes=_sum_int([r.progressive_passes for r in rows]),
        progressive_carries=_sum_int([r.progressive_carries for r in rows]),
    )


def _season_sort_key(season: str) -> int:
    try:
        return int(season.split("/")[0])
    except (ValueError, IndexError, AttributeError):
        return 0


def in_range(season: str, season_from: str | None, season_to: str | None) -> bool:
    key = _season_sort_key(season)
    if season_from and key < _season_sort_key(season_from):
        return False
    if season_to and key > _season_sort_key(season_to):
        return False
    return True


def compare_players(
    *,
    player: Player,
    all_totals: list[SeasonTotals],
    season_from: str | None,
    season_to: str | None,
) -> PlayerComparison:
    season_rows = [r for r in all_totals if in_range(r.season, season_from, season_to)]
    notes = tuple(sorted({r.source for r in all_totals if r.source}))
    return PlayerComparison(
        player=player,
        season=totals_to_slice("season", season_rows),
        career=totals_to_slice("career", all_totals),
        source_notes=notes,
    )
