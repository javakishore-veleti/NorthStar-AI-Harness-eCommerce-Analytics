import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


class ReferenceFileTests(unittest.TestCase):
    def test_company_write_is_denied_and_work_write_stays_out_of_company(self) -> None:
        from stages import write_model_file

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            agents = root / "company" / "AGENTS.md"
            agents.parent.mkdir()
            agents.write_text("original", encoding="utf-8")
            with self.assertRaises(PermissionError):
                write_model_file(root, "company/AGENTS.md", "changed")
            self.assertEqual(agents.read_text(encoding="utf-8"), "original")
            skill = root / "skills" / "company" / "write-proposal" / "SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text("procedure", encoding="utf-8")
            with self.assertRaises(PermissionError):
                write_model_file(root, "skills/company/write-proposal/SKILL.md", "changed")
            saved = write_model_file(root, ".runtime/workspace/task-1/work/note.md", "draft")
            self.assertEqual(saved.read_text(encoding="utf-8"), "draft")
            self.assertNotIn("company", saved.resolve().relative_to(root.resolve()).parts)

    def test_todo_list_is_enabled_and_limits_stay_separate(self) -> None:
        from langchain.agents.middleware import ModelCallLimitMiddleware, TodoListMiddleware

        from agent import SilentModel, build_harness
        from config import HarnessConfig
        from stages import PARENT_CALL_LIMIT, REVIEWER_CALL_LIMIT, parent_middleware, reference_permissions

        kinds = [type(item) for item in parent_middleware()]
        self.assertIn(TodoListMiddleware, kinds)
        limits = [item for item in parent_middleware() if isinstance(item, ModelCallLimitMiddleware)]
        self.assertEqual(limits[0].run_limit, PARENT_CALL_LIMIT)
        self.assertEqual(REVIEWER_CALL_LIMIT, 4)
        self.assertNotEqual(PARENT_CALL_LIMIT, REVIEWER_CALL_LIMIT)
        denied = reference_permissions()[0]
        self.assertEqual(denied.mode, "deny")
        self.assertIn("/company/**", denied.paths)
        self.assertIn("/skills/**", denied.paths)
        SilentModel.calls = 0
        self.assertIsNotNone(build_harness(HarnessConfig(REPO, role="sales")))
        self.assertEqual(SilentModel.calls, 0)
