# Design

Behavior of `north-start-ecomm-mcp`. Structure and layer rules are in [ARCHITECTURE.md](ARCHITECTURE.md).

The teaching harness this design follows is [ns-work-harness](https://github.com/aishwaryanr/awesome-generative-ai-guide/tree/main/youtube/code/ns-work-harness). Company facts, operation names, role matrix, and outbox rules stay. The call path is the closed domain stack, and every domain method takes the domain context as its only input.

Nothing in this document is implemented yet.

## Company facts

Synthetic records, created on first database open. Inserts use `INSERT OR IGNORE`, so a restart keeps outbox rows.

| Table | Seed |
| --- | --- |
| `customers` | `C-101`, Acme, "Unify weekly sales reporting across three teams", `buyer@acme.example` |
| `customers` | `C-102`, Beacon, "Investigate delayed dashboard refreshes", `ops@beacon.example` |
| `issues` | `INC-42`, Beacon, "Sync stalls when the upstream API returns HTTP 429", Data Platform |
| `revenue` | `2026-Q3`, `480000` |
| `outbox` | empty until `send_proposal` |

Columns:

- `customers(id, name, need, contact)`
- `issues(id, customer, symptom, owner)`
- `revenue(quarter, amount_usd)`
- `outbox(id, customer, body)`

Customer and issue name filters are case-insensitive (`COLLATE NOCASE`). Quarter match is exact. The customer lookup returns `id`, `name`, `need`, and `contact`. The issue lookup returns `id`, `customer`, `symptom`, and `owner`. The revenue lookup returns `quarter` and `amount_usd`. An unknown key returns an empty record list.

## Access

The employee role is application-owned. Presentation copies `X-Employee-Role` onto `ctx.req.role` and discards any role in the body. Facades enforce the matrix before they call a task.

| Role | Operations |
| --- | --- |
| `sales` | `customer_brief`, `send_proposal` |
| `engineering` | `customer_brief`, `issue_lookup` |
| `finance` | `customer_brief`, `revenue_summary` |

Denial rules, written onto `resp` and returned on the same context:

- Role missing or not in the matrix: `Unknown employee role: {role}.` Empty role is shown as `unknown`.
- Role known, operation not granted: `Access denied: {role} cannot use {operation}.`
- `resp.denied` is true in both cases. `resp.records` stays empty.

HTTP presentation returns 403 when `resp.denied` is true and 200 otherwise. MCP tools return the context either way. A missing customer on lookup is a 200 with an empty list. A missing customer on send is a 200 with `resp.message` set to `Unknown customer. Look up the customer before sending.`

## Context contract

Each domain has three DTO modules. Names are fixed.

| File | Type | Members |
| --- | --- | --- |
| `domainReq.py` | domain request | operation fields and `role` |
| `domainResp.py` | domain response | result fields, `denied`, `message` |
| `domainCtx.py` | domain context | `req`, `resp` |

Method shape on the API, the MCP tool, the facade, the task, and the DAO:

```text
def <operation>(self, ctx: <Domain>Ctx) -> <Domain>Ctx
```

Each of those types is a singleton class. Callers obtain it from that layer's `objects_factory`. FastAPI reads the JSON body into the context. The API method also accepts `X-Employee-Role`, writes it onto `req.role`, and passes the context into the facade factory. The MCP method reads the same header and then passes the context into the facade factory.

The facade starts by replacing `resp` with a new response object, then applies the access check, then calls its task factory.

### Customer

Request: `customer`, `role`.

Response: `records` (`id`, `name`, `need`, `contact`), `denied`, `message`.

| Layer | Type | Method |
| --- | --- | --- |
| API | `CustomerBriefApi` | `customer_brief(ctx)` |
| MCP | `CustomerBriefTool` | `customer_brief(ctx)` |
| Facade | `CustomerFacade` | `lookup(ctx)` |
| Task | `LookupCustomerTask` | `execute(ctx)` |
| DAO | `CustomerDao` | `find_by_name(ctx)` |

Factories: `CustomerBriefApiFactory.get_customer_brief_api()`, `CustomerBriefToolFactory.get_customer_brief_tool()`, `CustomerFacadeFactory.get_customer_facade()`, `LookupCustomerTaskFactory.get_lookup_customer_task()`, `CustomerDaoFactory.get_customer_dao()`.

Presentation:

- REST `POST /api/customer/brief`
- MCP tool `customer_brief`

Tool text for the MCP catalog: look up a customer's recorded goal and contact before answering or drafting. Cite the record id when the facts are used. The tool does not change data.

### Issues

Request: `customer`, `role`.

Response: `records` (`id`, `customer`, `symptom`, `owner`), `denied`, `message`.

| Layer | Type | Method |
| --- | --- | --- |
| API | `IssueLookupApi` | `issue_lookup(ctx)` |
| MCP | `IssueLookupTool` | `issue_lookup(ctx)` |
| Facade | `IssueFacade` | `lookup(ctx)` |
| Task | `LookupIssueTask` | `execute(ctx)` |
| DAO | `IssueDao` | `find_by_customer(ctx)` |

Factories: `IssueLookupApiFactory.get_issue_lookup_api()`, `IssueLookupToolFactory.get_issue_lookup_tool()`, `IssueFacadeFactory.get_issue_facade()`, `LookupIssueTaskFactory.get_lookup_issue_task()`, `IssueDaoFactory.get_issue_dao()`.

Presentation:

- REST `POST /api/issues/lookup`
- MCP tool `issue_lookup`

Tool text: look up a customer's reported engineering issue. The lookup does not resolve or modify the issue.

### Financials

Request: `quarter` in `YYYY-QN` form, `role`.

Response: `records` (`quarter`, `amount_usd`), `denied`, `message`.

| Layer | Type | Method |
| --- | --- | --- |
| API | `RevenueSummaryApi` | `revenue_summary(ctx)` |
| MCP | `RevenueSummaryTool` | `revenue_summary(ctx)` |
| Facade | `FinancialsFacade` | `summarize(ctx)` |
| Task | `RevenueSummaryTask` | `execute(ctx)` |
| DAO | `FinancialsDao` | `find_by_quarter(ctx)` |

Factories: `RevenueSummaryApiFactory.get_revenue_summary_api()`, `RevenueSummaryToolFactory.get_revenue_summary_tool()`, `FinancialsFacadeFactory.get_financials_facade()`, `RevenueSummaryTaskFactory.get_revenue_summary_task()`, `FinancialsDaoFactory.get_financials_dao()`.

Presentation:

- REST `POST /api/financials/revenue`
- MCP tool `revenue_summary`

Tool text: read the recorded revenue total for a quarter. Do not estimate a missing quarter. The tool does not modify financial records.

### Proposals

Request: `customer`, `body`, `role`.

Response: `status`, `receipt`, `customer`, `denied`, `message`.

| Layer | Type | Method |
| --- | --- | --- |
| API | `SendProposalApi` | `send_proposal(ctx)` |
| MCP | `SendProposalTool` | `send_proposal(ctx)` |
| Facade | `ProposalFacade` | `send(ctx)` |
| Task | `SendProposalTask` | `execute(ctx)` |
| DAO | `ProposalDao` | `insert_outbox(ctx)` |

Factories: `SendProposalApiFactory.get_send_proposal_api()`, `SendProposalToolFactory.get_send_proposal_tool()`, `ProposalFacadeFactory.get_proposal_facade()`, `SendProposalTaskFactory.get_send_proposal_task()`, `ProposalDaoFactory.get_proposal_dao()`.

Presentation:

- REST `POST /api/proposals/send`
- MCP tool `send_proposal`

Tool text: record a customer proposal in the local outbox. The body carries Customer goal, Proposed scope, Assumptions, and Next steps. Repeated identical proposals reuse the receipt. The tool does not send email.

Send sequence:

1. Facade clears `resp` and checks `send_proposal` access.
2. Facade builds a `CustomerCtx` with the same customer name and the same role, and calls `CustomerFacade.lookup`.
3. Empty customer records or a customer-lookup denial stops the send. `resp.message` is `Unknown customer. Look up the customer before sending.`
4. Facade writes the canonical customer name from the customer record onto `ctx.req.customer`.
5. Facade calls `SendProposalTaskFactory.get_send_proposal_task().execute`.
6. Task calls `ProposalDao.insert_outbox`.
7. DAO computes the receipt as the first 16 hex characters of `sha256(f"{customer}\\0{body}")`, runs `INSERT OR IGNORE`, and sets `resp.status` to `simulated_send`, plus `resp.receipt` and `resp.customer`.

Sales holds both `customer_brief` and `send_proposal`, so the inner customer lookup is allowed for a real send. Engineering and finance fail on step 1.

## Process endpoints

| Endpoint | Purpose |
| --- | --- |
| `GET /health` | Process is up. No domain call. |
| `/mcp` | FastMCP streamable HTTP mount. Tool names: `customer_brief`, `issue_lookup`, `revenue_summary`, `send_proposal`. |

Host bind is localhost. Port comes from `NORTHSTAR_MCP_PORT`, default `8080`.

Example customer call:

```http
POST /api/customer/brief
X-Employee-Role: sales
Content-Type: application/json

{"req": {"customer": "Acme"}, "resp": {}}
```

Success body includes `resp.records[0].id` of `C-101`. A body that sets `req.role` to `finance` while the header says `engineering` is treated as engineering.

## What the middleware leaves to the harness

These teaching behaviors stay out of the domain stacks. Later milestones can add them as their own components. They call this middleware. They do not grow new folders inside `daos/` or `tasks/`.

| Teaching stage | Later home | Design note |
| --- | --- | --- |
| Base agent loop | `harness/agent.py` `build_harness` on `deepagents`, configured by `harness/config.py` `HarnessConfig` | The middleware has no model client. `harness/mcp_client.py` `CompanyMcpClient` calls the MCP server |
| Context | Existing `company/AGENTS.md` and `skills/` | Procedures stay markdown. Skills are not company APIs |
| Actions beyond company tools | Harness middleware (`write_todos`, reviewer subagent, file tools) | Reviewer may call `customer_brief` and may not call `send_proposal` |
| Boundaries | Harness policy in front of the middleware | Human approval before `send_proposal`, protected reference files, model-call limits. Role checks inside this design still run even if a caller skips the harness |
| Persistence of conversations | Harness workspace and checkpoint store | Company SQLite is only customers, issues, revenue, and outbox. Working files under `/work/` and task checkpoints are a different store |

Employee-facing chat, role profile, task history, and approval controls belong to that later interface. The middleware's role header is the contract those controls must set. Production identity is still an authenticated mapping onto `sales`, `engineering`, or `finance`. A header alone is the local demonstration, same as the teaching app's local profiles.

## Checks that define done

When implementation starts, these checks are the contract. They belong with the vertical slice that introduces each rule.

- Sales `customer_brief` for Acme returns `C-101` and the seeded need and contact.
- Engineering `issue_lookup` for Beacon returns `INC-42`.
- Finance `revenue_summary` for `2026-Q3` returns `480000`.
- Finance `revenue_summary` for an unknown quarter returns an empty list.
- Sales `send_proposal` for Acme returns `simulated_send` and a 16-character receipt. The same customer and body return the same receipt and do not add a second outbox row.
- Sales `send_proposal` for an unknown customer returns the unknown-customer message and writes no outbox row.
- Engineering `send_proposal` and finance `issue_lookup` return the access-denial message.
- An unknown role returns the unknown-role message.
- A JSON body role does not override `X-Employee-Role`.
- Import check: `api/` and `mcp_tools/` do not import `daos`, `tasks`, or `common.database`. Facade implementations do not import `daos` or `common.database`. Tasks do not import facades or `common.database`. DAO implementations do not import facades, tasks, or presentation. `ProposalFacadeImpl` may import the customer facade factory.

## Follow-up backlog

The slices below are filed as native GitHub milestones M1–M8 and issues #1–#22. Execution order, gates, and evidence rules are in [SUPERPOWERS_GitIssues_OperatingModel.md](SUPERPOWERS_GitIssues_OperatingModel.md). The empty step log is [SUPERPOWERS_GitIssues_Progress.md](SUPERPOWERS_GitIssues_Progress.md). Each issue names the folders it is allowed to change.

1. Package skeleton under `Middleware/north-start-ecomm-mcp`, FastAPI process, health route, FastMCP mount, singleton and factory conventions.
2. Company database gateway, schema, and seed.
3. Customer vertical slice, closed from `api/` and `mcp_tools/` through the DAO.
4. Issues vertical slice.
5. Financials vertical slice.
6. Proposals vertical slice, including the business-layer customer lookup and idempotent outbox.
7. Access matrix and the header role rule, covered by the checks above.
8. Harness composition on `deepagents` that calls the MCP tools, loads `company/AGENTS.md` and `skills/`, and keeps approval, file workspace, and checkpoints outside the domain folders.

Slices 1–7 are the middleware. Slice 8 is the harness and stays blocked until the tool contracts above are stable. Implementation of any slice waits for a Superpowers implementation plan and red/green tests. These two documents are the design gate.
