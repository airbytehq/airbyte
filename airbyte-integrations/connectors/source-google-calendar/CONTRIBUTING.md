# Contributing to source-google-calendar

Manifest-only declarative connector built on `source-declarative-manifest`. All behavior lives in `manifest.yaml`.

## Authentication

Required flat OAuth fields (`client_id`, `client_secret`, `client_refresh_token_2`) — a refresh token issued by your own Google Cloud OAuth app with the `calendar.readonly` and `calendar.acls.readonly` scopes, plus that app's client ID and secret. Without `calendar.acls.readonly` the `acl` stream fails with a configuration error; generate a new refresh token with the scope or deselect `acl`. There is no built-in OAuth sign-in button.

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

Acceptance tests are configured in `acceptance-test-config.yml` and run through connector CI. The legacy `discovery`, `incremental`, and `full_refresh` blocks are not run by the CDK standard-test runner; it reads `spec`, `connection`, and `basic_read`. The basic-read catalog excludes `acl` until the sandbox token has the scope; `freebusy` may be empty.
