# M8 — Persistence and Employee Interface

Closed 2026-11-02 at `9ef3d5db7646c8f1de9f5c2ed9b6b5ae6a7f57b4`.

## Issues

- [#19](https://github.com/javakishore-veleti/NorthStar-AI-Harness-eCommerce-Analytics/issues/19) HRN-006, closed by [#73](https://github.com/javakishore-veleti/NorthStar-AI-Harness-eCommerce-Analytics/pull/73)
- [#20](https://github.com/javakishore-veleti/NorthStar-AI-Harness-eCommerce-Analytics/issues/20) HRN-007, closed by [#76](https://github.com/javakishore-veleti/NorthStar-AI-Harness-eCommerce-Analytics/pull/76)
- [#21](https://github.com/javakishore-veleti/NorthStar-AI-Harness-eCommerce-Analytics/issues/21) HRN-008, closed by [#79](https://github.com/javakishore-veleti/NorthStar-AI-Harness-eCommerce-Analytics/pull/79)
- [#22](https://github.com/javakishore-veleti/NorthStar-AI-Harness-eCommerce-Analytics/issues/22) HRN-009, closed by [#82](https://github.com/javakishore-veleti/NorthStar-AI-Harness-eCommerce-Analytics/pull/82)

## Commands

```bash
cd harness
env -u OPENAI_API_KEY -u ANTHROPIC_API_KEY uv run python -m unittest discover -s tests -q
cd Middleware/north-start-ecomm-mcp
env -u OPENAI_API_KEY -u ANTHROPIC_API_KEY uv run python -m unittest discover -s tests -q
```

## Observed results

Harness suite: 16 tests, OK. Middleware suite: 72 tests, OK.

`proposal.md` is saved under `.runtime/workspace/<task-id>/work/` and that save does not insert an outbox row. The checkpoint file is not the company database. Deleting a task removes its workspace and leaves `C-101`, `C-102`, and `INC-42`.

The employee page host is `127.0.0.1`. Switching the profile to finance changes the role header. Reject leaves the outbox empty. A planted provider key value is not rendered. `curl` to `http://127.0.0.1:8091/` returned `303` to `/tasks/<id>`.

The scripted teaching contract, run through the middleware MCP server, cited `C-101` for sales and did not send, cited `INC-42` and `C-102` for engineering, and cited `2026-Q3` / `480000` for finance. `provider_called` is false. `cost_usd` is 0. `observed_model_output` is null.

## Remaining risks

There is no model transcript. The three prompts are a scripted tool contract, not an observed provider run. The IDE browser opened an error page and could not reach `127.0.0.1:8091`; the page behavior was verified with the test client and with curl. SQLite shutdown warnings can still appear.
