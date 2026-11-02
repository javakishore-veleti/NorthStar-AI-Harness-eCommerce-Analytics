"""Closed-layer import audit.

ProposalFacadeImpl may import the customer facade factory. That exception is
encoded in `_is_customer_facade_factory`. Every other cross-layer import below
fails the audit.
"""

from __future__ import annotations

import ast
from pathlib import Path


def audit_package(package: Path) -> list[str]:
    domains = package / "domains"
    if not domains.exists():
        return []
    violations: list[str] = []
    for path in sorted(domains.rglob("*.py")):
        relative = path.relative_to(package)
        violations.extend(violations_for(relative, path.read_text(encoding="utf-8")))
    return violations


def violations_for(relative: Path, source: str) -> list[str]:
    found: list[str] = []
    for module in _imported_modules(source):
        if _forbidden(relative, module):
            found.append(f"{relative} imports {module}")
    return found


def _imported_modules(source: str) -> list[str]:
    tree = ast.parse(source)
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module)
    return modules


def _forbidden(relative: Path, module: str) -> bool:
    if relative.name == "proposal_facade_impl.py" and _is_customer_facade_factory(module):
        return False
    segments = set(module.split("."))
    layer = _layer(relative)
    if layer == "presentation":
        return bool(segments & {"daos", "tasks"}) or _is_database(module)
    if layer == "facade_impl":
        return "daos" in segments or _is_database(module) or _other_domain_facade(relative, module)
    if layer == "task":
        return "facades" in segments or _is_database(module)
    if layer == "dao":
        return bool(segments & {"facades", "tasks", "api", "mcp_tools"})
    return False


def _is_customer_facade_factory(module: str) -> bool:
    segments = module.split(".")
    blocked = {"daos", "tasks", "api", "mcp_tools"}
    return (
        "customer" in segments
        and "facades" in segments
        and "objects_factory" in segments
        and blocked.isdisjoint(segments)
    )


def _is_database(module: str) -> bool:
    return module == "common.database" or module.endswith(".common.database")


def _other_domain_facade(relative: Path, module: str) -> bool:
    segments = module.split(".")
    if "domains" not in segments or "facades" not in segments:
        return False
    parts = relative.parts
    if "domains" not in parts:
        return False
    own = parts[parts.index("domains") + 1]
    imported = segments[segments.index("domains") + 1]
    return imported != own


def _layer(relative: Path) -> str:
    parts = relative.parts
    if "tasks" in parts:
        return "task"
    if "daos" in parts:
        return "dao"
    if "facades" in parts and relative.name.endswith("_impl.py"):
        return "facade_impl"
    if "api" in parts or "mcp_tools" in parts:
        return "presentation"
    return "other"
