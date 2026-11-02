import os
import sqlite3
import tempfile
import unittest
from pathlib import Path


class EmployeeInterfaceTests(unittest.TestCase):
    def test_profile_switch_changes_the_role_header_and_reject_skips_the_outbox(self) -> None:
        from starlette.testclient import TestClient

        from server import HOST, create_interface

        self.assertEqual(HOST, "127.0.0.1")
        secret = "sk-test-should-not-appear"
        os.environ["OPENAI_API_KEY"] = secret
        try:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                company_db = root / "company.db"
                with sqlite3.connect(company_db) as conn:
                    conn.execute("CREATE TABLE outbox (id TEXT PRIMARY KEY)")
                with TestClient(create_interface(root)) as client:
                    home = client.get("/", follow_redirects=False)
                    self.assertEqual(home.status_code, 303)
                    task_url = home.headers["location"]
                    self.assertTrue(task_url.startswith("/tasks/"))
                    page = client.get(task_url)
                    self.assertEqual(page.status_code, 200)
                    self.assertIn("sales", page.text)
                    self.assertNotIn(secret, page.text)
                    switched = client.post(
                        task_url + "/message",
                        data={"role": "finance", "message": "What is the quarter total?"},
                        follow_redirects=True,
                    )
                    self.assertIn("finance", switched.text)
                    self.assertIn("What is the quarter total?", switched.text)
                    self.assertNotIn(secret, switched.text)
                    rejected = client.post(
                        task_url + "/decision",
                        data={"decision": "reject", "customer": "Acme", "body": "draft"},
                        follow_redirects=True,
                    )
                    self.assertIn("Rejected. The outbox was not changed.", rejected.text)
                with sqlite3.connect(company_db) as conn:
                    self.assertEqual(conn.execute("SELECT COUNT(*) FROM outbox").fetchone()[0], 0)
        finally:
            os.environ.pop("OPENAI_API_KEY", None)
