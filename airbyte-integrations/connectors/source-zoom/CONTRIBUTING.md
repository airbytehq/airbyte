# Contributing to source-zoom

## Deletions

Zoom's REST API exposes no deletion feed; deletions are only published as webhooks such as `meeting.deleted`.
Deleted meetings and webinars disappear from the next full refresh. For users, `users.status` (`active`,
`inactive`, or `pending`) is the only soft-delete indicator. Incremental streams do not observe deletions:
`meetings` and `webinars` use `created_at`, `report_meetings` uses `end_time`,
`report_meeting_participants` uses `meeting_end_time`, and `report_user_meetings` uses `end_time`.

The authorization endpoint is hidden and defaults to Zoom's token URL.

For general connector-development guidance, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Authentication

`manifest.yaml` uses `SelectiveAuthenticator` on `credentials.auth_type`. The `oauth2.0` option uses the OAuth `refresh_token` grant. Zoom refresh tokens expire after 90 days; each refresh can rotate the token, and the manifest's refresh-token updater saves the new refresh token, access token, and expiry back under `credentials`. `unit_tests/test_oauth_and_config_migration.py` verifies that rotated values are saved.

The `server_to_server` option uses the `account_credentials` grant and does not use refresh tokens. Zoom access tokens last one hour; `unit_tests/test_authenticator.py` exercises an `expires_in` response of 3599 seconds and refresh after expiry.

Config normalization migrates legacy top-level Server-to-Server OAuth fields (`account_id`, `client_id`, `client_secret`, and `authorization_endpoint`) into `credentials`, and sets `credentials.auth_type` to `server_to_server`. See `unit_tests/test_oauth_and_config_migration.py` for migration coverage.

## Error handling

The response filters below are defined in `manifest.yaml`. Mock-server coverage is in `unit_tests/test_error_handling.py`, `unit_tests/test_authenticator.py`, and the corresponding `unit_tests/integration/test_<stream>.py` tests.

| Zoom response | Action | Where |
| :------------ | :----- | :---- |
| Code `124` | Refresh the access token and retry the request. | Shared `definitions.zoom_error_handler`, attached to every requester; `test_authenticator.py` |
| Code `4711` | Fail with a configuration error that names the missing scope. | Shared `definitions.zoom_error_handler` on all requesters; additional stream-specific scope filters on `report_user_meetings`, `report_daily`, `chat_channels`, and `zoom_events`; `test_error_handling.py` and stream integration tests |
| Code `3161` | Ignore the user's standard meeting-list partition rather than failing the sync. | User-to-meeting parent requesters; the `test_error_handling.py` skip matrix no longer includes the session-based `report_meetings` or `report_meeting_participants` streams |
| Code `3001` | Ignore the affected resource when a meeting or webinar was deleted or no longer has report data. | `meetings`, `meeting_registrants`, `meeting_polls`, `meeting_registration_questions`, `webinar_registration_questions`, `webinar_tracking_sources`, `report_webinars`, and `report_webinar_participants`; deleted-meeting case in `test_error_handling.py`. Session-based `report_meetings` and `report_meeting_participants` ignore HTTP `400`/`404` instead |
| Code `300` | Ignore the response. | `meeting_registrants`; `report_user_meetings` and `report_daily` when Zoom reports a date outside its six-month window |
| Code `200` | Fail with a configuration error when a report requires a Pro-or-higher plan. | `report_user_meetings` and `report_daily` requesters |
| Code `1001` | Ignore a user removed after user discovery. | `report_user_meetings` and `chat_channels` requesters |
| HTTP `400` or `404` | Ignore the response; the affected stream can return no records. | Only the stream-specific requesters listed below |
| Token error `invalid_grant`, `invalid_client`, `invalid_request`, or `unsupported_grant_type` | Fail with a configuration error. | OAuth and Server-to-Server token authenticators; `test_oauth_and_config_migration.py`, `test_authenticator.py` |

The manifest explicitly ignores HTTP `400` responses on `meeting_polls`, `meeting_poll_results`, `meeting_registration_questions`, `webinars`, `webinar_panelists`, `webinar_registrants`, `webinar_absentees`, `webinar_polls`, `webinar_registration_questions`, `webinar_tracking_sources`, `webinar_qna_results`, `report_meetings`, `report_meeting_participants`, `report_webinars`, and `report_webinar_participants`. It explicitly ignores HTTP `404` responses on `meeting_poll_results`, `webinars`, `webinar_panelists`, `webinar_registrants`, `webinar_absentees`, `webinar_polls`, `webinar_poll_results`, `webinar_qna_results`, `report_meetings`, and `report_meeting_participants`.

## Rate limits

Zoom applies rate limits per account and plan, shared across every app on the account; see Zoom's [rate-limit documentation](https://developers.zoom.us/docs/api/rate-limits/). The live header sample from 2026-11-06 classified these source-zoom endpoints:

- **Heavy (Pro: 10 requests/second):** `/report/users/{uid}/meetings`, `/report/meetings/{uuid}`, `/report/meetings/{uuid}/participants`, `/report/daily`, `/report/webinars/{wuuid}`, `/report/webinars/{wuuid}/participants`, and `/past_webinars/{wuuid}/absentees`.
- **Medium (Pro: 20 requests/second):** `/users`, `/users/{uid}/meetings`, `/users/{uid}/webinars`, `/meetings/{mid}/registrants`, `/past_meetings/{uuid}/polls`, `/webinars/{wid}/panelists`, `/webinars/{wid}/registrants`, `/webinars/{wid}/tracking_sources`, `/past_webinars/{wuuid}/polls`, `/past_webinars/{wuuid}/qa`, and `/chat/users/{uid}/channels`.
- **Light (Pro: 30 requests/second):** `/meetings/{mid}`, `/meetings/{mid}/polls`, `/meetings/{mid}/registrants/questions`, `/webinars/{wid}`, `/webinars/{wid}/registrants/questions`, `/zoom_events/events`, and any request not matched by a higher category. `/webinars/{wid}/polls`, which was not in the live sample, uses this Light catch-all.

The `webinar_tracking_sources` response had no rate-limit category header and `chat_channels` returned the unrecognized `Dp_xms` category; both are budgeted conservatively as Medium. The sampled `webinars/{wid}` detail response had no category header and falls through to Light, consistent with the sampled meeting-detail endpoint.

The connector budgets at Pro rates because Pro is the minimum supported plan. Zoom documents higher per-second limits for Business+ (Light 80, Medium 60, Heavy 40 requests/second), but using Pro limits keeps connector-issued requests within the limits of every supported plan. Heavy and Resource-intensive requests share a daily cap of 30,000 on Pro and 60,000 on Business+.

Each Airbyte Zoom source applies its own rate-limit budget, but multiple Zoom sources and other apps on the same Zoom account share its limits, so their requests add up; lower `num_workers` on those sources if they hit 429s.

The manifest does not set `ratelimit_remaining_header` or `ratelimit_reset_header`: Zoom's `x-ratelimit-remaining` reports the daily Heavy count, not the one-second moving-window balance, so it must not be applied to that budget. The daily cap is not modeled as a `P1D` moving window because exhausting that budget would stall a sync for hours; the connector relies on Zoom's `Retry-After` response instead. `WaitTimeFromHeader` honors short `Retry-After` values and fails the stream for a wait of 600 seconds or longer; if the header is missing, the CDK uses exponential backoff. `unit_tests/test_error_handling.py` covers these cases.

## Keyless report streams

`meeting_poll_results`, `webinar_poll_results`, and `webinar_qna_results` expose respondent `email` and `name` as nullable fields and nest repeated question/answer details without a stable answer ID. Poll IDs identify polls rather than individual responses. Because respondent fields can be absent and question/answer text can repeat, no deterministic key exists, so these streams are intentionally keyless.

## Licence-gated streams

Webinar and report-webinar streams require the Zoom Webinars add-on. `zoom_events` requires a Webinars Plus or Zoom Events license. The test account lacks data for these licensed streams, so `acceptance-test-config.yml` lists them as empty and bypassed in `basic_read`; each is covered by a mock-server test in `unit_tests/integration/`:

- `webinars` — `test_webinars.py`
- `webinar_panelists` — `test_webinar_panelists.py`
- `webinar_registrants` — `test_webinar_registrants.py`
- `webinar_absentees` — `test_webinar_absentees.py`
- `webinar_polls` — `test_webinar_polls.py`
- `webinar_poll_results` — `test_webinar_poll_results.py`
- `webinar_registration_questions` — `test_webinar_registration_questions.py`
- `webinar_tracking_sources` — `test_webinar_tracking_sources.py`
- `webinar_qna_results` — `test_webinar_qna_results.py`
- `report_webinars` — `test_report_webinars.py`
- `report_webinar_participants` — `test_report_webinar_participants.py`
- `zoom_events` — `test_zoom_events.py`

## Testing

`unit_tests/pyproject.toml` defines the pytest dependencies and no Poe tasks. Run the unit and mock-server tests with:

```bash
cd airbyte-integrations/connectors/source-zoom/unit_tests
poetry install
poetry run pytest
```

Acceptance tests need a populated Zoom account and Server-to-Server OAuth credentials. The GSM secret is `SECRET_SOURCE-ZOOM__CREDS`; the acceptance config reads the credentials from `secrets/config.json`.
