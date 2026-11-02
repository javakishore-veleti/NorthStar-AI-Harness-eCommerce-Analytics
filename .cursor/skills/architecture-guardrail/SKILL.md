---
name: architecture-guardrail
description: >-
  Guardrail for every GitHub issue. Use before writing-plans and again before
  verification-before-completion. Checks ARCHITECTURE.md and DESIGN.md, and
  requires presentation, tasks, facades, and DAOs to be singleton classes
  reached through objects_factory. Invoke as /architecture-guardrail.
---

# Architecture guardrail

Run this on every issue before `/writing-plans`, and again before `/verification-before-completion`. Do not write domain code while either check fails.

## Check the documents first

Read the issue, `ARCHITECTURE.md`, and `DESIGN.md`.

Stop when the issue needs a type, method, factory, route, or tool those two documents do not name. Add the missing name to both documents in the same change before writing the class. A skill, a comment, or a plan does not replace those documents.

`app/main.py`, `app/mcp_server.py`, `app/http_role.py`, `common/access.py`, and `common/database.py` `company_db_path` stay ordinary functions. They are process wiring and shared helpers. Domain operations do not.

## Check the classes

From the API through the MCP tool, the facade, the task, and the DAO:

- The operation is a class. A module-level function is not an operation.
- The implementation uses the `Singleton` metaclass.
- An interface names the method. The implementation class name ends in `Impl`.
- Callers obtain the object from that layer's `objects_factory`. They do not construct `*Impl`.
- The method takes the domain context. The API method may also take `X-Employee-Role`. The MCP method reads that header inside the method, then calls the facade factory with the context only.
- Presentation calls the facade factory. The facade calls its task factory. The task calls its DAO factory. The DAO calls the database gateway.

## Run the audit

From `Middleware/north-start-ecomm-mcp`:

```bash
uv run python -m unittest tests.test_mw002.ImportAuditTests.test_singleton_factory_audit_passes tests.test_mw002.ImportAuditTests.test_audit_passes_on_the_current_tree -v
```

A failure is a stop. Do not plan around it and do not leave a new operation as a function because a framework wants a callable. Bind the singleton method to FastAPI or FastMCP.

## Progress log

Fill the `/architecture-guardrail` row in `SUPERPOWERS_GitIssues_Progress.md` only after this command has run for that issue. Leave the row blank when it has not run. Do not mark a closed issue's row complete for work that happened before the command existed.
