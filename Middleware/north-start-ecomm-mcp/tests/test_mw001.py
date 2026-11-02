import os
import tomllib
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]


class PackageTests(unittest.TestCase):
    def test_directory_and_import_names(self) -> None:
        self.assertEqual(PROJECT.name, "north-start-ecomm-mcp")
        self.assertTrue((PROJECT / "north_start_ecomm_mcp").is_dir())

    def test_console_script(self) -> None:
        with (PROJECT / "pyproject.toml").open("rb") as handle:
            project = tomllib.load(handle)["project"]
        self.assertEqual(
            project["scripts"]["northstar-mcp"],
            "north_start_ecomm_mcp.app.main:main",
        )
        self.assertNotIn("deepagents", project["dependencies"])

    def test_listen_port_default_and_override(self) -> None:
        from north_start_ecomm_mcp.app.main import HOST, listen_port

        self.assertEqual(HOST, "127.0.0.1")
        env = os.environ
        previous = env.pop("NORTHSTAR_MCP_PORT", None)
        try:
            self.assertEqual(listen_port(), 8080)
            env["NORTHSTAR_MCP_PORT"] = "9091"
            self.assertEqual(listen_port(), 9091)
            env["NORTHSTAR_MCP_PORT"] = "nope"
            with self.assertRaises(ValueError):
                listen_port()
        finally:
            if previous is None:
                env.pop("NORTHSTAR_MCP_PORT", None)
            else:
                env["NORTHSTAR_MCP_PORT"] = previous
