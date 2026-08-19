from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.composition import build_container
from app.settings import Settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = Settings()
    container = await build_container(settings)
    app.state.container = container
    yield
    for client in container.http_clients:
        await client.aclose()


def create_app() -> FastAPI:
    settings = Settings()
    app = FastAPI(
        title="Chelsea Stats API",
        version="1.0.0",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
