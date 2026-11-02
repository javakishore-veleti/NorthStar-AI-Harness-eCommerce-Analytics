"""Task conversation checkpoints. A different file from the company database."""

from __future__ import annotations

import shutil
import sqlite3
from pathlib import Path

from workspace import task_work_dir


class TaskCheckpoint:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = Path(repo_root)
        self.path = self.repo_root / ".runtime" / "harness-checkpoints.sqlite"

    def append(self, task_id: str, body: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO turns (task_id, body) VALUES (?, ?)",
                (task_id, body),
            )

    def turns(self, task_id: str) -> list[str]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT body FROM turns WHERE task_id = ? ORDER BY id",
                (task_id,),
            ).fetchall()
        return [row[0] for row in rows]

    def delete_task(self, task_id: str) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM turns WHERE task_id = ?", (task_id,))
        workspace = task_work_dir(self.repo_root, task_id).parent
        if workspace.exists():
            shutil.rmtree(workspace)

    def _connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.path)
        conn.execute(
            "CREATE TABLE IF NOT EXISTS turns ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, task_id TEXT, body TEXT)"
        )
        return conn
