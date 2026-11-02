import ast
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


class HealthTests(unittest.TestCase):
    def test_health_returns_ok(self) -> None:
        from fastapi.testclient import TestClient
        from north_start_ecomm_mcp.app.main import create_app

        with TestClient(create_app()) as client:
            response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})


class MountTests(unittest.TestCase):
    def test_mcp_is_mounted_with_its_lifespan(self) -> None:
        from starlette.routing import Mount
        from north_start_ecomm_mcp.app.main import create_app

        app = create_app()
        mounts = [route for route in app.routes if isinstance(route, Mount)]
        mcp_mounts = [route for route in mounts if route.path == "/mcp"]
        self.assertEqual(len(mcp_mounts), 1)
        self.assertIs(app.router.lifespan_context, mcp_mounts[0].app.lifespan)

    def test_mcp_route_is_not_missing(self) -> None:
        from fastapi.testclient import TestClient
        from north_start_ecomm_mcp.app.main import create_app

        with TestClient(create_app()) as client:
            response = client.get("/mcp")
        self.assertNotEqual(response.status_code, 404)
        self.assertNotIn("not initialized", response.text.lower())

    def test_sources_do_not_import_a_domain(self) -> None:
        package = PROJECT / "north_start_ecomm_mcp"
        self.assertTrue((package / "domains" / "customer").is_dir())
        for path in package.rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    names = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom):
                    names = [node.module or ""]
                else:
                    continue
                for name in names:
                    self.assertNotIn("deepagents", name.split("."))
                    if "app" in path.relative_to(package).parts:
                        self.assertNotIn("daos", name.split("."))
                        self.assertNotIn("tasks", name.split("."))
                        self.assertFalse(name.endswith("common.database"))
