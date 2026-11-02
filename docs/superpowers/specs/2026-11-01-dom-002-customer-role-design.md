# DOM-002 employee role on customer_brief

Issue #5 proves the role rules DESIGN.md already assigns to `customer_brief`. It does not add a second lookup path.

Presentation writes `X-Employee-Role` onto `ctx.req.role` and discards a role in the JSON body. `CustomerFacadeImpl` reads `common/access.py` before `LookupCustomerTask`. A missing role is reported as `unknown`. An unknown role is reported with that role's text. HTTP returns 403 when `resp.denied` is true. The MCP tool returns the same context and does not depend on the HTTP status.

Sales, engineering, and finance may call `customer_brief`. The DAO still filters only on `ctx.req.customer`.
