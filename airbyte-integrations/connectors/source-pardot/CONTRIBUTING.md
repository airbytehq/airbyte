# Contributing to source-pardot

For general guidance on contributing to Airbyte connectors, see the
[Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Unique behaviors (summary)

Full technical detail for each item lives in [AGENTS.md](./AGENTS.md), under the same number and title. Keep the two files in step.

1. **Errors Are Matched on the Vendor's Code in the Body** - The vendor documents no HTTP status per error code, so the filters read `code` (version 5) or `@attributes.err_code` (version 4, `email_clicks`). Codes 184, 201 and 49 fail at once and say what to fix; code 49 names the ability the stream needs. Code 66 is retried. Retries wait 21 to 321 seconds, five at most, about ten and a half minutes in all.
2. **The Daily Limit Ends the Sync** - Code 122 fails the sync at once: the limit resets the next day, and a wait would pass the one-hour heartbeat.
3. **No API Budget** - The daily limit depends on the edition and is shared with other integrations. The five concurrent requests are held by `num_workers` (2 to 5, default 3) and `max_concurrency: 5`.
4. **One Login at a Time, and the Host Follows the Account Type** - The CDK serializes token refreshes, so no two logins overlap; each stream still logs in once. An expired refresh token and a wrong client ID or secret fail and say what to fix. Sandboxes read from `pi.demo.pardot.com`; `pardot_api_host` selects it for a Developer Edition org, or `pi.pardot.com` for a training account.
5. **The Restart After 100,000 Records** - After a full page without `nextPageUrl`, 20 streams restart with an inclusive `...AfterOrEqualTo` filter, sent once and encoded, which re-reads the boundary second. 100,000 records in one second cannot be read.
6. **What Waits for a Test Account** - `visitors`, the cursor's `-12:00` offset, the `email_clicks` boundary second and whether a token can expire within the hour are unproven and unchanged.
7. **Saved Configs Are Cleaned** - A config migration removes `v5_page_size`, `page_size` and `split_up_interval`.

## Testing

Run the tests from the connector directory:

```bash
poe test-unit-tests          # mock server tests, no credentials
poe test-integration-tests   # spec and the invalid-config check; the rest is bypassed until a test account exists
```

- No test account exists yet, so the mock server tests in `unit_tests/mock_server/` are the proof for every stream: one file per stream, plus `test_base_requester.py` for the login and the hosts.
- A test fails when a read sends a request to a host that `allowedHosts` in `metadata.yaml` does not list.
- `unit_tests/poetry.lock` holds the CDK version of the base image in `metadata.yaml` for Python 3.11 and later. Relock when the base image moves.
