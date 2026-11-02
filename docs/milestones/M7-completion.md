# M7 — Harness Agent

Closed 2026-11-02 at `9ef3d5db7646c8f1de9f5c2ed9b6b5ae6a7f57b4`.

## Issues

- [#14](https://github.com/javakishore-veleti/NorthStar-AI-Harness-eCommerce-Analytics/issues/14) HRN-001, closed by [#58](https://github.com/javakishore-veleti/NorthStar-AI-Harness-eCommerce-Analytics/pull/58)
- [#15](https://github.com/javakishore-veleti/NorthStar-AI-Harness-eCommerce-Analytics/issues/15) HRN-002, closed by [#61](https://github.com/javakishore-veleti/NorthStar-AI-Harness-eCommerce-Analytics/pull/61)
- [#16](https://github.com/javakishore-veleti/NorthStar-AI-Harness-eCommerce-Analytics/issues/16) HRN-003, closed by [#64](https://github.com/javakishore-veleti/NorthStar-AI-Harness-eCommerce-Analytics/pull/64)
- [#17](https://github.com/javakishore-veleti/NorthStar-AI-Harness-eCommerce-Analytics/issues/17) HRN-004, closed by [#67](https://github.com/javakishore-veleti/NorthStar-AI-Harness-eCommerce-Analytics/pull/67)
- [#18](https://github.com/javakishore-veleti/NorthStar-AI-Harness-eCommerce-Analytics/issues/18) HRN-005, closed by [#70](https://github.com/javakishore-veleti/NorthStar-AI-Harness-eCommerce-Analytics/pull/70)

## Commands

```bash
cd harness
env -u OPENAI_API_KEY -u ANTHROPIC_API_KEY uv run python -m unittest discover -s tests -q
cd Middleware/north-start-ecomm-mcp
env -u OPENAI_API_KEY -u ANTHROPIC_API_KEY uv run python -m unittest discover -s tests -q
```

## Observed results

Harness suite: 16 tests, OK. Middleware suite: 72 tests, OK. Both ran with provider keys unset.

The harness import graph does not include `daos` or `common.database`. Scripted construction left the silent model call count at 0. Sales tools are `customer_brief` and `send_proposal` only. The reviewer company tool is `customer_brief` only. Reject writes zero outbox rows. Approve against the middleware returns `simulated_send` and one outbox row. A write to `company/AGENTS.md` is denied.

## Remaining risks

These checks do not call a model provider. A live provider run is not part of this gate. SQLite shutdown warnings can still appear.
