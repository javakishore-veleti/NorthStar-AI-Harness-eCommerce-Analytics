# DOM-006 proposal denial design

Issue #9 covers the rejection path of `send_proposal` from DESIGN.md. The send sequence from DOM-005 already stops before the task in both cases.

An unknown customer, or a customer lookup that itself is denied, sets `resp.message` to `Unknown customer. Look up the customer before sending.` and returns HTTP 200. `resp.denied` stays false. No outbox row is written.

Engineering and finance fail the `send_proposal` access check before the customer lookup. The response is HTTP 403 with `Access denied: {role} cannot use send_proposal.` A `sales` role in the JSON body does not override an engineering header. The outbox is unchanged.
