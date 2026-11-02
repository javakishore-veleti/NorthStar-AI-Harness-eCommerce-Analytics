# DOM-004 revenue_summary design

Issue #7 adds the financials domain from ARCHITECTURE.md and DESIGN.md. The operation name stays `revenue_summary`. The call path matches customer and issues.

`POST /api/financials/revenue` and MCP tool `revenue_summary` take `FinancialsCtx`. The request holds `quarter` and `role`. The response holds `records` (`quarter`, `amount_usd`), `denied`, and `message`. The facade replaces `resp`, checks `revenue_summary`, then calls `RevenueSummaryTask`. The DAO matches `quarter` exactly.

Finance lookup of `2026-Q3` returns `480000`. An unknown quarter is HTTP 200 and an empty list. Engineering is denied with `Access denied: engineering cannot use revenue_summary.` and HTTP 403. The tool does not estimate a missing quarter and does not modify financial records.
