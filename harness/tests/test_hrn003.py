import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


class ReviewerTests(unittest.TestCase):
    def test_reviewer_company_tools_are_customer_brief_only(self) -> None:
        from agent import SilentModel, company_tools
        from config import HarnessConfig
        from stages import PARENT_CALL_LIMIT, REVIEWER_CALL_LIMIT, reviewer_subagent

        lookup = next(
            tool
            for tool in company_tools(HarnessConfig(REPO, role="sales"))
            if tool.name == "customer_brief"
        )
        spec = reviewer_subagent(lookup, SilentModel())
        names = [tool.name for tool in spec["tools"]]
        self.assertEqual(names, ["customer_brief"])
        self.assertNotIn("send_proposal", names)
        self.assertEqual(spec["middleware"][0].run_limit, REVIEWER_CALL_LIMIT)
        self.assertNotEqual(PARENT_CALL_LIMIT, REVIEWER_CALL_LIMIT)

    def test_construction_leaves_the_delegate_off_and_skips_the_provider(self) -> None:
        from agent import SilentModel, build_harness
        from config import HarnessConfig
        from stages import general_purpose_delegate_enabled, parent_middleware

        SilentModel.calls = 0
        graph = build_harness(HarnessConfig(REPO, role="sales"))
        self.assertIsNotNone(graph)
        self.assertEqual(SilentModel.calls, 0)
        self.assertFalse(general_purpose_delegate_enabled())
        self.assertEqual(parent_middleware()[0].run_limit, 10)
