# MW-001 Middleware Package Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Create the `north-start-ecomm-mcp` uv project so localhost `GET /health` succeeds and FastMCP is mounted at `/mcp` with no domain package.

**Architecture:** A separate project under `Middleware/north-start-ecomm-mcp` owns the FastAPI composition root. `create_app()` mounts `FastMCP.http_app(path="/")` at `/mcp` and passes that app's lifespan to FastAPI. Health is a route on the composition root and does not import a domain.

**Tech Stack:** Python 3.13, uv, FastAPI, uvicorn, FastMCP, unittest, Starlette TestClient.

**Spec:** `docs/superpowers/specs/2026-11-01-mw-001-middleware-package-design.md`

## Global Constraints

- Project path: `Middleware/north-start-ecomm-mcp/`.
- Import package: `north_start_ecomm_mcp`.
- Python: `>=3.13`.
- Runtime dependencies: `fastapi`, `uvicorn`, `fastmcp`. No `deepagents`.
- Dev dependency: `httpx`.
- Console script: `northstar-mcp` calls `north_start_ecomm_mcp.app.main:main`.
- Bind host: `127.0.0.1`.
- Port: `NORTHSTAR_MCP_PORT`, default `8080`. A non-integer or an out-of-range value raises `ValueError` before the socket opens.
- MCP server name: `north-start-ecomm-mcp`. MCP app path is `"/"` and the FastAPI mount is `"/mcp"`.
- `GET /health` returns HTTP 200 and `{"status": "ok"}`.
- No tools, no `domains/`, no `common/`, no `http_role.py`.
- `.runtime/` is gitignored inside the middleware project.
- The root `pyproject.toml` and `main.py` stay unchanged.
- Do not call a paid model or send email.

---

### Task 1: Project skeleton and port

**Files:**
- Create: `Middleware/north-start-ecomm-mcp/pyproject.toml`
- Create: `Middleware/north-start-ecomm-mcp/.python-version`
- Create: `Middleware/north-start-ecomm-mcp/.gitignore`
- Create: `Middleware/north-start-ecomm-mcp/north_start_ecomm_mcp/__init__.py`
- Create: `Middleware/north-start-ecomm-mcp/north_start_ecomm_mcp/app/__init__.py`
- Create: `Middleware/north-start-ecomm-mcp/north_start_ecomm_mcp/app/main.py`
- Create: `Middleware/north-start-ecomm-mcp/tests/test_mw001.py`
- Create: `Middleware/north-start-ecomm-mcp/uv.lock`

**Interfaces:**
- Consumes: nothing
- Produces: `listen_port() -> int`, `HOST = "127.0.0.1"`, console script name `northstar-mcp`

- [x] **Step 1: Write the failing test**

```python
import os
import tomllib
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]


class PackageTests(unittest.TestCase):
    def test_directory_and_import_names(self) -> None:
        self.assertEqual(PROJECT.name, "north-start-ecomm-mcp")
        self.assertTrue((PROJECT / "north_start_ecomm_mcp").is_dir())

    def test_console_script(self) -> None:
        with (PROJECT / "pyproject.toml").open("rb") as handle:
            project = tomllib.load(handle)["project"]
        self.assertEqual(
            project["scripts"]["northstar-mcp"],
            "north_start_ecomm_mcp.app.main:main",
        )
        self.assertNotIn("deepagents", project["dependencies"])

    def test_listen_port_default_and_override(self) -> None:
        from north_start_ecomm_mcp.app.main import HOST, listen_port

        self.assertEqual(HOST, "127.0.0.1")
        env = os.environ
        previous = env.pop("NORTHSTAR_MCP_PORT", None)
        try:
            self.assertEqual(listen_port(), 8080)
            env["NORTHSTAR_MCP_PORT"] = "9091"
            self.assertEqual(listen_port(), 9091)
            env["NORTHSTAR_MCP_PORT"] = "nope"
            with self.assertRaises(ValueError):
                listen_port()
        finally:
            if previous is None:
                env.pop("NORTHSTAR_MCP_PORT", None)
            else:
                env["NORTHSTAR_MCP_PORT"] = previous
```

- [x] **Step 2: Run test to verify it fails**

Run from `Middleware/north-start-ecomm-mcp`:

```bash
uv run python -m unittest tests.test_mw001.PackageTests -v
```

Expected: FAIL because the project files and `listen_port` do not exist yet. `uv run` from a missing project fails first; create the project metadata in step 3, then re-run until the failure is `listen_port` or a missing module, then finish the function.

- [x] **Step 3: Write minimal implementation**

`pyproject.toml`:

```toml
[project]
name = "north-start-ecomm-mcp"
version = "0.1.0"
description = "NorthStar company middleware process."
requires-python = ">=3.13"
dependencies = [
    "fastapi",
    "fastmcp",
    "uvicorn",
]

[project.scripts]
northstar-mcp = "north_start_ecomm_mcp.app.main:main"

[dependency-groups]
dev = ["httpx"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["north_start_ecomm_mcp"]
```

`.python-version` contains `3.13`. `.gitignore` contains `.venv/` and `.runtime/`. Package `__init__.py` files are empty.

`north_start_ecomm_mcp/app/main.py`:

```python
from __future__ import annotations

import os

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
```

Then, from `Middleware/north-start-ecomm-mcp`:

```bash
uv lock
```

- [x] **Step 4: Run test to verify it passes**

```bash
uv run python -m unittest tests.test_mw001.PackageTests -v
```

Expected: PASS, 3 tests.

- [x] **Step 5: Commit**

```bash
git add Middleware/north-start-ecomm-mcp docs/superpowers/plans/2026-11-01-mw-001-middleware-package.md
git commit -m "Add the middleware project skeleton and listen port."
```

### Task 2: Health route

**Files:**
- Modify: `Middleware/north-start-ecomm-mcp/north_start_ecomm_mcp/app/main.py`
- Modify: `Middleware/north-start-ecomm-mcp/tests/test_mw001.py`

**Interfaces:**
- Consumes: `listen_port`
- Produces: `create_app() -> FastAPI`, module attribute `app`, `GET /health` body `{"status": "ok"}`

- [x] **Step 1: Write the failing test**

```python
class HealthTests(unittest.TestCase):
    def test_health_returns_ok(self) -> None:
        from fastapi.testclient import TestClient
        from north_start_ecomm_mcp.app.main import create_app

        with TestClient(create_app()) as client:
            response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
```

- [x] **Step 2: Run test to verify it fails**

```bash
uv run python -m unittest tests.test_mw001.HealthTests -v
```

Expected: FAIL with `ImportError` for `create_app`.

- [x] **Step 3: Write minimal implementation**

Add to `main.py`:

```python
from fastapi import FastAPI


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
```

- [x] **Step 4: Run test to verify it passes**

```bash
uv run python -m unittest tests.test_mw001.HealthTests tests.test_mw001.PackageTests -v
```

Expected: PASS.

- [x] **Step 5: Commit**

```bash
git add Middleware/north-start-ecomm-mcp/north_start_ecomm_mcp/app/main.py Middleware/north-start-ecomm-mcp/tests/test_mw001.py
git commit -m "Serve GET /health from the middleware composition root."
```

### Task 3: FastMCP mount and closed imports

**Files:**
- Create: `Middleware/north-start-ecomm-mcp/north_start_ecomm_mcp/app/mcp_server.py`
- Modify: `Middleware/north-start-ecomm-mcp/north_start_ecomm_mcp/app/main.py`
- Modify: `Middleware/north-start-ecomm-mcp/tests/test_mw001.py`

**Interfaces:**
- Consumes: `create_app`
- Produces: `build_mcp_app() -> Starlette`, mount path `/mcp`, FastAPI lifespan equal to `mcp_app.lifespan`

- [x] **Step 1: Write the failing test**

```python
import ast


class MountTests(unittest.TestCase):
    def test_mcp_is_mounted_with_its_lifespan(self) -> None:
        from starlette.routing import Mount
        from north_start_ecomm_mcp.app.main import create_app

        app = create_app()
        mounts = [route for route in app.routes if isinstance(route, Mount)]
        mcp_mounts = [route for route in mounts if route.path == "/mcp"]
        self.assertEqual(len(mcp_mounts), 1)
        self.assertIs(app.router.lifespan_context, mcp_mounts[0].app.lifespan)

    def test_mcp_route_is_not_missing(self) -> None:
        from fastapi.testclient import TestClient
        from north_start_ecomm_mcp.app.main import create_app

        with TestClient(create_app()) as client:
            response = client.get("/mcp")
        self.assertNotEqual(response.status_code, 404)
        self.assertNotIn("not initialized", response.text.lower())

    def test_sources_do_not_import_a_domain(self) -> None:
        package = PROJECT / "north_start_ecomm_mcp"
        self.assertFalse((package / "domains").exists())
        forbidden = ("domains", "deepagents", "common.database")
        for path in package.rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    names = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom):
                    names = [node.module or ""]
                else:
                    continue
                for name in names:
                    for item in forbidden:
                        self.assertFalse(
                            name == item or name.startswith(item + "."),
                            f"{path} imports {name}",
                        )
```

- [x] **Step 2: Run test to verify it fails**

```bash
uv run python -m unittest tests.test_mw001.MountTests -v
```

Expected: FAIL because `/mcp` is not mounted.

- [x] **Step 3: Write minimal implementation**

`mcp_server.py`:

```python
from __future__ import annotations

from fastmcp import FastMCP
from starlette.applications import Starlette


def build_mcp_server() -> FastMCP:
    return FastMCP("north-start-ecomm-mcp")


def build_mcp_app() -> Starlette:
    return build_mcp_server().http_app(path="/")
```

Replace `create_app` in `main.py`:

```python
from north_start_ecomm_mcp.app.mcp_server import build_mcp_app


def create_app() -> FastAPI:
    mcp_app = build_mcp_app()
    app = FastAPI(lifespan=mcp_app.lifespan)
    app.mount("/mcp", mcp_app)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app
```

- [x] **Step 4: Run test to verify it passes**

```bash
uv run python -m unittest discover -s tests -v
```

Expected: PASS. If `lifespan_context` is not the same object as `mcp_app.lifespan`, stop and fix the composition root so FastAPI receives that lifespan object. Do not weaken the test to a name check.

- [x] **Step 5: Commit**

```bash
git add Middleware/north-start-ecomm-mcp/north_start_ecomm_mcp Middleware/north-start-ecomm-mcp/tests/test_mw001.py
git commit -m "Mount FastMCP at /mcp without a domain package."
```

### Task 4: Live health evidence

**Files:**
- Modify: `docs/superpowers/plans/2026-11-01-mw-001-middleware-package.md` checkboxes only if this task's command output is recorded in the issue comment, not in this file.

**Interfaces:**
- Consumes: `northstar-mcp`, `GET /health`

- [x] **Step 1: Start the process on a free port**

From `Middleware/north-start-ecomm-mcp`:

```bash
NORTHSTAR_MCP_PORT=8765 uv run northstar-mcp
```

Expected log: uvicorn listening on `127.0.0.1:8765`.

- [x] **Step 2: Request health**

```bash
curl -sS -D - http://127.0.0.1:8765/health
```

Expected: HTTP 200 and `{"status":"ok"}`.

- [x] **Step 3: Stop the process**

Stop the uvicorn process. Do not leave it running. Do not commit `.runtime/` or `.venv`.
