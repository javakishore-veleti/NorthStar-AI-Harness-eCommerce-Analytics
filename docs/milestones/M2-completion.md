# M2 — Customer Domain

Closed 2026-11-02 at `9ef3d5db7646c8f1de9f5c2ed9b6b5ae6a7f57b4`.

## Issues

- [#4](https://github.com/javakishore-veleti/NorthStar-AI-Harness-eCommerce-Analytics/issues/4) DOM-001, closed by [#30](https://github.com/javakishore-veleti/NorthStar-AI-Harness-eCommerce-Analytics/pull/30)
- [#5](https://github.com/javakishore-veleti/NorthStar-AI-Harness-eCommerce-Analytics/issues/5) DOM-002, closed by [#32](https://github.com/javakishore-veleti/NorthStar-AI-Harness-eCommerce-Analytics/pull/32)

## Commands

```bash
cd Middleware/north-start-ecomm-mcp
env -u OPENAI_API_KEY -u ANTHROPIC_API_KEY uv run python -m unittest discover -s tests -q
```

## Observed results

72 tests, OK. A sales lookup of Acme returns `C-101`. The `X-Employee-Role` header wins over a role planted in the JSON body. An unknown role is denied.

## Remaining risks

None beyond the shared SQLite shutdown warning noted in M1.
