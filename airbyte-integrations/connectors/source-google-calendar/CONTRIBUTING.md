# Contributing to source-google-calendar

Manifest-only declarative connector built on `source-declarative-manifest`. All behavior lives in `manifest.yaml`.

## Authentication

Two options under `credentials`: `auth_type: oauth2.0` ("Authenticate via Google (OAuth)" — backed by `advanced_auth` for Airbyte Cloud) and `auth_type: manual` ("Authenticate with custom app (client ID / secret)" — your own Google Cloud OAuth app). Both require `credentials.client_id`, `credentials.client_secret`, and `credentials.refresh_token`. Advanced auth requests `calendar.calendarlist.readonly`, `calendar.calendars.readonly`, `calendar.events.readonly`, `calendar.settings.readonly`, `calendar.freebusy`, and `calendar.acls.readonly`. Custom-app tokens may use legacy `calendar.readonly` instead of the five non-ACL scopes; `calendar.acls.readonly` is needed only for `acl`. Without it, `acl` fails with a configuration error; generate a scoped refresh token or deselect `acl`. `config_normalization_rules` migrates flat `client_id`/`client_secret`/`client_refresh_token_2` into the custom-app option (`auth_type: manual`), preserving the original issuing app.

## Design choices

- **Incremental `events` uses `updatedMin` + `showDeleted` rather than `syncToken`.** `syncToken` is opaque and non-datetime and can require a full resync on expiry (410). A saved `updatedMin` cursor older than 21 days triggers a re-read, leaving margin for Google's measured 29-day limit. `showDeleted=true` means deletions arrive as `status: "cancelled"` records. Cancelled stubs without `updated` are stamped with the later of the slice start and now minus one hour so they replace live rows under Append + Deduped. With no `start_date` configured, the cursor starts at `2000-01-01T00:00:00Z`; initial reads and full re-reads only send `updatedMin` for a configured start date within the last 21 days, and otherwise filter downloaded records client-side. Fresh incremental reads send the shared saved cursor (`global_substream_cursor: true`).
- **Per-calendar partitioning:** `events`, `acl`, and `freebusy` partition over `calendar_id` through one hidden parent, `calendar_partitions`. When `calendarid` is set, it reads `calendars/{calendarid}` directly (`primary` resolves to the real id), so the calendar does not need to be in the account's calendar list; when unset, it pages through `users/me/calendarList` with `showHidden=true`. The events router requests `minAccessRole=reader`, the ACL router requests `owner`, and freebusy sets no minimum. Those role filters do not apply to an explicitly configured calendar. Calendar ids are URL-encoded in request paths.
- **`channels` is intentionally excluded** — it is push-notification infrastructure (watch/stop), not data to replicate.
- **`acl` requires `calendar.acls.readonly`** (or `calendar.acls` / `calendar`) and an enabled Calendar API. Missing scope or a disabled API fails with `config_error`; other 403 responses (non-owner) and 404 responses are IGNOREd. Rate-limit and quota filters run before these rules.
- **Rate budget:** a 500 requests/minute moving-window API budget covers all requests, including POST `freeBusy`. Rate-limit reasons and HTTP 429 use exponential backoff; exhausted project/user quota fails as a transient error until it resets. Concurrency defaults to 3 workers and is capped at 10.
- **`freebusy` is a snapshot:** POST `freeBusy` requests now minus 30 days through now plus 45 days, independently of `start_date`. Calendar-level errors in a successful response are logged and produce no rows.

## Running locally

```bash
# creds go in secrets/config.json (never commit it)
source-declarative-manifest spec --manifest-path manifest.yaml
source-declarative-manifest check --config secrets/config.json --manifest-path manifest.yaml
source-declarative-manifest discover --config secrets/config.json --manifest-path manifest.yaml
source-declarative-manifest read --config secrets/config.json --catalog integration_tests/configured_catalog.json --manifest-path manifest.yaml
cd unit_tests && poetry install --no-root && poetry run pytest   # unit tests
```

Acceptance tests are configured in `acceptance-test-config.yml` and run through connector CI. The CDK standard-test runner reads every section. The `connection`, `discovery`, `basic_read` and `full_refresh` entries for `secrets/config.json` are merged into one scenario that runs check, discover, and the read tests; its basic read uses `configured_catalog_full_refresh.json` and leaves out the `empty_streams`, so `acl` (until the sandbox token has the `calendar.acls.readonly` scope) and `freebusy` (the sandbox calendar may have no busy blocks) are not read there. The `incremental` `future_state` entry runs separately: a read from `integration_tests/abnormal_state.json` that must return no records.
