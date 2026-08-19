from app.application.comparison_engine import compare_players, in_range
from app.domain.models import Player, SeasonTotals


def test_in_range_bounds() -> None:
    assert in_range("2023/24", "2023/24", "2024/25")
    assert not in_range("2022/23", "2023/24", None)


def test_compare_sums_season_not_career() -> None:
    player = Player(id="p1", name="Test")
    totals = [
        SeasonTotals(player=player, season="2023/24", competition="PL", goals=22, assists=11, minutes=2600, rating=7.8, source="demo"),
        SeasonTotals(player=player, season="2024/25", competition="PL", goals=15, assists=10, minutes=3100, rating=7.6, source="demo"),
    ]
    result = compare_players(
        player=player, all_totals=totals, season_from="2024/25", season_to="2024/25"
    )
    assert result.season.goals == 15
    assert result.career.goals == 37
    assert result.season.rating == 7.6
    assert result.career.rating == 7.7
