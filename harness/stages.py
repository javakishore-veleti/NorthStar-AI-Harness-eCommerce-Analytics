"""Load company guidance and skill directories for the harness."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from deepagents import (
    GeneralPurposeSubagentProfile,
    HarnessProfile,
    register_harness_profile,
)
from deepagents.middleware.filesystem import FilesystemPermission
from langchain.agents.middleware import ModelCallLimitMiddleware, TodoListMiddleware

PARENT_CALL_LIMIT = 10
REVIEWER_CALL_LIMIT = 4
_PROFILE_KEYS = ("silentmodel", "openai", "anthropic")


def company_context(repo_root: Path) -> dict[str, object]:
    agents = repo_root / "company" / "AGENTS.md"
    skill_dirs = (
        repo_root / "skills" / "company",
        repo_root / "skills" / "team",
    )
    if not agents.is_file():
        raise FileNotFoundError(agents)
    for directory in skill_dirs:
        if not any(directory.rglob("SKILL.md")):
            raise FileNotFoundError(directory)
    return {
        "memory": ["/company/AGENTS.md"],
        "skills": ["/skills/company/", "/skills/team/"],
        "agents_text": agents.read_text(encoding="utf-8"),
    }


def disable_general_purpose_delegate() -> None:
    """Register only the proposal reviewer. The automatic broad delegate stays off."""
    profile = HarnessProfile(
        general_purpose_subagent=GeneralPurposeSubagentProfile(enabled=False),
    )
    for key in _PROFILE_KEYS:
        register_harness_profile(key, profile)


def general_purpose_delegate_enabled(key: str = "silentmodel") -> bool:
    from deepagents.profiles.harness.harness_profiles import _get_harness_profile

    profile = _get_harness_profile(key)
    setting = profile.general_purpose_subagent
    return bool(setting and setting.enabled)


def parent_middleware() -> list[Any]:
    return [
        ModelCallLimitMiddleware(run_limit=PARENT_CALL_LIMIT, exit_behavior="end"),
        TodoListMiddleware(),
    ]


def reference_permissions() -> list[FilesystemPermission]:
    return [
        FilesystemPermission(
            operations=["write"],
            paths=["/company/**", "/skills/**"],
            mode="deny",
        )
    ]


def write_model_file(repo_root: Path, relative: str, content: str) -> Path:
    """Write a model file. company/ and skills/ stay read-only."""
    root = repo_root.resolve()
    target = (root / relative).resolve()
    try:
        rel = target.relative_to(root)
    except ValueError as exc:
        raise PermissionError(relative) from exc
    if rel.parts and rel.parts[0] in {"company", "skills"}:
        raise PermissionError(f"read-only reference path: {relative}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return target


def reviewer_subagent(lookup: Any, model: Any) -> dict[str, Any]:
    """Proposal reviewer. Company tools are customer_brief only."""
    return {
        "name": "proposal-reviewer",
        "description": "Review a proposal against customer facts; flag unsupported commitments.",
        "system_prompt": "Look up the customer. Return evidence, assumptions and corrections.",
        "model": model,
        "tools": [lookup],
        "middleware": [
            ModelCallLimitMiddleware(run_limit=REVIEWER_CALL_LIMIT, exit_behavior="end")
        ],
    }
