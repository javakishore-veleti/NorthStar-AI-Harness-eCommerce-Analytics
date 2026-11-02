import sqlite3
import tempfile
import unittest
from pathlib import Path


class WorkspaceTests(unittest.TestCase):
    def test_saved_proposal_is_readable_and_leaves_the_outbox_empty(self) -> None:
        from workspace import company_db_is_outside_workspace, save_work_file

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            company_db = root / "company.db"
            with sqlite3.connect(company_db) as conn:
                conn.execute("CREATE TABLE outbox (id TEXT PRIMARY KEY, customer TEXT, body TEXT)")
            path = save_work_file(root, "task-9", "proposal.md", "Customer goal: unify reporting\n")
            self.assertEqual(path.name, "proposal.md")
            self.assertIn(".runtime/workspace/task-9/work", path.as_posix())
            self.assertEqual(path.read_text(encoding="utf-8"), "Customer goal: unify reporting\n")
            self.assertTrue(company_db_is_outside_workspace(root, "task-9", company_db))
            with sqlite3.connect(company_db) as conn:
                count = conn.execute("SELECT COUNT(*) FROM outbox").fetchone()[0]
            self.assertEqual(count, 0)
            self.assertFalse(str(company_db.resolve()).startswith(str(path.parent.resolve())))
