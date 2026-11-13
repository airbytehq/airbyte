# Contributing to source-outreach

For general guidance on contributing to Airbyte connectors, see the
[Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Unique behaviors (summary)

Full technical detail for each item lives in [AGENTS.md](./AGENTS.md).

1. **Pagination and page sizes** — Most streams use pages of 1000; `mailings` uses 100 to avoid failures on large HTML bodies. Pagination follows Outreach's keyset cursor.
2. **Incremental sync** — The saved cursor is inclusive, so the last record can repeat. Call dispositions and purposes return timestamps without milliseconds.
3. **Error handling** — Missing scopes fail with an actionable configuration error. Rate-limit and maintenance responses wait and retry.
4. **Rate limits and concurrency** — All workers share Outreach's hourly quota and wait for the reset time reported by the API.
5. **Schemas** — JSON:API attributes become top-level fields and relationships become related-id lists.
6. **Authentication: renew on HTTP 401** — A rejected access token is renewed before retrying the same page. A second rejection fails without repeatedly renewing; 403 scope failures still require reauthorization.

## Testing

- `unit_tests/mock_server/` has one test file per stream plus `test_error_handling.py` and `test_spec.py`. They need
  no Outreach account. Run them from `unit_tests/` with `poetry run pytest mock_server/ -vv`.
- The acceptance tests read the CI secret `SECRET_SOURCE-OUTREACH_CREDS`.
- `sequence_states` is the only stream the test account cannot seed; its mock-server test is its only coverage.
- `snippets` and `templates` are listed in `empty_streams` although the test account has records for both. Their
  schemas type `tags` (and, on `templates`, `toRecipients`, `ccRecipients` and `bccRecipients`) as strings, but the API
  returns arrays of strings, so the records fail schema validation. Retyping a top-level field is a breaking change and
  needs its own major version.
