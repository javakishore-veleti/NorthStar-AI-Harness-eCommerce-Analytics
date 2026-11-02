# DOM-001 customer_brief Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the closed `customer_brief` slice from ARCHITECTURE.md and DESIGN.md.

**Architecture:** Presentation binds `X-Employee-Role` through `app/http_role.py`, then calls `CustomerFacadeFactory`. The singleton facade replaces `resp`, checks `common/access.py`, and calls `LookupCustomerTask`. The task calls `CustomerDaoFactory`. The singleton DAO queries the company database.

**Tech Stack:** Python 3.13, FastAPI, FastMCP, pydantic, unittest, SQLite via `DatabaseGateway`.

**Spec:** `docs/superpowers/specs/2026-11-01-dom-001-customer-brief-design.md`

## Global Constraints

- Follow the folder names in ARCHITECTURE.md. Do not add `company.py`, `tools/*.py`, or `server.py`.
- Domain methods take `CustomerCtx` and return `CustomerCtx`.
- Presentation does not import `daos`, `tasks`, or `common.database`.
- The facade does not import `daos` or `common.database`.
- The task does not import a facade or `common.database`.
- The DAO does not import a facade, a task, `api`, or `mcp_tools`.
- `deepagents` is not imported.
- Role matrix and denial sentences are the ones in DESIGN.md.
- Customer name match is `COLLATE NOCASE`.

---

### Task 1: Context, access, header role, and the closed stack

**Files:**
- Create: `Middleware/north-start-ecomm-mcp/north_start_ecomm_mcp/app/http_role.py`
- Create: `Middleware/north-start-ecomm-mcp/north_start_ecomm_mcp/common/access.py`
- Create: `Middleware/north-start-ecomm-mcp/north_start_ecomm_mcp/domains/customer/` as laid out in ARCHITECTURE.md
- Create: `Middleware/north-start-ecomm-mcp/tests/test_dom001.py`
- Modify: `Middleware/north-start-ecomm-mcp/north_start_ecomm_mcp/app/main.py`
- Modify: `Middleware/north-start-ecomm-mcp/north_start_ecomm_mcp/app/mcp_server.py`
- Modify: `Middleware/north-start-ecomm-mcp/tests/test_mw001.py`
- Modify: `Middleware/north-start-ecomm-mcp/tests/test_mw002.py`
- Modify: `Middleware/north-start-ecomm-mcp/tests/test_mw003.py`

- [x] **Step 1: Write `tests/test_dom001.py` for the DESIGN.md customer contract**

Cover sales Acme (`C-101`, seeded need, `buyer@acme.example`), unknown name HTTP 200, case-insensitive name, header role over a body role, unknown role HTTP 403 with `Unknown employee role: unknown.`, a client-supplied `resp.records` replaced before return, the DAO reading `ctx.req.customer` only, the MCP tool name and catalog text, and `audit_package` returning `[]`.

- [x] **Step 2: Run the new test and confirm it fails because the package is missing**

Run: `uv run --reinstall-package north-start-ecomm-mcp python -m unittest tests.test_dom001 -v`

Expected: FAIL or ERROR on import of `domains.customer`.

- [x] **Step 3: Add the stack from ARCHITECTURE.md and DESIGN.md**

DTOs use `customer` and `role` on the request, and `records`, `denied`, and `message` on the response. Records hold `id`, `name`, `need`, and `contact`.

`common/access.py` uses this matrix:

```python
MATRIX = {
    "sales": frozenset({"customer_brief", "send_proposal"}),
    "engineering": frozenset({"customer_brief", "issue_lookup"}),
    "finance": frozenset({"customer_brief", "revenue_summary"}),
}
```

Unknown role: `Unknown employee role: {role}.` Empty role is shown as `unknown`. Known role without the operation: `Access denied: {role} cannot use {operation}.`

The DAO query is:

```sql
SELECT id, name, need, contact
FROM customers
WHERE name = ? COLLATE NOCASE
```

`POST /api/customer/brief` returns 403 when `resp.denied` is true, otherwise 200. The MCP tool is `customer_brief`.

- [x] **Step 4: Run the full suite**

Run: `uv run --reinstall-package north-start-ecomm-mcp python -m unittest discover -s tests -v`

Expected: PASS. The M1 tests that asserted `domains/` was absent now assert the closed-layer audit passes and that only a DAO imports `common.database`.

- [x] **Step 5: Commit**
