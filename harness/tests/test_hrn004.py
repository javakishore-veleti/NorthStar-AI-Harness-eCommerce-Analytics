import ast
import unittest
from pathlib import Path

HARNESS = Path(__file__).resolve().parents[1]
REPO = HARNESS.parent


class ApprovalConfigTests(unittest.TestCase):
    def test_send_is_interrupted_and_construction_skips_the_provider(self) -> None:
        from agent import SilentModel, build_harness
        from approval import INTERRUPT_ON
        from config import HarnessConfig

        self.assertEqual(
            INTERRUPT_ON["send_proposal"]["allowed_decisions"],
            ["approve", "reject"],
        )
        SilentModel.calls = 0
        graph = build_harness(HarnessConfig(REPO, role="sales"))
        self.assertIsNotNone(graph)
        self.assertEqual(SilentModel.calls, 0)

    def test_harness_has_no_email_transport(self) -> None:
        banned = ("smtplib", "smtp", "email.mime", "email.message")
        for path in HARNESS.glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                modules = []
                if isinstance(node, ast.Import):
                    modules.extend(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    modules.append(node.module)
                for module in modules:
                    self.assertFalse(any(module.startswith(name) for name in banned), module)
