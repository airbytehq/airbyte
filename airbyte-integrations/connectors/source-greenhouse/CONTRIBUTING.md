# Contributing to source-greenhouse

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

This is a declarative connector for Greenhouse Harvest v3. The streams, authentication, and spec live in `manifest.yaml`; `components.py` holds only the state migration that drops the legacy `applied_at` watermark.

## Unique behaviors (summary)

Full technical detail for each item lives in [AGENTS.md](./AGENTS.md).

1. **Partner-Application OAuth With Single-Use Rotating Refresh Tokens** -- Users authorize through Airbyte's registered Greenhouse partner app; the client ID and secret are injected by Airbyte Cloud, never entered by users, so the consent flow is Cloud-only. Refresh tokens rotate on every use and expire after about a day idle, and refresh failures are matched on Greenhouse's `error` code so they surface as a re-authenticate config error.
2. **Cursor Follow-Up Requests Carry No Other Query Parameters** -- Greenhouse rejects any paginated request that combines the cursor with other parameters, so every first-page parameter is guarded with `if not next_page_token`.
3. **Descending Primary-Key Pagination Forces Two-Sided Date Windows** -- Results are ordered by ID, not by cursor field, so incremental requests must send both a lower and an upper date bound or records are silently skipped.
4. **Grouped Substream Routers Pinned to 50 Parent IDs** -- Five child streams batch parent IDs into comma-joined filters capped at 50 by the API, and always read parents over full history.
5. **Fixed-Window Rate Limit Budget With No Published Ceiling** -- Greenhouse publishes no v3 request ceiling, so the connector holds itself to 50 requests per 30-second window shared across all worker threads.
6. **Stream-Specific First-Page Parameters** -- Several streams share an endpoint and differ only by a first-page filter (`custom_field_key`, `show_service_accounts`, `include_defaults`), so removing one changes record counts without an error.

## Testing notes

- Live tests need a fresh Greenhouse refresh token obtained through the Cloud consent flow; because tokens are single-use, a refresh token that has already been exchanged elsewhere fails with `invalid_grant`.
- Unit tests run with `poe test-unit-tests` from the connector directory (see [Developing Connectors Locally](https://docs.airbyte.com/platform/connector-development/local-connector-development)) and cover the pagination, error-classification, and OAuth refresh behavior described above.
