# NorthStar-AI-Harness-eCommerce-Analytics

NorthStar company harness for customer lookup, issue triage, revenue read, and local proposal outbox. The structure is the closed domain stack in [ARCHITECTURE.md](ARCHITECTURE.md) and [DESIGN.md](DESIGN.md). Work is tracked in GitHub milestones M1–M8 and issues #1–#22.

## Superpowers in this repo

Superpowers 6.3.0 skills are vendored so Cursor Agent can run the methodology from this repository. Source is the local Claude plugin cache of [obra/superpowers](https://github.com/obra/superpowers). The MIT license is [`.cursor/skills/SUPERPOWERS-LICENSE.txt`](.cursor/skills/SUPERPOWERS-LICENSE.txt). Copyright 2025 Jesse Vincent.

Each skill is a directory under `.cursor/skills/` with a `SKILL.md`:

| Skill | Use when |
|---|---|
| `using-superpowers` | Starting work that should follow the methodology |
| `brainstorming` | Designing an issue before code |
| `writing-plans` | Turning an approved design into file-level steps |
| `using-git-worktrees` | Opening an isolated branch for an issue |
| `executing-plans` | Implementing a written plan |
| `subagent-driven-development` | Splitting a larger issue across agents |
| `test-driven-development` | Writing the failing test first |
| `systematic-debugging` | A test or command failed |
| `verification-before-completion` | Claiming an acceptance criterion passed |
| `requesting-code-review` | Asking for review before a PR |
| `receiving-code-review` | Handling review comments |
| `finishing-a-development-branch` | Closing the branch after verification |
| `dispatching-parallel-agents` | Independent tasks with no shared state |
| `writing-skills` | Authoring a new skill |

### Run it

1. Open this repository in Cursor.
2. Start a new Agent chat. Skills are picked up at session start.
3. Point the agent at the issue and the skill. Example for the first issue:

```text
Use .cursor/skills/brainstorming/SKILL.md for GitHub issue #1 (MW-001).
Read ARCHITECTURE.md, DESIGN.md, and SUPERPOWERS_GitIssues_OperatingModel.md.
Do not edit code until the design is approved.
```

4. Continue with `writing-plans`, then `using-git-worktrees`, then `test-driven-development` or `executing-plans`, as the operating model describes. Record start time, finish time, and the pull request in [SUPERPOWERS_GitIssues_Progress.md](SUPERPOWERS_GitIssues_Progress.md).

The marketplace command `/add-plugin superpowers` is optional. It adds the session-start hook from the Cursor plugin marketplace. This repo already contains the skill files, so a new Agent session can read them without that install.

Procedure and gates: [SUPERPOWERS_GitIssues_OperatingModel.md](SUPERPOWERS_GitIssues_OperatingModel.md). Adoption notes: [SUPERPOWERS_ADOPTION.md](SUPERPOWERS_ADOPTION.md).
