# Contributing to source-datadog

For general guidance on contributing to Airbyte connectors, see the
[Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Unique behaviors (summary)

Full technical detail for each item lives in [AGENTS.md](./AGENTS.md), under the same number and title. Keep the two files in step.

1. **Two Keys, One Permission per Stream, No OAuth** -- Datadog offers OAuth only to approved Technology Partners ([Create an API-based integration](https://docs.datadoghq.com/extend/integrations/api_integration/)), so the connector authenticates with an API key and an application key. Each stream needs one permission on the application key, and a 403 names it.
2. **Paging Differs per Endpoint, and `monitors` Has None** -- Every paginated stream sends the largest page size Datadog documents, or the documented default where it states no maximum. `monitors` has no paginator on purpose: without the `page` parameter Datadog returns all monitors in one response ([monitors API](https://docs.datadoghq.com/api/latest/monitors/#get-all-monitor-details)). `incidents` counts its own offset, because the `next_offset` Datadog returns never signals the end.
3. **`logs` and `audit_logs` Send Microsecond Bounds Because the End Bound Is Exclusive** -- Datadog leaves out records at the exact end of a time window, so the monthly windows are sent with microseconds and meet without a gap. Each sync starts one day before the saved state, because Datadog accepts logs up to 18 hours late, and ends at the time of the sync. The other streams are full refresh: their endpoints take no time filter.
4. **Deleted Dashboards and SLOs Come From a Second Request** -- Datadog returns deleted dashboards and SLOs only when asked, so both streams read twice and the connector sets the `deleted` flag itself.
5. **Error Map** -- A 401, the two kinds of 403, a rejected log query, an account without Synthetic Monitoring and an expired `metrics` page cursor each fail with a message that says what to do. Rate limits and server errors are retried, after the wait Datadog gives in `X-RateLimit-Reset`.
6. **Rate Limits Are per Endpoint and Read From Headers** -- Datadog documents no table of limits; each endpoint reports its own in response headers ([rate limits](https://docs.datadoghq.com/api/latest/rate-limits/)). The connector holds one budget per endpoint, read on a small account, and follows the `X-RateLimit-Remaining` header.
7. **Schema Fields Declared From Observed Values** -- Seven fields are in live records and not in Datadog's OpenAPI specs, so their types come from what was observed. `dashboards.is_read_only` was removed in 2.0.0 and is declared again, because the API still sends it.
8. **What Only the Mock Tests Prove** -- The test account is too small to show a second page, a deleted record or most errors, so the mock tests in `unit_tests/mock_server/` are the proof for those. The unit tests pin the CDK version of the base image.
9. **Left for the Next Major Release** -- `incident_teams`, `downtimes`, the missing `synthetic_tests` primary key, untyped timestamp fields and two unused spec fields are known and need a breaking release.

## Testing

Run the tests from the connector directory:

```bash
poe test-unit-tests          # mock tests, no credentials
poe test-integration-tests   # the CDK's standard tests, with secrets/config.json
```

- `unit_tests/pyproject.toml` pins `airbyte-cdk` to the version of the base image in `metadata.yaml`. Bump the two together.
- A unit test that runs longer than 30 seconds ends the whole run without a summary. That is the timeout catching a paginator that never stops.
- The standard tests read every stream except those listed under `empty_streams` in `acceptance-test-config.yml`. Each of those needs a mock test file, and a unit test fails when one is missing.
- `integration_tests/abnormal_state.json` holds a state far in the future for `logs` and `audit_logs`, in the format the cursor writes. A new incremental stream needs a state there.
- `integration_tests/invalid_config.json` holds made-up keys of the right length, so the failed connection test reaches Datadog and gets its 403.
