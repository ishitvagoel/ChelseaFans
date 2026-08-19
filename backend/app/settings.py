from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    football_data_api_key: str = ""
    api_football_key: str = ""
    api_football_base_url: str = "https://v3.football.api-sports.io"
    database_url: str = "sqlite+aiosqlite:///./chelsea.db"
    upstash_redis_rest_url: str = ""
    upstash_redis_rest_token: str = ""
    redis_url: str = ""
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    chelsea_football_data_team_id: int = 61
    chelsea_api_football_team_id: int = 49
    use_demo_data: bool = True

    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]
