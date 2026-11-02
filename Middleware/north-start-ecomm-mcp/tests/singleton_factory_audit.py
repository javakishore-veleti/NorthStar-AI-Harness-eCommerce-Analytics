"""Singleton and objects_factory audit.

Presentation, tasks, facades, and DAOs are singleton classes. Callers obtain
them from that layer's objects_factory. Module-level operation functions fail
this audit.
"""

from __future__ import annotations

import ast
from pathlib import Path

_LAYERS = ("api", "mcp_tools", "facades", "daos")
_FUNCTION_LAYERS = ("api", "mcp_tools", "tasks")


def audit_package(package: Path) -> list[str]:
    domains = package / "domains"
    if not domains.exists():
        return []
    violations: list[str] = []
    for domain in sorted(path for path in domains.iterdir() if path.is_dir()):
        if not (domain / "facades").is_dir():
            continue
        for layer in _LAYERS:
            factory = domain / layer / "objects_factory.py"
            if not factory.exists():
                violations.append(f"{domain.name}/{layer} has no objects_factory.py")
        task_factories = list(domain.glob("facades/*/tasks/objects_factory.py"))
        if not task_factories:
            violations.append(f"{domain.name} tasks have no objects_factory.py")
    for path in sorted(domains.rglob("*.py")):
        relative = path.relative_to(package)
        violations.extend(violations_for(relative, path.read_text(encoding="utf-8")))
    return violations


def violations_for(relative: Path, source: str) -> list[str]:
    found: list[str] = []
    tree = ast.parse(source)
    if _in_function_layer(relative):
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                found.append(f"{relative} defines module function {node.name}")
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name.endswith("Impl"):
            if not _uses_singleton(node):
                found.append(f"{relative} class {node.name} is not a Singleton")
    if relative.name == "objects_factory.py":
        names = [node.name for node in tree.body if isinstance(node, ast.ClassDef)]
        if not any(name.endswith("Factory") for name in names):
            found.append(f"{relative} has no Factory class")
    return found


def _in_function_layer(relative: Path) -> bool:
    return any(part in _FUNCTION_LAYERS for part in relative.parts)


def _uses_singleton(node: ast.ClassDef) -> bool:
    for keyword in node.keywords:
        if keyword.arg != "metaclass":
            continue
        value = keyword.value
        if isinstance(value, ast.Name) and value.id == "Singleton":
            return True
    return False
