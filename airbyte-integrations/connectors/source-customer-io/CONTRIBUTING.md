# Contributing to source-customer-io

For general guidance on contributing to Airbyte connectors, see the
[Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Unique behaviors (summary)

Full technical detail for each item lives in [AGENTS.md](./AGENTS.md).

1. **The App API Is API-Key-Only** - every request sends the App API key as a bearer token.
   Customer.io offers OAuth only for its MCP server ([auth.md](https://docs.customer.io/auth.md)),
   so there is no OAuth flow to add. A wrong Region fails with 401 like an invalid key
   ([data centers](https://docs.customer.io/accounts/settings/data-centers/#specifying-your-region-in-the-api)).
   Details in AGENTS.md section 1.
2. **HTTP Errors Are Classified on the Shared Base Requester** - 401 and 403 fail as configuration
   errors that name the fix; 429 waits for `Retry-After`
   ([API rate limits](https://docs.customer.io/integrations/api/customerio-apis/#api-rate-limits)),
   or backs off exponentially when the header is absent, for at most 30 retries; 5xx retry; a 404
   on `listCampaignActions` (an automation deleted mid-sync) skips that automation; anything else
   follows the CDK default mapping. Details in AGENTS.md section 2.
3. **One Shared Request Budget and Three Workers** - `api_budget` allows 10 requests per second
   ([rate limits](https://docs.customer.io/integrations/api/app/#rate-limits)), the App API limit
   shared by the whole workspace (`components.responses.InboxPreviewReadRateLimited` in the
   [OpenAPI spec](https://docs.customer.io/files/journeys-app.json)), and `concurrency_level` runs
   3 workers. Details in AGENTS.md section 3.
4. **Incremental Sync Is Client-Side With a One-Hour Lookback** - no list endpoint filters by time
   ([OpenAPI spec](https://docs.customer.io/files/journeys-app.json)), so every sync reads the full
   lists and keeps records whose `updated` (epoch seconds) is at or after the saved cursor minus
   one hour, so Incremental | Append stores the last hour's records again on every sync. A new
   campaign's actions start from the stream-wide cursor, not the Start Date. Details in AGENTS.md
   section 4.
5. **`campaigns_actions.id` Is a JSON String** - the
   [OpenAPI spec](https://docs.customer.io/files/journeys-app.json) documents an integer; joins
   with `campaigns.actions[].id` need a cast. Details in AGENTS.md section 5.
6. **`campaigns_actions` Logs a Harmless Parent-State Warning** - "Parent state handling is not
   supported for CartesianProductStreamSlicer." comes from the one-element `partition_router` list
   and needs no action. Details in AGENTS.md section 6.
7. **Four `campaigns` Fields Are Untyped** - `audience.person_filters`,
   `audience.relationship_filters`, `object_attribute_triggers` and `relationship_attribute_triggers`
   are typed `object` in the [OpenAPI spec](https://docs.customer.io/files/journeys-app.json), but
   every example there is a JSON string and no live record shows them, so the schema leaves them
   untyped. Details in AGENTS.md section 7.

## Testing notes

- From the connector directory, `poe test-unit-tests` runs the requests-mock tests in
  `unit_tests/`, and `airbyte-cdk connector test` runs the standard tests against
  `secrets/config.json`.
- `integration_tests/invalid_config.json` holds an invalid key with a past Start Date, so the
  failed check exercises the 401 message. There is no `expected_records.jsonl`: the sandbox data
  changes and no current harness asserts on it.
