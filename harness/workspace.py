"""Per-task working files. This is not the company database."""

from __future__ import annotations

from pathlib import Path

PROPOSAL_DRAFT = "proposal.md"


def task_work_dir(repo_root: Path, task_id: str) -> Path:
    if not task_id or task_id in {".", ".."} or "/" in task_id or "\\" in task_id:
        raise ValueError(f"Invalid task id: {task_id!r}")
    return (Path(repo_root) / ".runtime" / "workspace" / task_id / "work").resolve()


def save_work_file(repo_root: Path, task_id: str, name: str, content: str) -> Path:
    """Map a /work/<name> draft onto the task workspace."""
    if not name or name != Path(name).name or name.startswith("."):
        raise ValueError(f"Invalid work file name: {name!r}")
    path = task_work_dir(repo_root, task_id) / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def company_db_is_outside_workspace(repo_root: Path, task_id: str, company_db: Path) -> bool:
    work = task_work_dir(repo_root, task_id)
    try:
        Path(company_db).resolve().relative_to(work)
    except ValueError:
        return True
    return False
