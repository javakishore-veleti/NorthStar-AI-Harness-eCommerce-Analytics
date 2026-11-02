import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]


class CompanyGuidanceTests(unittest.TestCase):
    def test_proposal_skill_names_the_four_sections(self) -> None:
        text = (REPO / "skills/company/write-proposal/SKILL.md").read_text(encoding="utf-8")
        for section in ("Customer goal", "Proposed scope", "Assumptions", "Next steps"):
            self.assertIn(section, text)
        self.assertNotIn(".py", Path("skills/company/write-proposal/SKILL.md").suffix)

    def test_triage_skill_ends_on_the_evidence_line(self) -> None:
        text = (REPO / "skills/team/triage-issue/SKILL.md").read_text(encoding="utf-8")
        self.assertIn(
            "Finish with evidence, next check, owner and unresolved questions.",
            text,
        )
        self.assertTrue(text.strip().endswith("Do not claim that a proposed fix has been executed."))

    def test_guidance_files_are_markdown(self) -> None:
        paths = [
            REPO / "company/AGENTS.md",
            REPO / "skills/company/write-proposal/SKILL.md",
            REPO / "skills/team/triage-issue/SKILL.md",
        ]
        for path in paths:
            self.assertEqual(path.suffix, ".md")
            self.assertIn("Northstar", path.read_text(encoding="utf-8"))
