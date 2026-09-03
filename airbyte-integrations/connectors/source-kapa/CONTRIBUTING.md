# Contributing to Source Kapa

## Overview

Source Kapa is a manifest-only connector for the Kapa Query API v1 project threads endpoint. The manifest owns authentication, request construction, cursor pagination, incremental state, schema, and retry behavior; no custom Python runtime code is used.

Key files:

- `manifest.yaml`: connector behavior and stream schema.
- `metadata.yaml`: image identity, registry settings, and documentation links.
- `acceptance-test-config.yml`: connector standard-test scenarios and explicit credential bypasses.
- `unit_tests/`: mocked runtime tests for the declarative manifest.
- `integration_tests/`: local config, catalog, and state artifacts.
- `erd/source.dbml`: stream model.

## Prerequisites

- Docker with Buildx
- Python 3.10 or newer
- `uv`
- `jq`
- An initialized `airbyte-ci/connectors/pipelines` Poetry environment for `make test`
- A dedicated Kapa project and API key for authenticated checks

Run `make help` for the local command list.

## Secrets

Create `.secrets/config.json` locally with non-placeholder values:

```json
{
  "api_key": "<api_key>",
  "project_id": "00000000-0000-4000-8000-000000000000",
  "start_date": "2026-08-27T00:00:00Z"
}
```

The values above are non-production placeholders. Never commit `.secrets/config.json`, reusable tokens, account identifiers, private project URLs, or payloads copied from a real thread.

## Validation Sequence

Run credential-free validation first:

```bash
make unit-test
make connector-test
make build
make spec
```

Then run the authenticated protocol commands in order:

```bash
make check
make discover
make read
```

Expected outcomes:

- `spec` emits an Airbyte specification with `api_key`, `project_id`, and `start_date` required.
- `check` makes a minimal threads request and succeeds only with access to the configured project.
- `discover` exposes `threads` with primary key `id` and cursor `last_activity_at`.
- `read` emits thread records and a stream state message without moving the cursor backward.

Use `integration_tests/future_state.json` to verify that an abnormal future cursor returns no records and does not trigger an unbounded historical read.

## Pull Request Checklist

- Verify endpoint paths, parameters, timestamp formats, and response fields against the Kapa API reference.
- Add or update mocked runtime tests for every behavioral manifest change.
- Keep `configured_catalog.json`, state fixtures, documentation, and `erd/source.dbml` synchronized with the stream set.
- Run unit tests, connector standard tests, Docker build, and spec validation.
- Run authenticated check, discover, and a bounded incremental read when test credentials are available.
- Update both image tags and the user-documentation changelog for a release.
- Confirm `README.md`, `CONTRIBUTING.md`, integration docs, fixtures, and logs contain no real secrets or tenant-specific data.
- Confirm `.secrets/config.json` remains local-only and every tracked configuration example uses placeholders.

## Troubleshooting

Authentication failures: confirm the API key belongs to a user or service account with access to the project and that `project_id` is the project UUID, not a display name.

Rate limits: preserve `Retry-After` headers when capturing diagnostics. The connector retries documented rate-limit responses with a bounded budget; permission-related 403 responses must fail without retrying.

Pagination: verify `next_cursor` is passed unchanged as the next request's `cursor`. Never decode or alter the signed token.

State: compare the emitted `last_activity_at` value with the latest record. Kapa's `updated_since` filter is inclusive, so a boundary record can repeat and must retain a stable `id`.

Timeouts and transient errors: inspect Airbyte logs for 502, 503, or 504 responses. These statuses use a 60-second fallback backoff with at most 20 retries.