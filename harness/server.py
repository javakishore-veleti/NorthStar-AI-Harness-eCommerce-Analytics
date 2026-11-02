"""Localhost employee interface. Separate from the middleware process."""

from __future__ import annotations

import html
import os
from pathlib import Path
from uuid import uuid4

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.routing import Route

from approval import SendApproval
from checkpoint import TaskCheckpoint
from mcp_client import CompanyMcpClient
from workspace import task_work_dir

HOST = "127.0.0.1"
DEFAULT_PORT = 8090
ROLES = ("sales", "engineering", "finance")
_PAGE = Path(__file__).with_name("web") / "index.html"


def listen_port() -> int:
    raw = os.environ.get("NORTHSTAR_UI_PORT", str(DEFAULT_PORT))
    port = int(raw)
    if not 1 <= port <= 65535:
        raise ValueError(f"NORTHSTAR_UI_PORT must be between 1 and 65535, got {port}")
    return port


class EmployeeInterface:
    def __init__(self, repo_root: Path, mcp_url: str = "http://127.0.0.1:8080/mcp") -> None:
        self.repo_root = Path(repo_root)
        self.mcp_url = mcp_url
        self.checkpoint = TaskCheckpoint(self.repo_root)
        self.roles: dict[str, str] = {}
        self.notices: dict[str, str] = {}

    def role_for(self, task_id: str) -> str:
        return self.roles.get(task_id, "sales")

    def header_for(self, task_id: str) -> dict[str, str]:
        return {"X-Employee-Role": self.role_for(task_id)}

    def render(self, task_id: str) -> str:
        role = self.role_for(task_id)
        history = "".join(
            f"<li>{html.escape(turn)}</li>" for turn in self.checkpoint.turns(task_id)
        ) or "<li>No messages yet.</li>"
        work = task_work_dir(self.repo_root, task_id)
        names = sorted(path.name for path in work.glob("*")) if work.exists() else []
        artifacts = "".join(f"<li>{html.escape(name)}</li>" for name in names) or "<li>No saved files.</li>"
        page = _PAGE.read_text(encoding="utf-8")
        selected = {item: ("selected" if item == role else "") for item in ROLES}
        return (
            page.replace("{{task_id}}", html.escape(task_id))
            .replace("{{role_header}}", html.escape(self.header_for(task_id)["X-Employee-Role"]))
            .replace("{{sales_selected}}", selected["sales"])
            .replace("{{engineering_selected}}", selected["engineering"])
            .replace("{{finance_selected}}", selected["finance"])
            .replace("{{history}}", history)
            .replace("{{artifacts}}", artifacts)
            .replace("{{notice}}", html.escape(self.notices.get(task_id, "")))
        )

    async def home(self, request: Request) -> RedirectResponse:
        task_id = uuid4().hex[:8]
        self.roles[task_id] = "sales"
        return RedirectResponse(f"/tasks/{task_id}", status_code=303)

    async def show(self, request: Request) -> HTMLResponse:
        task_id = request.path_params["task_id"]
        self.roles.setdefault(task_id, "sales")
        return HTMLResponse(self.render(task_id))

    async def message(self, request: Request) -> RedirectResponse:
        task_id = request.path_params["task_id"]
        form = await request.form()
        role = str(form.get("role") or "sales")
        if role not in ROLES:
            role = "sales"
        self.roles[task_id] = role
        text = str(form.get("message") or "").strip()
        if text:
            self.checkpoint.append(task_id, f"{role}: {text}")
        return RedirectResponse(f"/tasks/{task_id}", status_code=303)

    async def decision(self, request: Request) -> RedirectResponse:
        task_id = request.path_params["task_id"]
        form = await request.form()
        choice = str(form.get("decision") or "reject")
        customer = str(form.get("customer") or "")
        body = str(form.get("body") or "")
        client = CompanyMcpClient(self.mcp_url, self.role_for(task_id))
        result = SendApproval(client).decide(choice, customer, body)
        if choice == "reject":
            self.notices[task_id] = "Rejected. The outbox was not changed."
        else:
            self.notices[task_id] = f"Approved with header {client.server_config()['mcpServers']['northstar']['headers']['X-Employee-Role']}."
            self.checkpoint.append(task_id, f"decision: {choice} {result}")
        return RedirectResponse(f"/tasks/{task_id}", status_code=303)


def create_interface(repo_root: Path, mcp_url: str = "http://127.0.0.1:8080/mcp") -> Starlette:
    ui = EmployeeInterface(repo_root, mcp_url)
    return Starlette(
        routes=[
            Route("/", ui.home),
            Route("/tasks/{task_id}", ui.show),
            Route("/tasks/{task_id}/message", ui.message, methods=["POST"]),
            Route("/tasks/{task_id}/decision", ui.decision, methods=["POST"]),
        ]
    )


def main() -> None:
    import uvicorn

    repo = Path(os.environ.get("NORTHSTAR_REPO_ROOT", Path(__file__).resolve().parents[1]))
    uvicorn.run(create_interface(repo), host=HOST, port=listen_port())
