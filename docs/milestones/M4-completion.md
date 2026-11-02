# M4 — Proposals Domain

Closed 2026-11-02 at `9ef3d5db7646c8f1de9f5c2ed9b6b5ae6a7f57b4`.

## Issues

- [#8](https://github.com/javakishore-veleti/NorthStar-AI-Harness-eCommerce-Analytics/issues/8) DOM-005, closed by [#40](https://github.com/javakishore-veleti/NorthStar-AI-Harness-eCommerce-Analytics/pull/40)
- [#9](https://github.com/javakishore-veleti/NorthStar-AI-Harness-eCommerce-Analytics/issues/9) DOM-006, closed by [#43](https://github.com/javakishore-veleti/NorthStar-AI-Harness-eCommerce-Analytics/pull/43)

## Commands

```bash
cd Middleware/north-start-ecomm-mcp
env -u OPENAI_API_KEY -u ANTHROPIC_API_KEY uv run python -m unittest discover -s tests -q
```

## Observed results

72 tests, OK. A repeated identical proposal reuses one receipt and returns `simulated_send`. An unknown customer writes no outbox row. An engineering send is denied and leaves the outbox unchanged. The middleware does not send email.

## Remaining risks

None beyond the shared SQLite shutdown warning noted in M1.
