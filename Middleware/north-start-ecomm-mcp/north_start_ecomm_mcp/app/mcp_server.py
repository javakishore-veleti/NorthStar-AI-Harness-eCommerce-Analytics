from __future__ import annotations

from fastmcp import FastMCP
from starlette.applications import Starlette


def build_mcp_server() -> FastMCP:
    return FastMCP("north-start-ecomm-mcp")


def build_mcp_app() -> Starlette:
    return build_mcp_server().http_app(path="/")
