from __future__ import annotations

import os

from fastapi import FastAPI

HOST = "127.0.0.1"
DEFAULT_PORT = 8080


def listen_port() -> int:
    raw = os.environ.get("NORTHSTAR_MCP_PORT", str(DEFAULT_PORT))
    try:
        port = int(raw)
    except ValueError as exc:
        raise ValueError(
            f"NORTHSTAR_MCP_PORT must be an integer, got {raw!r}"
        ) from exc
    if not 1 <= port <= 65535:
        raise ValueError(
            f"NORTHSTAR_MCP_PORT must be between 1 and 65535, got {port}"
        )
    return port


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()


def main() -> None:
    import uvicorn

    uvicorn.run(app, host=HOST, port=listen_port())
