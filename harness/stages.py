"""Load company guidance and skill directories for the harness."""

from __future__ import annotations

from pathlib import Path


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
