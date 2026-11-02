# DOM-003 issue_lookup design

Issue #6 adds the issues domain from [ARCHITECTURE.md](../../../ARCHITECTURE.md) and [DESIGN.md](../../../DESIGN.md). The call path matches customer: presentation, facade, task, DAO.

`POST /api/issues/lookup` and MCP tool `issue_lookup` take `IssueCtx`. The request holds `customer` and `role`. The response holds `records` (`id`, `customer`, `symptom`, `owner`), `denied`, and `message`. The facade replaces `resp`, checks `issue_lookup` in `common/access.py`, then calls `LookupIssueTask`. The DAO queries `issues` with `COLLATE NOCASE` through `DatabaseGateway`.

Engineering lookup of Beacon returns `INC-42`. Finance is denied with `Access denied: finance cannot use issue_lookup.` and HTTP 403. An unknown customer is HTTP 200 and an empty list. The lookup does not change the issue.
