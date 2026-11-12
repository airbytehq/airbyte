# Contributing to source-google-calendar

Manifest-only declarative connector built on `source-declarative-manifest`. All behavior lives in `manifest.yaml`.

## Authentication

Two options under `credentials`: `auth_type: oauth2.0` ("Authenticate via Google (OAuth)" — backed by `advanced_auth` for Airbyte Cloud) and `auth_type: manual` ("Authenticate with custom app (client ID / secret)" — your own Google Cloud OAuth app). Both require `credentials.client_id`, `credentials.client_secret`, and `credentials.refresh_token`. Advanced auth requests `calendar.calendarlist.readonly`, `calendar.calendars.readonly`, `calendar.events.readonly`, `calendar.settings.readonly`, `calendar.freebusy`, and `calendar.acls.readonly`. Custom-app tokens may use the broader `calendar.readonly` instead of the five non-ACL scopes; `calendar.acls.readonly` is needed only for `acl`. Without it, `acl` fails with a configuration error; generate a scoped refresh token or deselect `acl`. `config_normalization_rules` migrates flat `client_id`/`client_secret`/`client_refresh_token_2` into the custom-app option (`auth_type: manual`), preserving the original issuing app.

## Design choices

- **Incremental `events` uses `updatedMin` + `showDeleted` rather than `syncToken`.** `syncToken` is opaque and non-datetime and can require a full resync on expiry (410). A saved `updatedMin` cursor older than 21 days triggers a re-read, leaving margin for Google's measured 29-day limit. `showDeleted=true` means deletions arrive as `status: "cancelled"` records. Cancelled stubs without `updated` are stamped with the later of the slice start and now minus one hour so they replace live rows under Append + Deduped. With no `start_date` configured, the cursor starts at `2000-01-01T00:00:00Z`; initial reads and full re-reads only send `updatedMin` for a configured start date within the last 21 days, and otherwise filter downloaded records client-side. Fresh incremental reads send the shared saved cursor (`global_substream_cursor: true`).
- **Full-refresh exceptions for token-capable streams:** [Google's sync protocol](https://developers.google.com/workspace/calendar/api/guides/sync) requires clearing stored data and a full resync if a `syncToken` expires (410). These streams intentionally read snapshots rather than persist expiring tokens; none offers an `updatedMin` filter:
  - [`settings`](https://developers.google.com/workspace/calendar/api/v3/reference/settings/list) reads a small per-user preference snapshot, avoiding token state for infrequently changed settings.
  - [`calendarlist`](https://developers.google.com/workspace/calendar/api/v3/reference/calendarList/list) reads a typically small calendar directory. Complete snapshots also keep parent partition discovery current; Google's token mode disallows the `minAccessRole` filter used by those parents.
  - [`acl`](https://developers.google.com/workspace/calendar/api/v3/reference/acl/list) reads typically small sharing-rule snapshots per owned calendar, including deleted rules, without maintaining and recovering a separate token for every calendar.
- **Per-calendar partitioning:** `events`, `acl`, and `freebusy` partition over `calendar_id` through one hidden parent, `calendar_partitions`. When `calendarid` is set, it reads `calendars/{calendarid}` directly (`primary` resolves to the real id), so the calendar does not need to be in the account's calendar list; when unset, it pages through `users/me/calendarList` with `showHidden=true`. The events router requests `minAccessRole=reader`, the ACL router requests `owner`, and freebusy sets no minimum. Those role filters do not apply to an explicitly configured calendar. Calendar ids are URL-encoded in request paths.
- **Deletions and parent-only filtering:** public `calendarlist` emits `deleted: true` tombstones, `acl` emits deleted rules with `role: "none"`, and `events` emits `status: "cancelled"`. Internal parent reads do not request deleted calendar-list entries. Their defensive deletion filters apply only to internal parent reads that select calendar IDs for `calendars`, `events`, `acl`, and `freebusy`, not to output records. They avoid unnecessary requests for removed calendars; calendar/event child reads that still return 404 or 410 `deleted` are logged and skipped. Full-refresh `calendars` has no tombstone: a removed calendar drops out of its next snapshot, with the deletion visible in `calendarlist`. Calendar-list and settings requests use `maxResults=250`.
- **`channels` is intentionally excluded** — it is push-notification infrastructure (watch/stop), not data to replicate.
- **`acl` requires `calendar.acls.readonly`** (or `calendar.acls` / `calendar`) and an enabled Calendar API. Missing scope or a disabled API fails with `config_error`; other 403 responses (non-owner) and 404 responses are IGNOREd. Rate-limit and quota filters run before these rules.
- **Rate budget:** a 500 requests/minute moving-window API budget covers all requests, including POST `freeBusy`. Rate-limit reasons and HTTP 429 use exponential backoff; exhausted project/user quota fails as a transient error until it resets. Concurrency defaults to 3 workers and is capped at 10; saved values below 2 run with 2 workers.
- **Retry timing:** [Google's error guide](https://developers.google.com/workspace/calendar/api/guides/errors) recommends exponential backoff but documents no `Retry-After` header or other server-provided wait duration. The manifest explicitly uses `ExponentialBackoffStrategy` with `factor: 5`, not a header-based wait strategy.
- **`freebusy` is a snapshot:** POST `freeBusy` requests now minus 30 days through now plus 45 days, independently of `start_date`. Calendar-level errors in a successful response are logged and produce no rows.

## Error mapping

The base requester maps [Google Calendar errors](https://developers.google.com/workspace/calendar/api/guides/errors) as follows. The ACL requester has the 403/404 exceptions noted below. Reason-specific filters run before generic HTTP-status filters.

| Response | Handling |
| --- | --- |
| 401 | Fail with `config_error`; re-authorize or replace the refresh token. |
| `rateLimitExceeded` / `userRateLimitExceeded` (403 or 429) | `RATE_LIMITED`, with exponential backoff. |
| `quotaExceeded` / `dailyLimitExceeded`, except 429 | Fail with `transient_error` until quota resets. |
| 403 `insufficientPermissions` / `ACCESS_TOKEN_SCOPE_INSUFFICIENT` | Fail with a missing-scope `config_error`. ACL also recognizes `accessNotConfigured` / `SERVICE_DISABLED` as configuration errors. |
| Other 403 | Fail with `config_error` for calendar access or an API that is turned off; ACL ignores these responses for non-owned calendars. |
| 404 | Calendar/event child reads log and skip; parent validation and non-calendar endpoints fail with `config_error`. ACL still ignores it. |
| 410 `deleted` | Calendar/event child reads log and skip; parent validation fails with `config_error`. |
| 410 `fullSyncRequired` | Fail with `config_error`; reset events. |
| Other 410, including `updatedMinTooLongAgo` | Base requester fails with `transient_error`; reset events to re-read sooner, or let the 21-day retention guard trigger a re-read. |
| Other 429 | `RATE_LIMITED`, with exponential backoff. |
| 500 / 502 / 503 / 504 | `RETRY`, with exponential backoff. |

**404 exception.** Google's guide suggests backoff even for a missing or inaccessible resource. This connector instead fails immediately during configured-calendar validation, but skips calendar/event child reads if a calendar disappears or becomes unshared after discovery. The `calendars` stream always uses list-derived partitions, even with Calendar Id set. ACL retains its existing skip behavior; configured-calendar validation runs before ACL requests. List-endpoint failures still fail the sync.

## Running locally

```bash
# creds go in secrets/config.json (never commit it)
source-declarative-manifest spec --manifest-path manifest.yaml
source-declarative-manifest check --config secrets/config.json --manifest-path manifest.yaml
source-declarative-manifest discover --config secrets/config.json --manifest-path manifest.yaml
source-declarative-manifest read --config secrets/config.json --catalog integration_tests/configured_catalog.json --manifest-path manifest.yaml
cd unit_tests && poetry install --no-root && poetry run pytest   # unit tests
```

Acceptance tests are configured in `acceptance-test-config.yml` and run through connector CI. Use the `SECRET_SOURCE-GOOGLE-CALENDAR__CREDS` secret from `dataline-integration-testing` as `secrets/config.json`. It has no `calendarid`, so all calendars on the account are read. The refresh token must carry both `calendar.readonly` and `calendar.acls.readonly`; otherwise `acl` fails with insufficient scopes.

The account's calendars hold more than 20 events, including cancelled, recurring and all-day events, plus recurring timed events that keep busy blocks in the rolling 75-day `freebusy` window.

The CDK standard-test runner reads every section. The `connection`, `discovery`, `basic_read` and `full_refresh` entries for `secrets/config.json` are merged into one scenario that runs check, discover, and the read tests; its basic read uses `configured_catalog_full_refresh.json` and reads all streams. The `incremental` `future_state` entry runs separately: a read from `integration_tests/abnormal_state.json` that must return no records.
