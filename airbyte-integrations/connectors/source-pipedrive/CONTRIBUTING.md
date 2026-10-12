# Contributing to source-pipedrive

For general guidance on contributing to Airbyte connectors, see the
[Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Unique behaviors (summary)

Full technical detail for each item lives in [AGENTS.md](./AGENTS.md).

1. **Core Streams Read API v2 Entity Endpoints; Nothing Reads Recents Any More** -- `deals`,
   `deals_archived`, `persons`, `organizations`, `activities` and `products` read `api/v2/...` with
   cursor pagination and the inclusive `updated_since` filter; `notes` and `leads` use the same
   filter on API v1, `files` re-reads its list and filters client-side, and all three page in `id`
   order with a one-hour lookback so an edit during a read cannot skip a row. `leads_archived` reads
   the archived leads `GET /v1/leads` leaves out; `deal_products` asks for 100 deals per request;
   `product_variations` expands every product regardless of the Start Date; `goals` asks once per
   assignee type, because without one Pipedrive returns only the token owner's goals. `pipelines`,
   `stages`, `filters` and `users` are full refresh on purpose. The base URL stays
   `https://api.pipedrive.com/` with `v1/...` and `api/v2/...` paths; several v1 endpoints 404 under
   `/api/v1/`. Archived deals are a separate stream because a cached parent must not have a
   multi-value partition router. Details in AGENTS.md section 1.
2. **API v2 Records Nest Custom Fields and Carry `is_deleted`** -- custom fields live under the
   nullable `custom_fields` object and schemas keep `additionalProperties: true`; tightening them
   drops every custom field. Lead custom fields arrive as top-level hash keys (API v1), the only
   undeclared fields a read returns, hence `fail_on_extra_columns: false`. `components.py` is gone;
   plain `DpathExtractor` on `data` is correct. Details in AGENTS.md section 2.
3. **Date Fields Are Typed to Their Actual Shape** -- RFC3339 values (API v2, `leads`, `lead_labels`)
   are `date-time` + `timestamp_with_timezone`; `YYYY-MM-DD HH:MM:SS` values (API v1) are `date-time` +
   `timestamp_without_timezone`; `HH:MM` fields such as `activities.due_time`, and
   `deal_flow.old_value`/`new_value` (they take the type of whichever field changed), stay untyped.
   Adding or changing a `format` is a breaking change, so the date-like fields listed in AGENTS.md
   wait for the next major release. Declared JSON types follow Pipedrive's OpenAPI; the differences
   kept on purpose (whole-value `integer` flags and epoch milliseconds, five `goals` ids declared
   `number`, two arrays without `items`, `deal_fields.show_in_pipelines`) and the three fields whose
   values really vary in kind (`deal_fields.mandatory_flag`, `deal_flow.additional_data`,
   `options[].id`) are listed with their reasons there. A type change is a breaking change. Details
   in AGENTS.md section 3.
4. **The API Token Travels in the `x-api-token` Header** -- one `ApiKeyAuthenticator` on
   `base_requester`, as Pipedrive's authentication guide and OpenAPI document; never put the token in
   `request_parameters`. The token scopes every stream to one user's visibility. OAuth is planned in
   [airbytehq/airbyte#85773](https://github.com/airbytehq/airbyte/pull/85773). Details in AGENTS.md
   section 4.
5. **Mail Streams Are Scoped to One User's Mailbox and Fan Out per Folder and Thread** --
   `mailThreads` queries four folders (so threads can repeat) and `mail` makes one request per
   thread; both only see the token owner's mailbox. `mailThreads` keeps `use_cache: false` because
   concurrent folder partitions corrupt the CDK's cached-parent sqlite file. Details in AGENTS.md
   section 5.
6. **HTTP Errors Are Classified on the Shared Base Requester** -- every status code Pipedrive
   documents is mapped, with its vendor meaning, in AGENTS.md: 401/402/403/415 fail as configuration
   errors, 410/501 as system errors, 429 waits on `x-ratelimit-reset`, 5xx retry through the CDK
   default. Message templates survive any body and cap Pipedrive's text at 300 characters. Child
   streams skip a single deleted or hidden parent; plan-gated streams return no records when Pipedrive
   reports the feature as unavailable; Cloudflare's HTML 403 and statuses the CDK default mapping
   lacks always reach the shared handler. Per-stream handlers must be a `CompositeErrorHandler` that
   falls through to `base_error_handler`. Details in AGENTS.md section 6.
7. **One Shared Request Budget and a Small Thread Pool** -- `api_budget` throttles every stream to
   20 requests per rolling 2 seconds (Pipedrive's lowest-plan burst limit, matched by URL path so
   OAuth company hosts are covered too) and drains on a zero `x-ratelimit-remaining`; the daily token
   budget is per company and not modeled. `num_workers` runs 2 to 10 streams in parallel (default 3;
   a saved 1 runs as 2, a saved value above 10 is lowered to 10). The section also derives
   `maxSecondsBetweenMessages`. Details in AGENTS.md section 7.
8. **Deletions Are Replicated for Deals and Projects** -- `deals` and `deals_archived` request
   `status=open,won,lost,deleted` and emit deals deleted in the last 30 days with `is_deleted: true`;
   `projects` requests every documented status, so deleted projects arrive with `status: deleted`. No
   other stream replicates deletions. Details in AGENTS.md section 8.
9. **Every List Endpoint's Pagination Is Recorded** -- v2 lists page by cursor at 500, v1 lists by
   offset at the largest size each endpoint serves (500, `files` 100, `call_logs` and `mailThreads`
   50), and nine short v1 lists are unpaginated. Re-check the reference and one live request before
   changing a `limit`. Details in AGENTS.md section 9.

## Testing notes

- Validate manifest changes with `airbyte-cdk connector test` from the connector directory;
  mock-server unit tests live in `unit_tests/` and run with `poetry run pytest` from that directory.
  The unit-test lock pins the same CDK as the base image; bump both together.
- `integration_tests/` holds the acceptance test config. `expected_records.jsonl` mirrors a
  specific sandbox account, so record-level assertions need an updated fixture when the sandbox
  data changes. The sandbox's daily token budget is small (`x-daily-ratelimit-token-limit` has read
  30,000 and 99,999 on different days) and is shared by every API token, OAuth app and CI run in the
  company, so do not run several full reads in parallel.
- The sandbox has no mail connection, phone integration, Projects suite, legacy Teams, installments,
  product variations or archived leads; those streams are declared empty with reasons and covered by
  mock-server tests.
- Custom field keys are account-specific; don't hard-code hash keys in tests or schemas.
