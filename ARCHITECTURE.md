# Architecture

NorthStar company operations live in one middleware app, `north-start-ecomm-mcp`. The app replaces the flat teaching layout of [ns-work-harness](https://github.com/aishwaryanr/awesome-generative-ai-guide/tree/main/youtube/code/ns-work-harness) with a closed layer stack inside each business domain.

This document is the structure. Behavior, payloads, and access rules are in [DESIGN.md](DESIGN.md). No domain code is in the repo yet. The build order is filed as GitHub milestones M1–M8 and issues #1–#22, with the method in [SUPERPOWERS_GitIssues_OperatingModel.md](SUPERPOWERS_GitIssues_OperatingModel.md).

## What this repo is

NorthStar sells data-integration and dashboard-onboarding services. NS Work is the internal harness employees use to look up customers, triage issues, read a revenue quarter, and record a proposal in a local outbox.

The teaching repo puts that behavior in a handful of top-level Python files (`company.py`, `tools/*.py`, `agent.py`, `server.py`). This repo keeps the same company facts and the same four operations, and places each operation in a domain module whose subfolders are closed layers.

`deepagents` is a dependency of the harness project in `harness/`. It is the agent library for the harness composition root. It is not imported by domain layers. The middleware exposes company operations. The harness process calls those operations.

## Closed layers

Each domain uses the same closed stack. A layer calls only the layer directly below it.

| Order | Layer | Domain subfolder | May call |
| --- | --- | --- | --- |
| 1 | Presentation | `api/`, `mcp_tools/` | Business facade factory only |
| 2 | Business | `facades/` | Its own task factory, and another domain's business facade factory when a use case needs it |
| 3 | Services | `facades/<facade-name>/tasks/` | That domain's DAO factory only |
| 4 | Persistence | `daos/` | The database gateway only |
| 5 | Database | `common/database.py` | SQLite only |

Closed means a caller cannot skip a subfolder. Presentation does not call a task, a DAO, or SQL. A facade does not call a DAO. A task does not call SQL and does not call a facade. A DAO does not call a facade or a task.

The textbook diagram that marks the services layer OPEN does not apply inside these domains. Services stay closed here. A facade always enters its task. The task always enters its DAO.

DTOs and factories are not layers. Every layer may read and write the domain context object. Each layer from presentation through persistence is a singleton class. The caller obtains that class from the layer's `objects_factory` and does not construct the implementation.

`common/` is shared infrastructure, not a domain:

- `common/singleton.py` — metaclass for presentation implementations, task implementations, facade implementations, DAO implementations, and the database gateway
- `common/database.py` — the database layer
- `common/access.py` — role-to-operation matrix, read by business facades

The composition root, `app/main.py`, may construct the database gateway at process start. That wiring is outside the domain stacks.

## Runtime shape

One process serves both HTTP APIs and MCP tools.

- FastAPI is the HTTP server.
- FastMCP (`fastmcp`) provides the MCP tools.
- The MCP ASGI app is mounted on FastAPI at `/mcp`, and FastAPI uses the MCP lifespan so sessions initialize.
- Uvicorn serves the process on localhost.

Presentation modules are the only place that reads the employee role. The role arrives on the `X-Employee-Role` header. The presentation layer writes that value onto the context and then calls the facade with the context alone. A role field sent in the JSON body is overwritten. The model does not assign its own role.

## Domain modules

Four domains match the company operations in the teaching harness.

| Domain | Teaching source | Operation |
| --- | --- | --- |
| `customer` | `tools/customer.py` | `customer_brief` |
| `issues` | `tools/issues.py` | `issue_lookup` |
| `financials` | `tools/revenue.py` | `revenue_summary` |
| `proposals` | `tools/proposals.py` | `send_proposal` |

`financials` is the domain name. `revenue_summary` stays the operation name so harness callers keep a stable tool name.

## Folder layout

The app directory name is `north-start-ecomm-mcp`. The importable package is `north_start_ecomm_mcp` because a Python package name cannot contain a hyphen. The presentation folder is `mcp_tools` for the same reason.

```text
Middleware/north-start-ecomm-mcp/
  north_start_ecomm_mcp/
    app/
      main.py                  # FastAPI composition root
      mcp_server.py            # FastMCP registration
      http_role.py             # header -> context role
    common/
      singleton.py
      database.py
      access.py
    domains/
      customer/
        api/
          objects_factory.py
          interfaces.py
          impl/
            customer_brief_api_impl.py
        mcp_tools/
          objects_factory.py
          interfaces.py
          impl/
            customer_brief_tool_impl.py
        dtos/
          domainReq.py
          domainResp.py
          domainCtx.py
        facades/
          objects_factory.py
          interfaces/
            customer_facade.py
          customer_facade/
            customer_facade_impl.py
            tasks/
              objects_factory.py
              interfaces.py
              impl/
                lookup_customer_task_impl.py
        daos/
          objects_factory.py
          interfaces.py
          impl/
            customer_dao_impl.py
      issues/
        api/
          objects_factory.py
          interfaces.py
          impl/
            issue_lookup_api_impl.py
        mcp_tools/
          objects_factory.py
          interfaces.py
          impl/
            issue_lookup_tool_impl.py
        dtos/
          domainReq.py
          domainResp.py
          domainCtx.py
        facades/
          objects_factory.py
          interfaces/
            issue_facade.py
          issue_facade/
            issue_facade_impl.py
            tasks/
              objects_factory.py
              interfaces.py
              impl/
                lookup_issue_task_impl.py
        daos/
          objects_factory.py
          interfaces.py
          impl/
            issue_dao_impl.py
      financials/
        api/
          objects_factory.py
          interfaces.py
          impl/
            revenue_summary_api_impl.py
        mcp_tools/
          objects_factory.py
          interfaces.py
          impl/
            revenue_summary_tool_impl.py
        dtos/
          domainReq.py
          domainResp.py
          domainCtx.py
        facades/
          objects_factory.py
          interfaces/
            financials_facade.py
          financials_facade/
            financials_facade_impl.py
            tasks/
              objects_factory.py
              interfaces.py
              impl/
                revenue_summary_task_impl.py
        daos/
          objects_factory.py
          interfaces.py
          impl/
            financials_dao_impl.py
      proposals/
        api/
          objects_factory.py
          interfaces.py
          impl/
            send_proposal_api_impl.py
        mcp_tools/
          objects_factory.py
          interfaces.py
          impl/
            send_proposal_tool_impl.py
        dtos/
          domainReq.py
          domainResp.py
          domainCtx.py
        facades/
          objects_factory.py
          interfaces/
            proposal_facade.py
          proposal_facade/
            proposal_facade_impl.py
            tasks/
              objects_factory.py
              interfaces.py
              impl/
                send_proposal_task_impl.py
        daos/
          objects_factory.py
          interfaces.py
          impl/
            proposal_dao_impl.py
```

The same pattern is mandatory in every domain. A new operation adds a task and a DAO method behind the existing facade. It does not add a shortcut from `api/` to `daos/`.

## Objects that cross the layers

### Context only

From the API class and the MCP tool class downward, every domain method takes one argument, the domain context, and returns that same context. Methods do not take `customer`, `quarter`, `body`, or `role` as their own parameters. The API method may also take the `X-Employee-Role` header so it can write `req.role` before the facade call. The MCP method reads that header inside the method.

The context type lives in `dtos/domainCtx.py`. It holds two members:

- `req` from `dtos/domainReq.py`
- `resp` from `dtos/domainResp.py`

Callers fill `req`. The stack fills `resp`. The business facade replaces `resp` at the start of each call so a client cannot submit finished records.

The database gateway is the exception that ends the chain. DAO methods still accept only the domain context. Inside the DAO, the implementation reads fields from `ctx.req` and passes SQL text and bound parameters to the gateway. Domain code above the DAO never sees SQL.

### Singletons and factories

Presentation implementations, task implementations, facade implementations, DAO implementations, and the database gateway are singletons. One process holds one instance of each.

Each domain has:

- `api/objects_factory.py` — static methods that return the API interface.
- `mcp_tools/objects_factory.py` — static methods that return the MCP tool interface.
- `facades/<facade-name>/tasks/objects_factory.py` — static methods that return the task interface.
- `facades/objects_factory.py` — static methods that return the facade interface.
- `daos/objects_factory.py` — static methods that return the DAO interface.

The factory method constructs the singleton implementation and types the return as the interface. Callers depend on the factory and the interface. They do not instantiate `*Impl` classes. A module-level function is not a domain operation.

### Cross-domain calls

`send_proposal` must know that the customer exists and must store the canonical customer name. That check stays on the business layer. `ProposalFacadeImpl` builds a `CustomerCtx`, calls `CustomerFacadeFactory`, and reads the customer response. It then calls `SendProposalTask` with the proposal context.

`SendProposalTask` calls `ProposalDao` only. It does not call the customer facade or the customer DAO. No task reaches into another domain.

## Company data

One SQLite file is the company database. The path comes from `NORTHSTAR_COMPANY_DB`, otherwise `Middleware/north-start-ecomm-mcp/.runtime/company.db`. Schema creation and seed rows run when the database singleton is first constructed. Tables match the teaching harness: `customers`, `issues`, `revenue`, `outbox`.

Reads use a read-only connection. The proposal DAO uses a write connection for the outbox insert. The outbox is a local record. The middleware does not send email.

## Where the teaching files go

| Teaching file | Enterprise home |
| --- | --- |
| `tools/customer.py`, `tools/issues.py`, `tools/revenue.py`, `tools/proposals.py` | Domain presentation (`mcp_tools/` and `api/`) plus the stack below |
| `tools/binding.py` | Presentation role binding plus the business access check |
| `company.py` data and seed | `common/database.py` and the four DAOs |
| `company.py` `ACCESS` | `common/access.py`, enforced in facades |
| `company/AGENTS.md`, `skills/` | Already in this repo. Harness context for a later agent process. Stays out of domain folders |
| `agent.py`, `stages.py` | `harness/agent.py` `build_harness` and `harness/stages.py` `company_context`. Uses `deepagents`. Calls this middleware |
| `server.py`, `web/` | Later employee interface. Separate from the middleware process described here |
| `workspace.py` | Later harness working files. Separate from the company SQLite file |
| Human approval before send | `harness/approval.py` `SendApproval`. Reject does not call the middleware. Approve calls `send_proposal`. The middleware records the outbox row. There is no email transport |

`harness/config.py` `HarnessConfig` holds the repo root, the middleware MCP URL, and the role chosen by application code. Provider credential values stay in `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`. `harness/mcp_client.py` `CompanyMcpClient` calls the middleware MCP server. The harness does not import DAO implementations or `common.database`.

`build_harness` binds the employee role from `HarnessConfig` before the model is invoked and passes only that role's tools. The model has no role argument. The middleware access matrix still denies a direct call that skips the harness filter.

`reviewer_subagent` may call `customer_brief` and may not call `send_proposal`. Its model-call limit is separate from the parent limit in `parent_middleware`. `disable_general_purpose_delegate` leaves the automatic general-purpose delegate off.

## Delivery method

Implementation of this architecture follows the Superpowers methodology: a written design (these documents), then an implementation plan, then red/green tests, then the layer code. `deepagents` stays the agent library for the later harness work. Domain milestones do not start by editing `agent.py`.

GitHub milestones M1–M8 slice the teaching walkthrough (context, actions, boundaries, persistence) into work that lands in the layers above, not into a second copy of the flat teaching modules. Issue status is tracked in [SUPERPOWERS_GitIssues_Progress.md](SUPERPOWERS_GitIssues_Progress.md).
