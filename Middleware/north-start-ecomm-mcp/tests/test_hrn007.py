import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "harness"))


class CompanySeedTests(unittest.TestCase):
    def setUp(self) -> None:
        from north_start_ecomm_mcp.common.singleton import Singleton

        self.tmp = tempfile.TemporaryDirectory()
        self.previous_db = os.environ.get("NORTHSTAR_COMPANY_DB")
        os.environ["NORTHSTAR_COMPANY_DB"] = str(Path(self.tmp.name) / "company.db")
        Singleton._instances.clear()

    def tearDown(self) -> None:
        from north_start_ecomm_mcp.common.singleton import Singleton

        Singleton._instances.clear()
        if self.previous_db is None:
            os.environ.pop("NORTHSTAR_COMPANY_DB", None)
        else:
            os.environ["NORTHSTAR_COMPANY_DB"] = self.previous_db
        self.tmp.cleanup()

    def test_deleting_a_task_leaves_the_company_seed(self) -> None:
        from checkpoint import TaskCheckpoint
        from north_start_ecomm_mcp.common.database import DatabaseGateway
        from workspace import save_work_file

        gateway = DatabaseGateway()
        root = Path(self.tmp.name)
        save_work_file(root, "task-9", "proposal.md", "draft")
        store = TaskCheckpoint(root)
        store.append("task-9", "turn")
        self.assertNotEqual(store.path.resolve(), Path(os.environ["NORTHSTAR_COMPANY_DB"]).resolve())
        store.delete_task("task-9")
        customers = {row["id"] for row in gateway.read("SELECT id FROM customers")}
        issues = {row["id"] for row in gateway.read("SELECT id FROM issues")}
        self.assertTrue({"C-101", "C-102"} <= customers)
        self.assertIn("INC-42", issues)
