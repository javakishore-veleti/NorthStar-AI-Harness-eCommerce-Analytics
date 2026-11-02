"""Harness settings. Provider credentials stay in the environment."""

from __future__ import annotations

import os
from pathlib import Path

PROVIDER_ENV_VARS = ("OPENAI_API_KEY", "ANTHROPIC_API_KEY")
DEFAULT_MCP_URL = "http://127.0.0.1:8080/mcp"


class HarnessConfig:
    """Repo root, middleware MCP URL, and the role chosen by application code."""

    def __init__(
        self,
        repo_root: Path,
        mcp_url: str | None = None,
        role: str = "sales",
    ) -> None:
        self.repo_root = Path(repo_root)
        self.mcp_url = mcp_url or os.environ.get("NORTHSTAR_MCP_URL", DEFAULT_MCP_URL)
        self.role = role

    def provider_env_var_names(self) -> tuple[str, ...]:
        """Names only. Construction does not read the values."""
        return PROVIDER_ENV_VARS
