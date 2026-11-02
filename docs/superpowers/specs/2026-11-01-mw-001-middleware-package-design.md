# MW-001 Middleware package design

GitHub issue [#1](https://github.com/javakishore-veleti/NorthStar-AI-Harness-eCommerce-Analytics/issues/1). Structure is [ARCHITECTURE.md](../../../ARCHITECTURE.md). Behavior of the two process endpoints is [DESIGN.md](../../../DESIGN.md).

## Classification

This is a new process. The repository has no FastAPI app and no `Middleware/` tree. The issue, ARCHITECTURE.md, and DESIGN.md already fix the folder names, the import name, the mount path, the port, and the health rule. This spec records the decisions used to implement that slice and nothing past it.

## Goal

`Middleware/north-start-ecomm-mcp` is its own uv project. Importing `north_start_ecomm_mcp` and running the console script starts a localhost FastAPI process. `GET /health` returns success and does not call a domain. FastMCP is mounted at `/mcp`, and FastAPI uses that MCP app's lifespan. The process starts with no domain package.

## Approaches

1. **Separate uv project under `Middleware/north-start-ecomm-mcp`.** Matches the issue and ARCHITECTURE.md. The root project keeps `deepagents` for a later harness. Recommended.
2. **Add FastAPI to the root `pyproject.toml`.** Mixes the harness dependency with the middleware process. Rejected.
3. **Register `customer_brief`, `issue_lookup`, `revenue_summary`, and `send_proposal` on this mount.** Those tools need domain packages. The acceptance criteria say the process starts without a domain package. Rejected for this issue. DESIGN.md names those tools as the later contract of `/mcp`. This issue only mounts the server.

## Decisions

- Project path: `Middleware/north-start-ecomm-mcp/`.
- Import package: `north_start_ecomm_mcp`.
- Python: `>=3.13`, matching the repository `.python-version`.
- Runtime dependencies: `fastapi`, `uvicorn`, `fastmcp`. No `deepagents`.
- Dev dependency: `httpx`, required by Starlette's `TestClient`.
- Console script: `northstar-mcp` calls `north_start_ecomm_mcp.app.main:main`.
- Bind host: `127.0.0.1`.
- Port: `NORTHSTAR_MCP_PORT`, default `8080`. A non-integer or an out-of-range value raises `ValueError` before the socket opens.
- Composition root: `north_start_ecomm_mcp/app/main.py`. `create_app()` builds the FastAPI app. The module exposes `app` for uvicorn.
- MCP module: `north_start_ecomm_mcp/app/mcp_server.py`. `build_mcp_app()` returns `FastMCP("north-start-ecomm-mcp").http_app(path="/")`.
- Mount: `app.mount("/mcp", mcp_app)` and `FastAPI(lifespan=mcp_app.lifespan)`. Path `"/"` on the MCP app plus mount `"/mcp"` exposes MCP at `/mcp`, not `/mcp/mcp`.
- Health: `GET /health` returns HTTP 200 and `{"status": "ok"}`. The handler does not import or call a domain.
- No tools are registered. No `domains/` tree. No `common/`. No `http_role.py`. Those belong to later issues.
- `.runtime/` is gitignored inside the middleware project so a later company database is not committed.

## Files

- Create: `Middleware/north-start-ecomm-mcp/pyproject.toml`
- Create: `Middleware/north-start-ecomm-mcp/.python-version`
- Create: `Middleware/north-start-ecomm-mcp/.gitignore`
- Create: `Middleware/north-start-ecomm-mcp/north_start_ecomm_mcp/__init__.py`
- Create: `Middleware/north-start-ecomm-mcp/north_start_ecomm_mcp/app/__init__.py`
- Create: `Middleware/north-start-ecomm-mcp/north_start_ecomm_mcp/app/main.py`
- Create: `Middleware/north-start-ecomm-mcp/north_start_ecomm_mcp/app/mcp_server.py`
- Create: `Middleware/north-start-ecomm-mcp/tests/test_mw001.py`
- Create: `Middleware/north-start-ecomm-mcp/uv.lock` after `uv lock`

The root `pyproject.toml` and `main.py` stay as they are.

## Error handling

- Absent `NORTHSTAR_MCP_PORT` selects `8080`.
- `NORTHSTAR_MCP_PORT` that is not an integer, or is outside `1..65535`, raises `ValueError` with the invalid value in the message.
- `/health` has no domain failure path. If the process is not up, the client fails to connect.
- An MCP request that is not a streamable HTTP call may return a non-success status. It must not be `404`.

## Tests

From `Middleware/north-start-ecomm-mcp`:

```bash
uv run python -m unittest discover -s tests -v
```

- Importing `north_start_ecomm_mcp` succeeds, and the app directory name is `north-start-ecomm-mcp`.
- `GET /health` through `TestClient` returns 200 and `{"status": "ok"}`.
- The FastAPI app has a mount at `/mcp`, and its lifespan is the MCP app lifespan.
- A request to `/mcp` is not `404`.
- Package sources do not import `domains`, `deepagents`, or `common.database`.
- `domains/` does not exist.
- `listen_port()` is `8080` when the variable is unset, and it reads a set value.
- `pyproject.toml` defines the script `northstar-mcp`.

Evidence, after the unit tests pass: start `northstar-mcp` on a free port, request `GET /health`, record the status and body, then stop the process.

## Out of scope

Singleton metaclass and the import audit scaffold (MW-002). Company SQLite seed (MW-003). Domain slices, role header binding, and the four MCP tools. Any call to a paid model. Email. Changes to `company/AGENTS.md` or the truncated skill files.
