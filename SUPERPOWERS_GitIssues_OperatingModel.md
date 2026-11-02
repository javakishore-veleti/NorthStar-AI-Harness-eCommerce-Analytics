# Superpowers + GitHub Issues — Cursor Operating Model

**Repository:** `javakishore-veleti/NorthStar-AI-Harness-eCommerce-Analytics`  
**Purpose:** Execute GitHub issues and milestone outcomes using Superpowers as the engineering methodology and Cursor as the only coding environment for now. Claude Code is out of this phase.  
**Status:** Operating procedure. No issue, test, or milestone is complete solely because an agent says so.

The product shape is [ARCHITECTURE.md](ARCHITECTURE.md) and [DESIGN.md](DESIGN.md). This file is how that shape gets built. The teaching harness is the behavior source. It is not the folder layout to copy.

## 1. Operating principles

1. **GitHub issue is the unit of scope.** Each change maps to one issue, or a documented batch. Every PR references the issues it addresses.
2. **Milestone is the unit of delivery.** Closing a milestone requires working software, evidence, and a gate. Closed issue counts are not the gate.
3. **Superpowers is the method, not a model.** Use brainstorming, planning, worktrees, TDD, systematic debugging, subagent execution, code review, and verification in Cursor.
4. **Cursor is the control center and the implementer.** Do not hand implementation to Claude Code during this phase.
5. **Human approves architecture changes, provider spend, and merges.** Do not call a paid model, send email, or merge because an issue mentions a demo.
6. **Evidence before status.** Record commands and outputs. Separate scripted tests from a live model transcript.
7. **Small batches, clean branches.** Prefer one issue per PR. Batch two issues only when they share one test run and one rollback boundary.

Company rules that every issue inherits:

- Presentation calls the facade factory. The facade calls its task. The task calls its DAO factory. The DAO calls the database gateway.
- Domain methods take the domain context as their only argument.
- `X-Employee-Role` sets `ctx.req.role`. The model does not assign its role.
- `send_proposal` writes a local outbox row. It does not send email.
- `deepagents` stays out of `domains/`.

## 2. One-time Cursor and repository setup

### 2.1 Prerequisites

- Open this repository in Cursor and fast-forward `main`.
- Install `git`, GitHub CLI (`gh`), uv, and Python 3.13.
- Superpowers skills are in `.cursor/skills/<name>/SKILL.md`. Start a new Agent session so Cursor discovers them. Run steps are in [README.md](README.md).
  - **1 Nov 2026.** `/add-plugin` was not available as a tool, so the marketplace plugin and its session-start hook are not installed. The 14 Superpowers 6.3.0 skill directories were copied from the local Claude plugin cache into `.cursor/skills/`. The MIT license is `.cursor/skills/SUPERPOWERS-LICENSE.txt`. `/add-plugin superpowers` remains optional if you also want the marketplace hook.
- Read `ARCHITECTURE.md`, `DESIGN.md`, `SUPERPOWERS_ADOPTION.md`, this file, and `company/AGENTS.md` before coding. `company/AGENTS.md` and both `SKILL.md` files on `main` are truncated. CTX-001 restores them. Do not invent the missing procedure text.
- Confirm native milestones M1–M8 and issues #1–#22 exist. Issue titles are not a substitute for milestone assignment.

### 2.2 Verify GitHub and the working tree

```bash
gh auth status
gh repo view javakishore-veleti/NorthStar-AI-Harness-eCommerce-Analytics
git status --short
git pull --ff-only origin main
gh issue list --repo javakishore-veleti/NorthStar-AI-Harness-eCommerce-Analytics --state open --limit 100
gh api repos/javakishore-veleti/NorthStar-AI-Harness-eCommerce-Analytics/milestones --paginate --jq '.[].title'
```

**1 Nov 2026 — milestones created.** Eight open milestones, M1 through M8, and 22 open issues assigned to them. Labels: `priority:P0`, `priority:P1`, `priority:P2`, `middleware`, `domain`, `access`, `harness`, `testing`.

### 2.3 Issue board

Use GitHub Project statuses **Backlog → Ready → In Progress → In Review → Done**, plus **Blocked**. Filter by native milestone and priority. Keep one issue in progress per worktree.

**1 Nov 2026.** Created user project 8, [NorthStar eCommerce Analytics Harness](https://github.com/users/javakishore-veleti/projects/8) (`PVT_kwHOAFyDNM4BpxKm`), and linked this repository. Issues #1–#22 were added. Status options were left on the project defaults in that session. Set each item to Backlog before starting MW-001, and add a Blocked option if the default set does not have one.

## 3. Standard issue lifecycle

### Step 1 — Select the next issue

Filter to the current native milestone, `priority:P0` first. Read the issue, ARCHITECTURE.md, DESIGN.md, and the code the issue is allowed to touch. If the issue is unclear, comment on it. Do not start speculative implementation. Move the project status to **In Progress** when work starts.

```bash
gh issue view ISSUE_NUMBER --repo javakishore-veleti/NorthStar-AI-Harness-eCommerce-Analytics --comments
```

### Step 2 — Open a clean worktree

```bash
git fetch origin
git worktree add ../ns-issue-ISSUE_NUMBER -b issue/ISSUE_NUMBER-short-description origin/main
```

Open that folder in its own Cursor window. Do not implement on `main`.

### Step 3 — Brainstorm and approve the design

Ask Superpowers `brainstorming` for the issue. Cover current behavior, desired behavior, layer boundaries, and what the issue must not change. A trivial docs fix can be a short issue comment. A new domain method needs a design note.

**Human gate A:** Approve the design before changing context fields, facade methods, the role matrix, or harness approval behavior.

### Step 4 — Write an executable plan

Ask Superpowers `writing-plans`. Require file paths, the failing test, the implementation step, and the command that proves the acceptance criteria. Keep substantial plans in `docs/plans/` or the PR body. A plan is not completed work.

**Human gate B:** Approve the plan when it changes the HTTP contract, the SQLite schema, or which process imports `deepagents`.

### Step 5 — Implement with Superpowers

| Issue type | Primary | Review |
|---|---|---|
| Middleware package, FastAPI, FastMCP, database | Cursor Agent + Superpowers | Cursor review |
| Domain slice | Cursor Agent + Superpowers | Cursor review plus the closed-layer audit |
| Access matrix | Cursor Agent + Superpowers | Cursor review |
| Harness, approval, workspace, UI | Cursor Agent + Superpowers | Human approval before any provider call |
| Docs and skill text | Cursor Agent + Superpowers | Lightweight review |

Use `test-driven-development`: write the failing test, then the minimum code, then refactor. Use `subagent-driven-development` or `executing-plans` based on size. Do not give a subagent a provider key.

### Step 6 — Validate and review

Run the tests in the worktree. Use `systematic-debugging` on failures and `verification-before-completion` before claiming success.

| Acceptance criterion | Test/command | Actual result | Evidence link |
|---|---|---|---|
| Example criterion | `uv run python -m unittest` | PASS/FAIL/NOT RUN | Log or CI |

Do not mark PASS without running the check. Do not mark a model demo PASS from a scripted test.

### Step 7 — Commit and open a PR

```bash
git status --short
git diff --check
git add <reviewed-files>
git commit -m "feat(scope): implement ISSUE_NUMBER requirement"
git push -u origin issue/ISSUE_NUMBER-short-description
gh pr create --base main --head issue/ISSUE_NUMBER-short-description \
  --title "[ISSUE-ID] Short outcome" --body "Closes #ISSUE_NUMBER"
```

Include the issue link, layer impact, tests, and rollback note. Do not commit `.runtime/` or `.env`.

### Step 8 — Merge, close, and update the log

Merge only after the required checks and the acceptance evidence are reviewed. Confirm the issue closes and the native milestone is correct. Set the project status to Done. Fill the matching rows in [SUPERPOWERS_GitIssues_Progress.md](SUPERPOWERS_GitIssues_Progress.md) with real start times, finish times, and the PR link. Remove the worktree after the commits are on `main`.

## 4. Reusable Cursor Agent prompt

```text
Use Superpowers to implement GitHub issue #<NUMBER> in
javakishore-veleti/NorthStar-AI-Harness-eCommerce-Analytics.
Read the issue, ARCHITECTURE.md, DESIGN.md, SUPERPOWERS_ADOPTION.md,
and SUPERPOWERS_GitIssues_OperatingModel.md.
Start with brainstorming, then an exact-file writing plan. Do not code
until I approve a change to context fields, the role matrix, or the
harness approval boundary. Use an isolated worktree.
Implement test-first. Run the real test command.
Report each acceptance criterion as PASS, FAIL, or NOT RUN with evidence.
Do not call a paid model, send email, or merge without my approval.
Prepare a PR that references the issue.
Keep domain methods on the domain context only, and do not skip a closed layer.
```

## 5. Batch operating model

Batch only when the issues share one testable deliverable.

1. List included issues and explicit exclusions.
2. Keep each issue traceable to its own acceptance criteria.
3. Prefer one PR per issue. Land a shared test harness first when later issues need it.
4. Use `Closes #N` only when every acceptance criterion of that issue passed.
5. Re-run the closed-layer audit and the role matrix after the last domain change.
6. Do not close the milestone until its gate passes.

**Good batch:** DOM-003 and DOM-004 after DOM-001 has landed, if each slice still has its own tests.  
**Avoid batch:** HRN-004 and DOM-005 in one PR. Outbox recording and human approval are different processes.

## 6. Milestone delivery

Issue numbers are GitHub issue numbers. Confirm milestone assignment before starting.

| Milestone | Issues | Delivery outcome | Gate to close |
|---|---|---|---|
| **M1 — Middleware Foundation** | #1 MW-001, #2 MW-002, #3 MW-003 | Package, health, FastMCP mount, singleton, seeded company database | Health responds, seed rows exist, singleton test passes |
| **M2 — Customer Domain** | #4 DOM-001, #5 DOM-002 | `customer_brief` closed slice and header role binding | Acme returns `C-101`. Header role wins. Unknown role is denied |
| **M3 — Issues and Financials** | #6 DOM-003, #7 DOM-004 | `issue_lookup` and `revenue_summary` | Beacon returns `INC-42`. `2026-Q3` returns `480000`. Finance cannot look up issues |
| **M4 — Proposals Domain** | #8 DOM-005, #9 DOM-006 | Local outbox, canonical customer, denials | Repeat send reuses the receipt. Unknown customer writes no row. Engineering cannot send |
| **M5 — Access Verification** | #10 ACC-001, #11 ACC-002 | Full role matrix and import audit | Twelve role/operation pairs match DESIGN.md. Audit passes on all four domains |
| **M6 — Harness Context** | #12 CTX-001, #13 CTX-002 | Restored skills and company guidance outside domain code | Skill text matches the teaching procedures. Domain code does not import skills |
| **M7 — Harness Agent** | #14 HRN-001, #15 HRN-002, #16 HRN-003, #17 HRN-004, #18 HRN-005 | `deepagents` calls MCP, role-scoped tools, reviewer, approval, protected files | Harness does not import DAOs. Rejecting send writes no outbox row. No provider call in the scripted checks |
| **M8 — Persistence and Employee Interface** | #19 HRN-006, #20 HRN-007, #21 HRN-008, #22 HRN-009 | Workspace, checkpoints, localhost UI, three teaching prompts | Workspace is not the company database. Sales draft cites `C-101` and does not send. Engineering cites `INC-42`. Finance cites `480000` |

M1 through M5 are the middleware. M6 can proceed beside them because it only restores markdown. M7 starts after ACC-001 and CTX-001. M8 starts after the harness can call tools. Close a milestone only when its own gate passes.

### M1 checklist

- [ ] MW-001: localhost health and `/mcp` mount.
- [ ] MW-002: singleton identity and the import audit scaffold.
- [ ] MW-003: fresh database has `C-101`, `C-102`, `INC-42`, and `2026-Q3` / `480000`.
- [ ] `.runtime/` is not committed.

### M2 checklist

- [ ] DOM-001: sales lookup of Acme returns `C-101` and `buyer@acme.example`.
- [ ] DOM-002: missing role denied, body role ignored, engineering still allowed to look up the customer.

### M3 checklist

- [ ] DOM-003: engineering lookup of Beacon returns `INC-42`. Finance is denied.
- [ ] DOM-004: finance `2026-Q3` returns `480000`. Unknown quarter is an empty list.

### M4 checklist

- [ ] DOM-005: identical proposal body reuses one receipt. Status is `simulated_send`.
- [ ] DOM-006: unknown customer and engineering send leave the outbox unchanged.

### M5 checklist

- [ ] ACC-001: all twelve role/operation pairs match the matrix.
- [ ] ACC-002: audit passes, and a DAO import from a task fails the audit when tried locally and then removed.

### M6 checklist

- [ ] CTX-001: `write-proposal` and `triage-issue` no longer contain truncated bracket text.
- [ ] CTX-002: `north_start_ecomm_mcp` does not import `skills` or `company`.

### M7 checklist

- [ ] HRN-001: harness constructs with no provider call and no DAO import.
- [ ] HRN-002: sales tool list has no `issue_lookup` or `revenue_summary`.
- [ ] HRN-003: reviewer company tool is `customer_brief` only.
- [ ] HRN-004: reject writes zero outbox rows. Approve writes one.
- [ ] HRN-005: model filesystem cannot overwrite `company/AGENTS.md`.

### M8 checklist

- [ ] HRN-006: `/work/proposal.md` lives under the task workspace, not in company SQLite.
- [ ] HRN-007: restoring a checkpoint does not roll back the company seed.
- [ ] HRN-008: role profile sets `X-Employee-Role`. Interface is localhost.
- [ ] HRN-009: three teaching prompts recorded with tool citations. State the provider cost. Do not treat this as done from unit tests alone.

## 7. Milestone closure

1. Filter issues by the native milestone. Required issues are closed and linked to merged PRs.
2. Pull `main` and run the milestone tests. Save the output.
3. Write `docs/milestones/M<NUMBER>-completion.md` with PR links, commands, observed results, and remaining risks.
4. Human acceptance, then close the milestone in GitHub.
5. Update [SUPERPOWERS_GitIssues_Progress.md](SUPERPOWERS_GitIssues_Progress.md) and only then adjust resume claims.

## 8. Definition of done

**Issue:** scope met, tests actually run, acceptance criteria supported, docs updated when the contract changed, no unapproved provider call, issue closed on the correct milestone.

**Milestone:** every required issue is done, the gate in section 6 passed, and the completion note exists.

**Superpowers evidence:** for each issue, the progress log shows which slash-command steps ran, with start, finish, and PR. An installed plugin is not evidence that a skill was used.

## 9. Weekly cadence

| Cadence | Activity | Output |
|---|---|---|
| Monday | Review the current milestone, pick 1–3 issues | Weekly issue plan |
| Daily start | Read the issue, update the worktree, design or plan | Approved plan |
| Daily end | Run tests, push the branch, comment on the issue | Traceable progress |
| Friday | Merge approved PRs and update the progress log | Weekly note |
| Milestone gate | Section 7 | Signed completion note |

## 10. Failure modes

- **Coding starts without a plan.** Stop. Run brainstorming and writing-plans.
- **A layer skip appears.** Presentation importing a DAO, or a task importing a facade, fails ACC-002. Fix the call path. Do not weaken the audit.
- **A method grows a customer or quarter argument.** Put the value on the domain context.
- **The model is allowed to set its role.** Presentation overwrites `ctx.req.role` from the header.
- **`send_proposal` gains an email client.** Remove it. The outbox is the product behavior.
- **Company SQLite and the task workspace share one file.** Split them. HRN-006 and HRN-007 exist for that split.
- **An issue title names a milestone but the GitHub milestone is empty.** Assign the native milestone before counting the issue.
- **The progress log is filled without a PR.** Leave the cells blank until the step happened.

## 11. Quick links

- [Repository](https://github.com/javakishore-veleti/NorthStar-AI-Harness-eCommerce-Analytics)
- [Issues](https://github.com/javakishore-veleti/NorthStar-AI-Harness-eCommerce-Analytics/issues)
- [Milestones](https://github.com/javakishore-veleti/NorthStar-AI-Harness-eCommerce-Analytics/milestones)
- [Project board](https://github.com/users/javakishore-veleti/projects/8)
- [Superpowers](https://github.com/obra/superpowers)
- [Adoption plan](SUPERPOWERS_ADOPTION.md)
- [Progress log](SUPERPOWERS_GitIssues_Progress.md)

**Start here:** MW-001 / GitHub issue #1. Run one full Superpowers lifecycle before opening a batch.
