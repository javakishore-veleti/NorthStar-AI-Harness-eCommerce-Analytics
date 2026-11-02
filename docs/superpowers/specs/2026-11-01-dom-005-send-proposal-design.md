# DOM-005 send_proposal design

Issue #8 adds the proposals domain from ARCHITECTURE.md and DESIGN.md. The operation name stays `send_proposal`. The call path matches the other domains, with one business-layer exception: `ProposalFacadeImpl` may import the customer facade factory.

`POST /api/proposals/send` and MCP tool `send_proposal` take `ProposalCtx`. The request holds `customer`, `body`, and `role`. The response holds `status`, `receipt`, `customer`, `denied`, and `message`. The facade replaces `resp`, checks `send_proposal`, looks up the customer, copies the canonical name, then calls `SendProposalTask`. The task calls `ProposalDao.insert_outbox`. The receipt is the first 16 hex characters of `sha256(customer + NUL + body)`. The insert is `INSERT OR IGNORE`. Success sets `resp.status` to `simulated_send`.

Sales send for Acme returns `simulated_send`, the canonical customer name, and a 16-character receipt. The same customer and body returns the same receipt and does not add a second outbox row. The tool records a local outbox row. It does not send email.
