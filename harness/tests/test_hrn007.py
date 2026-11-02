import sqlite3
import tempfile
import unittest
from pathlib import Path


class CheckpointTests(unittest.TestCase):
    def test_reopen_sees_the_earlier_turn_without_rolling_back_files(self) -> None:
        from checkpoint import TaskCheckpoint
        from workspace import save_work_file

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            company_db = root / "company.db"
            with sqlite3.connect(company_db) as conn:
                conn.execute("CREATE TABLE outbox (id TEXT PRIMARY KEY)")
                conn.execute("INSERT INTO outbox (id) VALUES ('keep')")
            store = TaskCheckpoint(root)
            self.assertNotEqual(store.path.resolve(), company_db.resolve())
            store.append("task-9", "first turn")
            saved = save_work_file(root, "task-9", "proposal.md", "draft")
            store.append("task-9", "follow up")
            self.assertEqual(store.turns("task-9"), ["first turn", "follow up"])
            self.assertEqual(saved.read_text(encoding="utf-8"), "draft")
            with sqlite3.connect(company_db) as conn:
                self.assertEqual(conn.execute("SELECT COUNT(*) FROM outbox").fetchone()[0], 1)
            store.delete_task("task-9")
            self.assertEqual(store.turns("task-9"), [])
            self.assertFalse(saved.exists())
            with sqlite3.connect(company_db) as conn:
                self.assertEqual(conn.execute("SELECT COUNT(*) FROM outbox").fetchone()[0], 1)
