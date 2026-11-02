"""Calls the middleware MCP server. Does not open the company database."""

from __future__ import annotations

import asyncio
from typing import Any


class CompanyMcpClient:
    def __init__(self, mcp_url: str, role: str) -> None:
        self.mcp_url = mcp_url
        self.role = role

    def server_config(self) -> dict[str, Any]:
        return {
            "mcpServers": {
                "northstar": {
                    "url": self.mcp_url,
                    "transport": "http",
                    "headers": {"X-Employee-Role": self.role},
                }
            }
        }

    def call(self, tool_name: str, req: dict[str, str]) -> Any:
        return asyncio.run(self._call(tool_name, req))

    async def _call(self, tool_name: str, req: dict[str, str]) -> Any:
        from fastmcp import Client

        async with Client(self.server_config()) as client:
            result = await client.call_tool(tool_name, {"ctx": {"req": req}})
        data = getattr(result, "data", None)
        return result if data is None else data
