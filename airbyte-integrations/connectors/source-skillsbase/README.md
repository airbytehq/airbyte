# Source Skills Base

Manifest-only Airbyte source for the [Skills Base REST API](https://help.skills-base.com/kb/technical-integrations/rest-api),
extended with a small custom Python authenticator to handle Skills Base's
concurrent-token-cap OAuth flow.

## Streams

| Stream                       | Endpoint                                                  | Sync modes                | Primary key             | Notes |
| ---------------------------- | --------------------------------------------------------- | ------------------------- | ----------------------- | ----- |
| `people`                     | `GET /1.0/people`                                         | full refresh, incremental | `id`                    | Cursor: `id` (IncrementingCountCursor). Paginated via `start_index`. |
| `skill_ratings`              | `GET /1.0/skillratings/person/{person_id}`                | full refresh              | (`person_id`, `skill_id`) | Substream of `people` — one HTTP call per person. `person_id` and `synced_at` are added via record transformations. |
| `qualifications_assignments` | `GET /2.0/qualificationassignments`                       | full refresh, incremental | `id`                    | Cursor: `id` (IncrementingCountCursor). Paginated via `start_index`. |

All streams extract records from the `data` field of the API response.

## Configuration

Required fields:

| Field           | Description                                                                          |
| --------------- | ------------------------------------------------------------------------------------ |
| `api_host`      | Base URL of your Skills Base instance, e.g. `https://api.skills-base.com` (no trailing slash). |
| `client_id`     | OAuth client ID issued under **Admin → Settings → API → Manage API Keys**.            |
| `client_secret` | OAuth client secret for the same API key.                                            |
| `start_date`    | `YYYY-MM-DD`. Reserved for future incremental fixtures; required by spec.            |

Auto-managed fields (do not set manually):

| Field                | Description                                                              |
| -------------------- | ------------------------------------------------------------------------ |
| `access_token`       | OAuth access token cached after a successful client-credentials exchange. |
| `token_expiry_date`  | ISO-8601 timestamp marking when the cached token expires.                 |

These two fields are declared on the spec so the Airbyte platform persists them
between syncs via the `CONNECTOR_CONFIG` control-message mechanism.

## Authentication

OAuth 2.0 client-credentials grant against `POST {api_host}/oauth/access_token`.

Skills Base enforces a low cap on **concurrently active** access tokens per
integration: requesting a new token while a previous one is still alive returns
`403 Access token allowance exceeded`. To avoid burning the allowance on every
sync run, the connector ships a custom authenticator that caches the token
across runs and refreshes only when necessary.

## Custom component (`components.py`)

The manifest references a custom authenticator class instead of using the
declarative `OAuth2` block, because the cache + control-message persistence
pattern is not expressible in pure YAML.

Class: `ClientCredentialsConfigUpdaterAuthenticator`

Behaviour, per call to `token`:

1. Acquire a process-wide `threading.Lock` so concurrent stream workers don't
   race the token endpoint.
2. Read `access_token` and `token_expiry_date` from `self.config`. If both are
   present and the timestamp is at least 60 s in the future, return the cached
   bearer unchanged.
3. Otherwise `POST` to `{api_host}/oauth/access_token` with `grant_type=client_credentials`:
   - **`403` / `429` with `rate limit`** in the body → sleep until `X-RateLimit-Reset` (or 60 s
     if absent), retry up to 3 times.
   - **`403` / `429` with `allowance exceeded`** → raise an
     `AirbyteTracedException(config_error)` instructing the user to wait for the
     existing token to expire on Skills Base's side. Empirically Skills Base does
     not send `X-RateLimit-Reset` / `Retry-After` on these responses, so the
     connector cannot self-schedule a retry — the slot release lives entirely on
     the server side.
   - **Other non-`2xx`** → raise `AirbyteTracedException(config_error)` with the
     HTTP status and body for debugging.
4. On success, mutate `self.config[access_token]` and
   `self.config[token_expiry_date]`, then call
   `emit_configuration_as_airbyte_control_message(self.config)`. The platform
   (or, locally, the `scripts/persist_token.sh` helper described below)
   writes those values back to the connection config so subsequent runs reuse
   them.

## Rate limiting

The declarative error handler (in `manifest.yaml`) covers data endpoints:

- `403` / `429` with `rate limit exceeded` in the body → `RATE_LIMITED`,
  honouring `X-RateLimit-Reset` then `Retry-After`, falling back to a 180 s
  constant backoff.
- `502` / `503` / `504` → `RETRY` with up to 8 attempts.
- `404` / `409` → `IGNORE` (treated as empty page).

Auth-endpoint rate limits are handled inside `components.py` (see above).

## Local development and testing

All commands below assume you are inside the connector directory:
`airbyte-integrations/connectors/source-skillsbase`.

### Provisioning secrets

Real credentials live in `./secrets/config.json` (the directory is gitignored
at the repo root). Use `integration_tests/sample_config.json` as a template
and fill in the four required fields.

### Makefile targets

The `Makefile` wraps the connector in `docker run` against the locally-built
dev image and pipes any `CONNECTOR_CONFIG` control message back into
`secrets/config.json` via `scripts/persist_token.sh`, mimicking what the
Airbyte platform does in production. That keeps the cached token in step with
what Skills Base considers active.

| Target                | What it does                                                                 |
| --------------------- | ---------------------------------------------------------------------------- |
| `make help`           | List all targets with one-line descriptions.                                 |
| `make build`          | Build the dev Docker image with `io.airbyte.name` / `io.airbyte.version` labels read from `metadata.yaml`. |
| `make spec`           | Print the connector spec JSON.                                               |
| `make gen-spec`       | Generate `integration_tests/spec.json` from the connector — re-run after any change to the `spec:` block in `manifest.yaml`. |
| `make check`          | Run `check` against `secrets/config.json` (expect succeed). Persists any refreshed token. |
| `make check-invalid`  | Run `check` against `integration_tests/invalid_config.json` (expect fail).   |
| `make discover`       | Discover available streams using `secrets/config.json`.                      |
| `make read`           | Read all streams using `integration_tests/configured_catalog.json`.          |
| `make read-qualifications` | Read only `qualifications_assignments` (smallest stream — useful for quick end-to-end checks). |
| `make test-acceptance` | Run Connector Acceptance Tests (rebuilds the image and pre-warms the token first). |
| `make unit-test`      | Run pure-Python unit tests for `components.py` (no Docker, no Skills Base). First run sets up `unit_tests/.venv` automatically. |
| `make clean`          | Remove the local dev Docker image.                                            |

### Typical first-run workflow

```bash
# 1. Populate credentials
mkdir -p secrets
cp integration_tests/sample_config.json secrets/config.json
$EDITOR secrets/config.json   # fill in api_host, client_id, client_secret, start_date

# 2. Build and sanity-check
make build
make check                    # writes a fresh access_token back into secrets/config.json
make discover                 # confirms the three streams are reported

# 3. Smallest end-to-end read
make read-qualifications
```

### Token-allowance gotcha

If you see `Access token allowance exceeded`, it means Skills Base still has a
live token on file that conflicts with the one the connector is asking for.
Two ways out:

1. Wait for the existing token to expire (default TTL is one hour from
   issuance, recorded in `token_expiry_date`).
2. Revoke it manually under **Admin → Settings → API → Manage API Keys**.

After either, clear the local cache before retrying so the connector requests a
fresh one:

```bash
jq 'del(.access_token, .token_expiry_date)' secrets/config.json > /tmp/c.json \
  && mv /tmp/c.json secrets/config.json
make check
```

## Unit tests

`unit_tests/test_authenticator.py` exercises the custom authenticator in
`components.py` directly with `pytest` + `requests-mock` — no Docker, no
Skills Base, no manifest parsing. Each test runs in milliseconds and covers:

- `_is_expired` boundary cases (past, future, inside the 60 s safety margin,
  malformed, naive vs tz-aware timestamps).
- `_get_or_refresh_token` cache decision (hit returns cached with zero HTTP;
  miss for any of `access_token` empty, `token_expiry_date` empty, or expired
  → triggers a refresh).
- `_refresh_and_persist_token` happy path (token + expiry written into
  `self.config`, expiry equals `now + expires_in`, `expires_in` defaults to
  3600 when the response omits it).
- `_refresh_and_persist_token` error branches (`403`/`429` "allowance
  exceeded" → `config_error`; `403`/`429` "rate limit" with
  `X-RateLimit-Reset` → retry; same response without the header → 60 s
  fallback retry; persistent rate limit → `transient_error`; other 4xx →
  `config_error`; network exception → `transient_error`).

Run with:

```bash
make unit-test
```

The first invocation creates `unit_tests/.venv` and installs `pytest`,
`requests-mock`, and `airbyte-cdk` into it. Subsequent runs reuse the venv.

## Connector Acceptance Tests

`acceptance-test-config.yml` configures the upstream Connector Acceptance Test
(CAT) suite. Run with `make test-acceptance`, which:

1. Rebuilds the dev image so labels/manifest changes are picked up.
2. Pre-warms `secrets/config.json` with a fresh token via `make check`, so
   CAT's parallel containers reuse a single live token instead of
   stampeding the OAuth endpoint.
3. Runs `airbyte/connector-acceptance-test:latest` against the connector with
   `-k "not test_backward_compatibility"`, because there is no previously-published
   image on Docker Hub for CAT to diff against.

### What CAT actually checks

- **`spec`** — connector spec matches `integration_tests/spec.json`.
- **`connection`** — valid config succeeds, `integration_tests/invalid_config.json` fails.
- **`discovery`** — discover returns a valid catalog.
- **`basic_read` / `full_refresh`** — runs against
  `integration_tests/qualifications_catalog.json` (single-stream
  `qualifications_assignments`) rather than the full catalog, because reading
  the `people` + `skill_ratings` substream on the live sandbox exceeds Skills
  Base's rate limits during a CAT cycle.
- **`incremental`** — currently bypassed; will be enabled once a baseline
  sync has been verified and an `abnormal_state.json` fixture is added.

### When to regenerate `integration_tests/spec.json`

Run `make gen-spec` whenever you edit the `spec:` block in `manifest.yaml`,
otherwise CAT's `spec` test will fail with a mismatch.

## Build and publish

The connector is published to GHCR by Canonical CD (see
`.github/workflows/canonical_cd.yml`). Two metadata fields drive that
pipeline:

| Field                | Used by         | Notes                                                      |
| -------------------- | --------------- | ---------------------------------------------------------- |
| `dockerImageTag`     | upstream / dev   | Tracks the upstream Airbyte versioning convention.        |
| `canonicalImageTag`  | Canonical CD    | Tag used when publishing to `ghcr.io/canonical/airbyte/source-skillsbase`. Bump the `-canonical-N.M.K` suffix on every Canonical-only build. |

To manually rebuild and publish (e.g. backfilling an image after a CD fix),
trigger the `Canonical Generate Image` workflow from the GitHub Actions UI
with `connectors=source-skillsbase`.

## Changelog

| Version | Date       | Summary                                                                                     |
| ------- | ---------- | ------------------------------------------------------------------------------------------- |
| 1.3.0   | 2026-10-21 | Add `competencies` stream (person-linked competency via the Skill Query API).               |
| 1.2.0   | 2026-10-08 | Update `courses` to the `/2.0/courses` schema; migrate `training_completions` to Skill Query. |
| 1.1.0   |            | Add `hire_date` field to the `people` stream.                                               |
| 1.0.0   | 2026-05-12 | Initial Skills Base source connector.                                                        |

