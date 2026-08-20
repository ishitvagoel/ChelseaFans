import pytest
from fastapi.testclient import TestClient

from app.composition import build_container
from app.main import app
from app.settings import Settings


def test_health_reports_demo() -> None:
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["demo"] is True
    assert isinstance(body["persistence"], bool)


def test_meta_demo_flag() -> None:
    with TestClient(app) as client:
        response = client.get("/v1/meta")
    assert response.status_code == 200
    body = response.json()
    assert body["demo"] is True
    assert "USE_DEMO_DATA" in body["message"]


@pytest.mark.asyncio
async def test_live_flag_does_not_register_api_football_without_key() -> None:
    settings = Settings(
        use_demo_data=False,
        football_data_api_key="",
        api_football_key="",
        database_url="",
    )
    container = await build_container(settings)
    assert container.demo is False
    assert [p.name for p in container.registry.season_stats] == []
    assert [p.name for p in container.registry.player_match_stats] == []


@pytest.mark.asyncio
async def test_demo_flag_registers_only_demo_provider() -> None:
    settings = Settings(use_demo_data=True, football_data_api_key="unused")
    container = await build_container(settings)
    assert container.demo is True
    assert [p.name for p in container.registry.fixtures] == ["demo"]
    assert [p.name for p in container.registry.season_stats] == ["demo"]
    assert container.http_clients == []
