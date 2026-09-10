# Contributing to source-pipedrive

For general guidance on contributing to Airbyte connectors, see the
[Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Unique behaviors (summary)

Full technical detail for each item lives in [AGENTS.md](./AGENTS.md).

1. **Core Streams Read API v2 Entity Endpoints; Nothing Reads Recents Any More** -- `deals`,
   `deals_archived`, `persons`, `organizations`, `activities` and `products` read `api/v2/...` with
   cursor pagination and the inclusive `updated_since` filter; `notes` and `leads` use the same
   filter on API v1; `files` re-reads its list and filters client-side; `deal_flow` filters each
   deal's change history client-side on `log_time`. `pipelines`, `stages`, `filters` and `users` are
   full refresh on purpose: the v2 pipelines/stages endpoints have no `updated_since` parameter
   (HTTP 400 if sent) and v1 filters/users are short unpaginated lists. The base URL stays
   `https://api.pipedrive.com/` with `v1/...` and `api/v2/...` paths; several v1 endpoints 404 under
   `/api/v1/`. Archived deals are a separate stream because a cached parent must not have a
   multi-value partition router. Details in AGENTS.md section 1.
2. **API v2 Records Nest Custom Fields and Carry `is_deleted`** -- custom fields live under the
   nullable `custom_fields` object and schemas keep `additionalProperties: true`; tightening them
   drops every custom field. `components.py` is gone; plain `DpathExtractor` on `data` is correct.
   Details in AGENTS.md section 2.
3. **Date Fields Are Typed to Their Actual Shape** -- RFC3339 values (API v2, `leads`, `lead_labels`)
   are `date-time` + `timestamp_with_timezone`; `YYYY-MM-DD HH:MM:SS` values (API v1) are `date-time`
   + `timestamp_without_timezone`; `HH:MM` fields such as `activities.due_time` stay untyped. Adding
   or changing a `format` is a breaking change. Details in AGENTS.md section 3.
4. **Authentication Is a Query Parameter, Not an Authenticator** -- the API token rides in the URL
   and scopes every stream to one user's visibility. OAuth is owned by
   [airbyte-internal-issues#17201](https://github.com/airbytehq/airbyte-internal-issues/issues/17201);
   don't add or document it early. Details in AGENTS.md section 4.
5. **Mail Streams Are Scoped to One User's Mailbox and Fan Out per Folder and Thread** --
   `mailThreads` queries four folders (so threads can repeat) and `mail` makes one request per
   thread; both only see the token owner's mailbox. Details in AGENTS.md section 5.
6. **HTTP Errors Are Classified on the Shared Base Requester** -- 401/402/403 fail as
   configuration errors carrying Pipedrive's `error` text, 410 fails as a system error, 429 waits on
   `x-ratelimit-reset` then backs off, 5xx retry; `deal_products`, `deal_flow` and `mail` skip a
   single inaccessible or deleted parent instead of failing the sync; `legacy_teams`, `projects`,
   `tasks`, `deal_installments` and `permission_set_assignments` return no records when Pipedrive
   reports the feature as unavailable (402/403, plus 404/410 where the endpoint may be retired).
   Per-stream handlers must be a `CompositeErrorHandler` that falls through to the shared
   `base_error_handler`. Details in AGENTS.md section 6.
7. **One Shared Request Budget and a Small Thread Pool** -- `api_budget` throttles every stream to
   20 requests per rolling 2 seconds (Pipedrive's lowest-plan burst limit, matched by URL path so
   OAuth company hosts are covered too) and `concurrency_level` runs `num_workers` streams in
   parallel (default 3, max 10). Details in AGENTS.md section 7.
8. **Deletions Are Replicated for Deals Only** -- `deals` and `deals_archived` request
   `status=open,won,lost,deleted` and emit deals deleted in the last 30 days with `is_deleted: true`;
   no other stream replicates deletions, and `is_deleted` on other records is passed through as
   returned. Details in AGENTS.md section 8.

## Testing notes

- Validate manifest changes with `airbyte-cdk connector test` from the connector directory;
  mock-server unit tests live in `unit_tests/` and run with `poetry run pytest` from that directory.
- `integration_tests/` holds the acceptance test config. `expected_records.jsonl` mirrors a
  specific sandbox account, so record-level assertions need an updated fixture when the sandbox
  data changes; the sandbox's daily request budget (30,000 tokens) is small, so do not run several
  full reads in parallel.
- Custom field keys are account-specific; don't hard-code hash keys in tests or schemas.
