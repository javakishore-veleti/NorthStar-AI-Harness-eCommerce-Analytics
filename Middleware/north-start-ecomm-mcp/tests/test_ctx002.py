import asyncio
import unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1] / "north_start_ecomm_mcp"
COMPANY_TOOLS = ("customer_brief", "issue_lookup", "revenue_summary", "send_proposal")


class SkillImportCheckTests(unittest.TestCase):
    def test_package_does_not_import_skills_or_company(self) -> None:
        from tests.closed_layer_audit import context_import_violations

        self.assertEqual(context_import_violations(PACKAGE), [])

    def test_domain_module_importing_a_skill_path_names_the_file(self) -> None:
        from tests.closed_layer_audit import context_violations_for

        relative = Path("domains/customer/api/impl/customer_brief_api_impl.py")
        source = "import skills.company.write_proposal\n"
        found = context_violations_for(relative, source)
        self.assertEqual(
            found,
            ["domains/customer/api/impl/customer_brief_api_impl.py imports skills.company.write_proposal"],
        )

    def test_domain_module_importing_company_names_the_file(self) -> None:
        from tests.closed_layer_audit import context_violations_for

        relative = Path("domains/proposals/facades/proposal_facade/proposal_facade_impl.py")
        source = "from company import AGENTS\n"
        found = context_violations_for(relative, source)
        self.assertEqual(
            found,
            ["domains/proposals/facades/proposal_facade/proposal_facade_impl.py imports company"],
        )

    def test_mcp_tool_names_stay_the_company_operations(self) -> None:
        from north_start_ecomm_mcp.app.mcp_server import build_mcp_server

        server = build_mcp_server()
        tools = asyncio.run(server.list_tools())
        names = tuple(tool.name for tool in tools)
        self.assertEqual(names, COMPANY_TOOLS)
