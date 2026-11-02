# Contributing to source-youtube-analytics

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Unique behaviors (summary)

Full technical detail for each item lives in [AGENTS.md](./AGENTS.md).

1. **Three-Level Job → Report → CSV Download Model** — Report streams use YouTube-generated CSV files, and the first sync can create reporting jobs before data is available. Values are converted to the types in each stream's schema, every page of the job and report lists is read, and a report file that is no longer available is skipped instead of failing the sync.
2. **Incremental Cursor Lives on the Parent `report` Stream** — Incremental syncs follow when YouTube created each report file, so corrected reports for older dates can still be picked up. Each report stream separately tracks the date contained in its rows.
3. **Shared Quota and Per-Stream Request Fan-Out** — Every selected report stream makes its own job and report requests and downloads its files, which increases quota use. You can set how many files download in parallel, but all downloads share one request limit. Cloud connections share Airbyte's YouTube API project quota.
4. **Error Mapping Depends on the Response Path** — Rejected credentials, a missing YouTube channel, denied access, and an invalid refresh token each produce a different error. The detailed guide explains what to check for each case.
5. **Content Owner Parameter and Static Extra Request Parameters** — You can optionally retrieve data on behalf of a YouTube content owner. Keep request settings static where required so YouTube receives valid values.
6. **Two Chained State Migrations** — Existing connections may have older saved progress that must be carried forward in order. The migration preserves report progress while allowing newly issued corrections to arrive.

## Testing

From `unit_tests/`, install dependencies with `poetry install --no-root` and run the unit tests with `poetry run pytest -x`. The connection check uses `report_types` because it can validate credentials without requiring a reporting job. Acceptance tests use the GSM secret `SECRET_YOUTUBE-ANALYTICS_CREDS`.
