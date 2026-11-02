# DOM-001 customer_brief design

Issue #4 implements the customer slice already specified in [ARCHITECTURE.md](../../../ARCHITECTURE.md) and [DESIGN.md](../../../DESIGN.md). This note records that slice. It does not add a second design.

## In scope

The `customer` domain under `north_start_ecomm_mcp/domains/customer/`, using the folder layout in ARCHITECTURE.md:

- `api/` and `mcp_tools/` call `CustomerFacadeFactory` only
- `dtos/domainReq.py`, `dtos/domainResp.py`, `dtos/domainCtx.py`
- `facades/interfaces/customer_facade.py` with `lookup(ctx)`
- `facades/customer_facade/customer_facade_impl.py` (singleton)
- `facades/customer_facade/tasks/lookup_customer_task.py` with `execute(ctx)`
- `facades/objects_factory.py` with `CustomerFacadeFactory.get_customer_facade()`
- `daos/interfaces.py` with `find_by_name(ctx)`
- `daos/impl/customer_dao_impl.py` (singleton)
- `daos/objects_factory.py` with `CustomerDaoFactory.get_customer_dao()`

Shared pieces named by the architecture:

- `app/http_role.py` turns `X-Employee-Role` into the role string. Presentation writes that string onto `ctx.req.role` and discards a role sent in the body.
- `common/access.py` holds the role matrix from DESIGN.md. `CustomerFacadeImpl` reads it.

Every method from presentation downward takes `CustomerCtx` and returns `CustomerCtx`. The facade replaces `resp` on entry, checks `customer_brief`, then calls `LookupCustomerTask`. The task calls the DAO factory only. The DAO reads `ctx.req.customer` and queries `customers` with `COLLATE NOCASE` through `DatabaseGateway`.

Presentation:

- `POST /api/customer/brief`
- MCP tool `customer_brief`, with the catalog text from DESIGN.md

HTTP returns 403 when `resp.denied` is true and 200 otherwise. MCP returns the same context either way. Denial messages match DESIGN.md. An unknown customer name is HTTP 200 with an empty `resp.records`.

## Out of scope

`issue_lookup`, `revenue_summary`, and `send_proposal` stay unbuilt. `deepagents` stays out of the domain. The composition root does not open the company database; the DAO does, on the first lookup.

## Acceptance

- Sales lookup of Acme returns `C-101`, `Unify weekly sales reporting across three teams`, and `buyer@acme.example`.
- An unknown name returns an empty record list and HTTP 200.
- `tests/closed_layer_audit.py` passes on the new tree.
