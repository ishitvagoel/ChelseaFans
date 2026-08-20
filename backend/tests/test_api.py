from fastapi.testclient import TestClient

from app.main import app


def test_health() -> None:
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "persistence" in response.json()


def test_just_finished_demo() -> None:
    with TestClient(app) as client:
        response = client.get("/v1/chelsea/just-finished?limit=5")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 5
    first = payload[0]
    assert first["score"] is not None
    assert first["player_stats"]
    assert first["sources"]


def test_compare_demo_players() -> None:
    with TestClient(app) as client:
        response = client.get(
            "/v1/compare",
            params={
                "player_ids": "demo-palmer,demo-jackson",
                "season_from": "2024/25",
                "season_to": "2024/25",
            },
        )
    assert response.status_code == 200
    body = response.json()
    assert len(body["players"]) == 2
    palmer = body["players"][0]
    assert palmer["season"]["goals"] == 15
    assert palmer["career"]["goals"] == 37


def test_search_and_context() -> None:
    with TestClient(app) as client:
        search = client.get("/v1/players/search", params={"q": "Palmer"})
        ctx = client.get("/v1/chelsea/context")
    assert search.status_code == 200
    assert any("Palmer" in p["name"] for p in search.json())
    assert ctx.status_code == 200
    assert ctx.json()["team_name"] == "Chelsea"
