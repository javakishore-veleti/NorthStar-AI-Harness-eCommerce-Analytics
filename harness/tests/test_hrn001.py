import ast
import os
import unittest
from pathlib import Path

HARNESS = Path(__file__).resolve().parents[1]
REPO = HARNESS.parent
MODULES = ("agent.py", "stages.py", "config.py", "mcp_client.py")


def import_violations(source: str, filename: str) -> list[str]:
    found: list[str] = []
    tree = ast.parse(source)
    for node in ast.walk(tree):
        modules: list[str] = []
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module)
        for module in modules:
            if "daos" in module.split(".") or module.endswith("common.database"):
                found.append(f"{filename} imports {module}")
    return found


class HarnessRootTests(unittest.TestCase):
    def test_harness_import_graph_skips_daos_and_the_database(self) -> None:
        found: list[str] = []
        for name in MODULES:
            source = (HARNESS / name).read_text(encoding="utf-8")
            found.extend(import_violations(source, name))
        self.assertEqual(found, [])

    def test_a_dao_import_fails_the_scan(self) -> None:
        source = (
            "from north_start_ecomm_mcp.domains.customer.daos.objects_factory "
            "import CustomerDaoFactory\n"
        )
        found = import_violations(source, "agent.py")
        self.assertEqual(
            found,
            ["agent.py imports north_start_ecomm_mcp.domains.customer.daos.objects_factory"],
        )

    def test_scripted_construction_does_not_call_a_provider(self) -> None:
        from agent import SilentModel, build_harness
        from config import HarnessConfig

        SilentModel.calls = 0
        os.environ.pop("OPENAI_API_KEY", None)
        os.environ.pop("ANTHROPIC_API_KEY", None)
        config = HarnessConfig(REPO, mcp_url="http://127.0.0.1:8080/mcp", role="sales")
        graph = build_harness(config)
        self.assertIsNotNone(graph)
        self.assertEqual(SilentModel.calls, 0)
        self.assertEqual(config.provider_env_var_names(), ("OPENAI_API_KEY", "ANTHROPIC_API_KEY"))

    def test_company_tools_point_at_the_mcp_server_and_hide_role(self) -> None:
        from agent import company_tools
        from config import HarnessConfig

        config = HarnessConfig(REPO, mcp_url="http://127.0.0.1:8080/mcp", role="sales")
        tools = {tool.name: tool for tool in company_tools(config)}
        self.assertEqual(
            set(tools),
            {"customer_brief", "issue_lookup", "revenue_summary", "send_proposal"},
        )
        for tool in tools.values():
            self.assertNotIn("role", tool.args)
        client = tools["customer_brief"].func.__closure__[0].cell_contents
        self.assertEqual(client.mcp_url, "http://127.0.0.1:8080/mcp")
        self.assertEqual(
            client.server_config()["mcpServers"]["northstar"]["headers"]["X-Employee-Role"],
            "sales",
        )

    def test_context_paths_are_the_teaching_files(self) -> None:
        from stages import company_context

        context = company_context(REPO)
        self.assertEqual(context["memory"], ["/company/AGENTS.md"])
        self.assertEqual(context["skills"], ["/skills/company/", "/skills/team/"])
        self.assertIn("Northstar", str(context["agents_text"]))
