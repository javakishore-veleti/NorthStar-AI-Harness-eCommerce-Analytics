from __future__ import annotations

import os

from fastapi import FastAPI

from north_start_ecomm_mcp.app.mcp_server import build_mcp_app
from north_start_ecomm_mcp.domains.customer.api.customer_brief import (
    router as customer_brief_router,
)
from north_start_ecomm_mcp.domains.issues.api.issue_lookup import (
    router as issue_lookup_router,
)
from north_start_ecomm_mcp.domains.financials.api.revenue_summary import (
    router as revenue_summary_router,
)
from north_start_ecomm_mcp.domains.proposals.api.send_proposal import (
    router as send_proposal_router,
)

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
    mcp_app = build_mcp_app()
    app = FastAPI(lifespan=mcp_app.lifespan)
    app.mount("/mcp", mcp_app)
    app.include_router(customer_brief_router)
    app.include_router(issue_lookup_router)
    app.include_router(revenue_summary_router)
    app.include_router(send_proposal_router)
    # include_router wraps the lifespan. The process must keep the MCP lifespan
    # itself so /mcp sessions initialize, as ARCHITECTURE.md requires.
    app.router.lifespan_context = mcp_app.lifespan

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()


def main() -> None:
    import uvicorn

    uvicorn.run(app, host=HOST, port=listen_port())
