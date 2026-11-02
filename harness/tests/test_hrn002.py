import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


class RoleToolTests(unittest.TestCase):
    def test_each_role_sees_only_its_operations(self) -> None:
        from agent import tools_for_role
        from config import HarnessConfig

        expected = {
            "sales": ["customer_brief", "send_proposal"],
            "engineering": ["customer_brief", "issue_lookup"],
            "finance": ["customer_brief", "revenue_summary"],
        }
        for role, names in expected.items():
            tools = tools_for_role(HarnessConfig(REPO, role=role))
            self.assertEqual([tool.name for tool in tools], names)
            for tool in tools:
                self.assertNotIn("role", tool.args)
        sales = {tool.name for tool in tools_for_role(HarnessConfig(REPO, role="sales"))}
        self.assertNotIn("issue_lookup", sales)
        self.assertNotIn("revenue_summary", sales)

    def test_role_is_bound_before_construction(self) -> None:
        from agent import SilentModel, build_harness
        from config import HarnessConfig

        SilentModel.calls = 0
        config = HarnessConfig(REPO, role="engineering")
        self.assertEqual(config.role, "engineering")
        graph = build_harness(config)
        self.assertIsNotNone(graph)
        self.assertEqual(SilentModel.calls, 0)
