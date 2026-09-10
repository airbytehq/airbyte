# Contributing to source-pipedrive

For general guidance on contributing to Airbyte connectors, see the
[Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Unique behaviors (summary)

1. **Core entities use API v2** -- `deals`, `persons`, `organizations`, `activities`, and `products`
   use `api/v2/...` paths on the bare `https://api.pipedrive.com/` base, with inclusive server-side
   `updated_since` and cursor pagination. `notes` and `files` use v1 list endpoints with client-side
   filtering; pipelines, stages, filters, and users are full refresh. v1 leads, lead labels, lead
   sources, goals, and mailbox endpoints only work under the bare host; do not move the base to `/api/`.
2. **API v2 custom fields are nested** -- custom fields are under `custom_fields`, and schemas retain
   `additionalProperties: true` for account-specific hash keys.
3. **Authentication is a query parameter, not an authenticator** -- every stream injects
   `api_token`; do not add OAuth here.
4. **Mail streams are scoped to one user's mailbox** -- `mailThreads` fans out by folder and `mail`
   fans out by thread.
5. **HTTP errors use the shared base handler** -- per-stream handlers must be CompositeErrorHandler
   entries ending in `#/definitions/base_error_handler`.
6. **One shared request budget and a small thread pool** -- keep `api_budget` and `concurrency_level`
   behavior unchanged.
7. **Deletions** -- deleted deals are emitted for 30 days with `is_deleted: true`; other streams do not
   replicate deletions.

Fields containing only `HH:MM` values are intentionally untyped, including activity `due_time` and
any equivalent time-only fields. Verify API values before adding date or time formats.

## Testing notes

- Validate manifest changes with `airbyte-cdk connector test` from the connector directory.
- Mock-server unit tests live in `unit_tests/` and run with `poetry run pytest unit_tests/ -x`.
- `integration_tests/` holds the acceptance test config and sandbox-specific expected records.
- Custom field keys are account-specific; don't hard-code hash keys in tests or schemas.
