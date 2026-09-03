# Kapa Source Connector

The Kapa source connector syncs project threads and their question-answer pairs from the Kapa Query API. It is a manifest-only connector using API-key authentication, cursor pagination, and incremental state based on `last_activity_at`.

For user-facing setup instructions, see the [Kapa source documentation](https://docs.airbyte.com/integrations/sources/kapa).

## Streams

| Stream | Primary key | Cursor | Sync modes |
| --- | --- | --- | --- |
| `threads` | `id` | `last_activity_at` | Full refresh, incremental |

Incremental requests send the saved cursor as the inclusive `updated_since` lower bound and sort by `last_activity_at` ascending. A record at the state boundary can be read again; append-dedup mode uses `id` to remove that boundary duplicate.

## Configuration

| Field | Required | Description |
| --- | --- | --- |
| `api_key` | Yes | Kapa API key sent in the `X-API-KEY` header. |
| `project_id` | Yes | UUID of the Kapa project to sync. |
| `start_date` | Yes | Earliest activity timestamp, in ISO 8601 format with whole-second precision. |

Keep real credentials in `.secrets/config.json`. The tracked values under `integration_tests/` are non-production placeholders.

## Local Development

Run `make help` to list commands and input paths. The default authenticated configuration path is `.secrets/config.json`.

```bash
make build
make spec
make unit-test
make connector-test
```

Authenticated commands require a local config:

```bash
make check
make discover
make read
```

Override inputs when needed:

```bash
make read CONFIG=.secrets/config.json CATALOG=integration_tests/configured_catalog.json STATE=integration_tests/sample_state.json
```

## Docker Commands

After `make build`, the corresponding container commands are:

```bash
docker run --rm airbyte/source-kapa:dev spec
docker run --rm -v "$PWD/.secrets/config.json:/config.json:ro" airbyte/source-kapa:dev check --config /config.json
docker run --rm -v "$PWD/.secrets/config.json:/config.json:ro" airbyte/source-kapa:dev discover --config /config.json
docker run --rm \
  -v "$PWD/.secrets/config.json:/config.json:ro" \
  -v "$PWD/integration_tests/configured_catalog.json:/catalog.json:ro" \
  -v "$PWD/integration_tests/sample_state.json:/state.json:ro" \
  airbyte/source-kapa:dev read --config /config.json --catalog /catalog.json --state /state.json
```

## Tests

`unit_tests/` loads the real manifest through the CDK and mocks Kapa HTTP responses. It covers authentication, request parameters, pagination, incremental lower bounds, resource errors, rate limiting, and transient service errors.

Credential-dependent acceptance tests are bypassed until a dedicated Kapa test project is available. When credentials are available, place them in `.secrets/config.json`, replace the bypasses in `acceptance-test-config.yml` with test scenarios, and run `make test` from an initialized `airbyte-ci/connectors/pipelines` Poetry environment.

## Known Limitations

- Only the Query API v1 project threads endpoint is supported.
- Kapa does not document endpoint-specific rate limits or every error payload. The connector applies bounded fallback handling for 403 rate-limit responses, 429, and transient 502/503/504 responses.
- Expected integration records are not tracked because thread data is specific to each Kapa project.

## Publishing

The initial connector and canonical image tags are both `0.1.0`. Update `dockerImageTag`, `canonicalImageTag`, and the changelog in the user documentation together for a release.
