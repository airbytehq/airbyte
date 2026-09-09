# Contributing to source-pipedrive

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/). Detailed technical notes live in [AGENTS.md](./AGENTS.md); this file is the short version.

## Connector shape

Manifest-only connector (`manifest.yaml`) with a single custom component, `NullCheckedDpathExtractor`, that tolerates `"data": null` responses. Prefer declarative changes; avoid adding Python for behavior the CDK already provides (error handlers, paginators, filters).

## Error handling

All streams share `definitions.base_error_handler` through `definitions.base_requester`:

| Status | Behavior |
|---|---|
| 401 / 402 / 403 | Fail as `config_error` with Pipedrive's `error` text and a next step (403 may also be a Cloudflare HTML block after rate-limit abuse) |
| 410 | Fail: endpoint permanently removed |
| 429 | Rate limited: wait for `x-ratelimit-reset` (capped at 300s), then exponential backoff, up to 10 retries |
| 500 / 502 / 503 / 504 | Retry with the same backoff |

`deal_products` and `mail` additionally ignore 403/404/410 for a single parent record and keep syncing the remaining parents.

## Rate limits

Pipedrive has a per-token burst limit (20-120 requests per 2s by plan) and a daily token budget. Burst 429s recover after a short wait; daily-budget 429s persist until midnight (server time) and will exhaust retries. Request throttling (`api_budget`) is a separate follow-up.

## Testing

```bash
cd unit_tests && poetry install && poetry run pytest          # mock-server tests for every error filter
airbyte-cdk connector test                                     # manifest validation / connector tests
uvx 'airbyte-cdk[dev]' secrets fetch                           # live creds from GSM into secrets/
```

`integration_tests/invalid_token_config.json` should make `check` fail with the 401 `config_error` message.
