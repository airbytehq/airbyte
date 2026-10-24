# Contributing to source-zoom

## Deletions

Zoom's REST API exposes no deletion feed; deletions are only published as webhooks such as `meeting.deleted`.
Deleted meetings and webinars disappear from the next full refresh. For users, `users.status` (`active`,
`inactive`, or `pending`) is the only soft-delete indicator. Incremental streams do not observe deletions.

The authorization endpoint is hidden and defaults to Zoom's token URL.

For general connector-development guidance, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Authentication

`manifest.yaml` uses `SelectiveAuthenticator` on `credentials.auth_type`. The `oauth2.0` option uses the OAuth `refresh_token` grant. Zoom refresh tokens expire after 90 days; each refresh can rotate the token, and the manifest's refresh-token updater saves the new refresh token, access token, and expiry back under `credentials`. `unit_tests/test_oauth_and_config_migration.py` verifies that rotated values are saved.

The `server_to_server` option uses the `account_credentials` grant and does not use refresh tokens. Zoom access tokens last one hour; `unit_tests/test_authenticator.py` exercises an `expires_in` response of 3599 seconds and refresh after expiry.

Config normalization migrates legacy top-level Server-to-Server OAuth fields (`account_id`, `client_id`, `client_secret`, and `authorization_endpoint`) into `credentials`, and sets `credentials.auth_type` to `server_to_server`. See `unit_tests/test_oauth_and_config_migration.py` for migration coverage.

## Error handling

The response filters below are defined in `manifest.yaml`. Mock-server coverage is in `unit_tests/test_error_handling.py` and `unit_tests/test_authenticator.py`.

| Zoom response | Action | Where |
| :------------ | :----- | :---- |
| Code `124` | Refresh the access token and retry the request. | Shared `definitions.zoom_error_handler`, attached to every requester; `test_authenticator.py` |
| Code `4711` | Fail with a configuration error that names the missing scope. | Shared `definitions.zoom_error_handler`; `test_error_handling.py` |
| Code `3161` | Ignore the user's meeting-list partition, so that user's meeting streams are skipped. | User-to-meeting parent requesters; `test_error_handling.py` |
| Code `3001` | Ignore the affected resource when a meeting or webinar was deleted or no longer has report data. | Meeting, webinar, and report requesters with an explicit filter; deleted-meeting case in `test_error_handling.py` |
| Code `300` | Ignore the response. | `meeting_registrants` requester |
| HTTP `400` or `404` | Ignore the response; the affected stream can return no records. | Only the stream-specific requesters listed below |
| Token error `invalid_grant`, `invalid_client`, `invalid_request`, or `unsupported_grant_type` | Fail with a configuration error. | OAuth and Server-to-Server token authenticators; `test_oauth_and_config_migration.py`, `test_authenticator.py` |

The manifest explicitly ignores HTTP `400` responses on `meeting_polls`, `meeting_poll_results`, `meeting_registration_questions`, `webinars`, `webinar_panelists`, `webinar_registrants`, `webinar_absentees`, `webinar_polls`, `webinar_poll_results`, `webinar_registration_questions`, `webinar_tracking_sources`, `webinar_qna_results`, `report_meetings`, `report_meeting_participants`, `report_webinars`, and `report_webinar_participants`. It explicitly ignores HTTP `404` responses on `meeting_poll_results`, `webinars`, `webinar_panelists`, `webinar_registrants`, `webinar_absentees`, `webinar_polls`, `webinar_poll_results`, `webinar_qna_results`, `report_meetings`, and `report_meeting_participants`.

## Rate limits

`manifest.yaml` does not configure `api_budget` or `concurrency_level`, so the connector relies on the CDK's default backoff for HTTP `429` and `5xx` responses. Zoom applies limits per account and plan. Report endpoints and past-webinar absentees are Heavy APIs; see Zoom's [rate-limits documentation](https://developers.zoom.us/docs/api/rate-limits/). Concurrency is not configured yet; see [PR #83260](https://github.com/airbytehq/airbyte/pull/83260).

## Licence-gated streams

Webinar and report-webinar streams require the Zoom Webinars add-on. The test account has no webinar data, so `acceptance-test-config.yml` lists these streams as empty and bypassed in `basic_read`; each is covered by a mock-server test in `unit_tests/integration/`:

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

## Testing

`unit_tests/pyproject.toml` defines the pytest dependencies and no Poe tasks. Run the unit and mock-server tests with:

```bash
cd airbyte-integrations/connectors/source-zoom/unit_tests
poetry install
poetry run pytest
```

Acceptance tests need a populated Zoom account and Server-to-Server OAuth credentials. The GSM secret is `SECRET_SOURCE-ZOOM__CREDS`; the acceptance config reads the credentials from `secrets/config.json`.
