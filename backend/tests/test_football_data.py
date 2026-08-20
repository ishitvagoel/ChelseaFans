from datetime import UTC, datetime, timedelta

from app.infrastructure.providers.football_data import finished_match_query_params


def test_finished_match_query_uses_lookback_window() -> None:
    params = finished_match_query_params()
    assert params["status"] == "FINISHED"
    start = datetime.strptime(params["dateFrom"], "%Y-%m-%d").date()
    end = datetime.strptime(params["dateTo"], "%Y-%m-%d").date()
    today = datetime.now(UTC).date()
    assert end == today
    assert timedelta(days=399) <= (end - start) <= timedelta(days=401)
    assert "limit" not in params
