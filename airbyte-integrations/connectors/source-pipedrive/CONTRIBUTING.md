# Contributing to source-pipedrive

For general guidance on contributing to Airbyte connectors, see the
[Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Unique behaviors (summary)

Full technical detail for each item lives in [AGENTS.md](./AGENTS.md).

1. **Incremental Streams Read From the Recents Endpoint, Not the Entity Endpoints** -- the ten
   incremental streams poll `/v1/recents` for anything modified since the start date, so they
   pick up edits to old records but never see untouched records created before the start date.
   Pipedrive caps the Recents endpoint at one month of history, so older records are never
   backfilled. The other sixteen streams are full refresh and ignore the start date, except
   `deal_products`, which only expands the deals returned by `deals`.
2. **Null-Payload Records From Recents Are Kept as Tombstones** -- when Pipedrive returns a
   `null` payload for a recent item, the connector emits a sparse record with just `id` and
   `item` instead of failing; don't filter these out or swap the custom extractor without
   checking with users.
3. **Custom Fields Arrive as Hash Keys Outside the Declared Schema** -- custom fields show up
   as 40-character hash keys that only pass through because schemas allow additional
   properties; tightening the schemas would silently drop them.
4. **Authentication Is a Query Parameter, Not an Authenticator** -- the API token rides in
   the URL and scopes every stream to one user's visibility. OAuth is owned by
   [airbyte-internal-issues#17201](https://github.com/airbytehq/airbyte-internal-issues/issues/17201);
   don't add or document it early.
5. **Mail Streams Are Scoped to One User's Mailbox and Fan Out per Folder and Thread** --
   `mailThreads` queries four folders (so threads can repeat) and `mail` makes one request per
   thread; both only see the token owner's mailbox.
6. **HTTP Errors Are Classified on the Shared Base Requester** -- 401/402/403 fail as
   configuration errors carrying Pipedrive's `error` text, 410 fails as a system error, 429 waits on
   `x-ratelimit-reset` then backs off, 5xx retry; `deal_products` and `mail` skip a single
   inaccessible or deleted parent instead of failing the sync. Details in AGENTS.md section 6.
7. **One Shared Request Budget and a Small Thread Pool** -- `api_budget` throttles every stream to
   20 requests per rolling 2 seconds (Pipedrive's lowest-plan burst limit, matched by URL path so
   OAuth company hosts are covered too) and `concurrency_level` runs `num_workers` streams in
   parallel (default 3, max 10). Details in AGENTS.md section 7.
8. **Deletes Are Not Replicated** -- deleted Pipedrive records stay in destinations until the
   stream is cleared. Any change here comes with the API v2 migration in
   [airbyte-internal-issues#17204](https://github.com/airbytehq/airbyte-internal-issues/issues/17204).

## Testing notes

- Validate manifest changes with `airbyte-cdk connector test` from the connector directory;
  mock-server unit tests live in `unit_tests/` and run with `poe test-unit-tests`.
- `integration_tests/` holds the acceptance test config. `expected_records.jsonl` mirrors a
  specific sandbox account, so record-level assertions need an updated fixture when the
  sandbox data changes.
- Custom field keys are account-specific; don't hard-code hash keys in tests or schemas.
