# Zoom

<HideInUI>

This page explains how to set up the Zoom source connector and which Zoom data it syncs.

</HideInUI>

## Prerequisites

- A Zoom account on a Pro plan or higher. Webinar and report-webinar streams also require the Zoom Webinars add-on.
- An account owner or admin who can create an account-level app and grant the required admin scopes.
- An account-level **General** app set to **Admin-managed** for OAuth2.0, or a **Server-to-Server OAuth** app.
- For OAuth2.0, have the app's **Client ID**, **Client Secret**, and **Refresh Token** ready. Airbyte Cloud obtains these when you authenticate.
- For Server-to-Server OAuth, have the **Account ID**, **Client ID**, and **Client Secret** ready.

Both authentication methods use an account-level app. For the scopes to grant, see [Required scopes](#required-scopes).

## Setup guide

### Step 1: Create a Zoom app

#### OAuth2.0 General app

1. Sign in to the [Zoom App Marketplace](https://marketplace.zoom.us/) and select **Develop** > **Build App**. Follow [Zoom's instructions for creating a General app](https://developers.zoom.us/docs/integrations/create/).
2. Create a **General** app and choose **Admin-managed**. A user-managed app cannot list account users.
3. If Airbyte asks for a redirect URL, add the URL it provides to the app's OAuth redirect URL and OAuth allow list.

#### Server-to-Server OAuth app

1. In the Zoom App Marketplace, select **Develop** > **Build App**, then create a **Server-to-Server OAuth** app using [Zoom's instructions](https://developers.zoom.us/docs/internal-apps/s2s-oauth/).
2. On the **App credentials** page, copy the **Account ID**, **Client ID**, and **Client Secret**.
3. On the **Scopes** page, add the [required scopes](#required-scopes).
4. Activate the app. Zoom does not issue access tokens for apps that are not activated.

#### Required scopes

Add these granular scopes to your Zoom app. If your app uses Zoom's classic scopes, add `user:read:admin`, `meeting:read:admin`, `webinar:read:admin`, and `report:read:admin` instead.

| Streams | Granular scopes |
| :------ | :-------------- |
| All streams (lists account users) | `user:read:list_users:admin` |
| `meetings`, `meeting_registrants`, `meeting_polls`, `meeting_poll_results`, `meeting_registration_questions`, `report_meetings`, `report_meeting_participants` (lists each user's meetings) | `meeting:read:list_meetings:admin` |
| `meetings` | `meeting:read:meeting:admin` |
| `meeting_registrants` | `meeting:read:list_registrants:admin` |
| `meeting_polls` | `meeting:read:list_polls:admin` |
| `meeting_poll_results` | `meeting:read:list_poll_results:admin` |
| `meeting_registration_questions` | `meeting:read:list_registration_questions:admin` |
| `webinars`, `webinar_panelists`, `webinar_registrants`, `webinar_absentees`, `webinar_polls`, `webinar_poll_results`, `webinar_registration_questions`, `webinar_tracking_sources`, `webinar_qna_results` | `webinar:read:list_webinars:admin`, `webinar:read:webinar:admin` |
| `webinar_panelists` | `webinar:read:list_panelists:admin` |
| `webinar_registrants` | `webinar:read:list_registrants:admin` |
| `webinar_absentees` | `webinar:read:list_absentees:admin` |
| `webinar_polls` | `webinar:read:list_polls:admin` |
| `webinar_poll_results` | `webinar:read:list_past_polls:admin` |
| `webinar_registration_questions` | `webinar:read:list_registration_questions:admin` |
| `webinar_tracking_sources` | `webinar:read:list_tracking_sources:admin` |
| `webinar_qna_results` | `webinar:read:past_qa:admin` |
| `report_meetings`, `report_meeting_participants` | `report:read:meeting:admin` |
| `report_meeting_participants` | `report:read:list_meeting_participants:admin` |
| `report_webinars`, `report_webinar_participants` | `report:read:webinar:admin` |
| `report_webinar_participants` | `report:read:list_webinar_participants:admin` |

### Step 2: Set up the Zoom connector in Airbyte

In Airbyte, create a Zoom source and select the authentication method that matches your app.

<!-- env:cloud -->

**For Airbyte Cloud:**

For OAuth2.0, select **OAuth2.0** and authorize your Zoom account:

1. Click **Authenticate your Zoom account** and sign in as a Zoom account owner or admin.

For Server-to-Server OAuth, select that authentication method and enter the app credentials:

1. Enter the **Account ID** from the app's **App credentials** page.
2. Enter the **Client ID** from the app's **App credentials** page.
3. Enter the **Client Secret** from the app's **App credentials** page.

<!-- /env:cloud -->

<!-- env:oss -->

**For Airbyte Open Source:**

For OAuth2.0, select **OAuth2.0** and enter the values for your admin-managed General app:

1. Enter the app's **Client ID**.
2. Enter the app's **Client Secret**.
3. Enter the **Refresh Token** issued after an account owner or admin authorizes your app.

For Server-to-Server OAuth, select that authentication method and enter the app credentials:

1. Enter the **Account ID** from the app's **App credentials** page.
2. Enter the **Client ID** from the app's **App credentials** page.
3. Enter the **Client Secret** from the app's **App credentials** page.

<!-- /env:oss -->

Zoom refresh tokens expire after 90 days. Re-authenticate if the source does not sync for that long. Zoom issues a new refresh token whenever the connector refreshes its access token, and the connector saves the new token to the source configuration. Authorizing the same Zoom app again, for example for a second source, revokes previously issued tokens. Server-to-Server OAuth apps do not use refresh tokens; the connector requests a new access token with the app credentials.

#### Configure the source with the Airbyte API or Terraform

Before version 1.4.0, Server-to-Server OAuth settings were top-level fields. Airbyte migrates existing configurations automatically. If you manage the source through the Airbyte API or Terraform, put the settings inside the `credentials` object:

- For OAuth2.0, set `auth_type` to `oauth2.0` and provide `client_id`, `client_secret`, and `refresh_token`.
- For Server-to-Server OAuth, set `auth_type` to `server_to_server` and provide `account_id`, `client_id`, and `client_secret`.

A configuration with only the old top-level `account_id`, `client_id`, `client_secret`, and `authorization_endpoint` fields is rejected. Once `credentials.auth_type` is set, the connector removes those top-level fields.

## Supported sync modes

| Sync mode | Supported? |
| :-------- | :--------- |
| Full Refresh | Yes |
| Incremental | No |
| Namespaces | No |

## Supported streams

The connector reads account users, then each user's meetings and webinars, and then details for those meetings and webinars.

| Stream | Endpoint | Primary key |
| :----- | :------- | :---------- |
| `users` | [GET /users](https://developers.zoom.us/docs/api/users/#tag/users/GET/users) | `id` |
| `meetings` | [GET /meetings/&#123;meetingId&#125;](https://developers.zoom.us/docs/api/meetings/#tag/meetings/GET/meetings/{meetingId}) | `id` |
| `meeting_registrants` | [GET /meetings/&#123;meetingId&#125;/registrants](https://developers.zoom.us/docs/api/meetings/#tag/invitation-&-registration/GET/meetings/{meetingId}/registrants) | `id` |
| `meeting_polls` | [GET /meetings/&#123;meetingId&#125;/polls](https://developers.zoom.us/docs/api/meetings/#tag/polls/GET/meetings/{meetingId}/polls) | `id` |
| `meeting_poll_results` | [GET /past_meetings/&#123;meetingId&#125;/polls](https://developers.zoom.us/docs/api/meetings/#tag/polls/GET/past_meetings/{meetingId}/polls) | — |
| `meeting_registration_questions` | [GET /meetings/&#123;meetingId&#125;/registrants/questions](https://developers.zoom.us/docs/api/meetings/#tag/invitation-&-registration/GET/meetings/{meetingId}/registrants/questions) | — |
| `webinars` | [GET /webinars/&#123;webinarId&#125;](https://developers.zoom.us/docs/api/meetings/#tag/webinars/GET/webinars/{webinarId}) | `id` |
| `webinar_panelists` | [GET /webinars/&#123;webinarId&#125;/panelists](https://developers.zoom.us/docs/api/meetings/#tag/webinars/GET/webinars/{webinarId}/panelists) | — |
| `webinar_registrants` | [GET /webinars/&#123;webinarId&#125;/registrants](https://developers.zoom.us/docs/api/meetings/#tag/webinars/GET/webinars/{webinarId}/registrants) | — |
| `webinar_absentees` | [GET /past_webinars/&#123;webinarId&#125;/absentees](https://developers.zoom.us/docs/api/meetings/#tag/webinars/GET/past_webinars/{webinarId}/absentees) | `id` |
| `webinar_polls` | [GET /webinars/&#123;webinarId&#125;/polls](https://developers.zoom.us/docs/api/meetings/#tag/webinars/GET/webinars/{webinarId}/polls) | — |
| `webinar_poll_results` | [GET /past_webinars/&#123;webinarId&#125;/polls](https://developers.zoom.us/docs/api/meetings/#tag/webinars/GET/past_webinars/{webinarId}/polls) | — |
| `webinar_registration_questions` | [GET /webinars/&#123;webinarId&#125;/registrants/questions](https://developers.zoom.us/docs/api/meetings/#tag/webinars/GET/webinars/{webinarId}/registrants/questions) | — |
| `webinar_tracking_sources` | [GET /webinars/&#123;webinarId&#125;/tracking_sources](https://developers.zoom.us/docs/api/meetings/#tag/webinars/GET/webinars/{webinarId}/tracking_sources) | `id` |
| `webinar_qna_results` | [GET /past_webinars/&#123;webinarId&#125;/qa](https://developers.zoom.us/docs/api/meetings/#tag/webinars/GET/past_webinars/{webinarId}/qa) | — |
| `report_meetings` | [GET /report/meetings/&#123;meetingId&#125;](https://developers.zoom.us/docs/api/meetings/#tag/reports/GET/report/meetings/{meetingId}) | `id` |
| `report_meeting_participants` | [GET /report/meetings/&#123;meetingId&#125;/participants](https://developers.zoom.us/docs/api/meetings/#tag/reports/GET/report/meetings/{meetingId}/participants) | `id` |
| `report_webinars` | [GET /report/webinars/&#123;webinarId&#125;](https://developers.zoom.us/docs/api/meetings/#tag/webinars/GET/report/webinars/{webinarId}) | — |
| `report_webinar_participants` | [GET /report/webinars/&#123;webinarId&#125;/participants](https://developers.zoom.us/docs/api/meetings/#tag/webinars/GET/report/webinars/{webinarId}/participants) | — |

## Limitations and troubleshooting

The connector currently supports Full Refresh only. Webinar streams require the Zoom Webinars add-on. Zoom may return no records for streams that your account or host does not have access to.

- If Zoom rejects the OAuth token request, the connection test or sync fails with a configuration error. For OAuth2.0, `invalid_grant` means the refresh token expired or was revoked; re-authenticate the source. `invalid_client` indicates an incorrect client ID or secret, or a deactivated app. For Server-to-Server OAuth, `invalid_request` means the Account ID is incorrect, and `unsupported_grant_type` means the selected authentication method does not match the app type. An S2S error message may say the refresh token was rejected even though S2S apps do not use refresh tokens.
- If Zoom returns code `4711`, the access token lacks a required scope. Add the missing scope from [Required scopes](#required-scopes) to the Zoom app and re-authenticate if you use OAuth2.0. Streams that ignore HTTP `400` responses return no records instead of reporting missing scopes.
- If Zoom rejects an expired access token with code `124`, the connector refreshes the token and retries the request.
- Zoom returns active users for the account. Meetings and webinars for inactive or pending users are not synced.
- Zoom's list endpoints return scheduled, unexpired meetings and webinars. Instant or expired meetings and webinars, and their associated registrants, polls, and reports, are not returned.
- If a user cannot host or schedule meetings, Zoom can return code `3161`; the connector skips that user's meeting partition instead of failing the sync.
- If a meeting or webinar was deleted or no longer has report data, Zoom can return code `3001`; the connector skips that resource.
- Some stream requesters ignore HTTP `400` or `404` responses, so those streams can return no records instead of failing. If an expected stream is empty, check your Zoom plan, the host's license, and the scopes on your app.

### Rate limits

Zoom applies [rate limits](https://developers.zoom.us/docs/api/rate-limits/) per account, shared across apps installed on that account, and limits depend on your plan. Free accounts have low daily limits, such as 1,000 requests per day for Heavy APIs. Report endpoints and `GET /past_webinars/{webinarId}/absentees` are Heavy APIs; on Pro and higher plans, they share a daily limit with resource-intensive APIs.

When Zoom returns HTTP `429`, the connector waits and retries the request. Because it makes several requests for each meeting and webinar, large accounts can reach daily limits. If syncs fail with rate-limit errors, deselect streams you do not need, especially report and webinar-absentee streams.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| :------ | :--------- | :------------------------------------------------------- | :--------------------------------------------------- |
| 1.4.1 | 2026-10-21 | [89087](https://github.com/airbytehq/airbyte/pull/89087) | Add registry metadata, spec titles and clearer Server-to-Server field descriptions |
| 1.4.0 | 2026-10-21 | [88359](https://github.com/airbytehq/airbyte/pull/88359) | Add OAuth2.0 authentication as the default, with automatic migration of existing Server-to-Server configurations |
| 1.3.2 | 2026-10-20 | [89459](https://github.com/airbytehq/airbyte/pull/89459) | Update dependencies |
| 1.3.1 | 2026-10-13 | [88881](https://github.com/airbytehq/airbyte/pull/88881) | Update dependencies |
| 1.3.0 | 2026-10-07 | [87561](https://github.com/airbytehq/airbyte/pull/87561) | Use the declarative OAuth authenticator, refresh tokens that expire mid-sync and report invalid credentials as configuration errors |
| 1.2.67 | 2026-10-07 | [87005](https://github.com/airbytehq/airbyte/pull/87005) | Fix sync failures on users without meeting hosting rights, deleted meetings and webinars, and webinar UUIDs containing slashes |
| 1.2.66 | 2026-10-06 | [88100](https://github.com/airbytehq/airbyte/pull/88100) | Update dependencies |
| 1.2.65 | 2026-09-29 | [87422](https://github.com/airbytehq/airbyte/pull/87422) | Update dependencies |
| 1.2.64 | 2026-09-22 | [86858](https://github.com/airbytehq/airbyte/pull/86858) | Update dependencies |
| 1.2.63 | 2026-09-15 | [86307](https://github.com/airbytehq/airbyte/pull/86307) | Update dependencies |
| 1.2.62 | 2026-09-08 | [85742](https://github.com/airbytehq/airbyte/pull/85742) | Update dependencies |
| 1.2.61 | 2026-08-18 | [84815](https://github.com/airbytehq/airbyte/pull/84815) | Update dependencies |
| 1.2.60 | 2026-08-11 | [84173](https://github.com/airbytehq/airbyte/pull/84173) | Update dependencies |
| 1.2.59 | 2026-07-28 | [83194](https://github.com/airbytehq/airbyte/pull/83194) | Update to CDK 7.23.8 and remove the Cloud version override |
| 1.2.58 | 2026-07-28 | [1082](https://github.com/airbytehq/airbyte-python-cdk/issues/1082) | Roll Cloud back to 1.2.56 |
| 1.2.57 | 2026-07-28 | [83156](https://github.com/airbytehq/airbyte/pull/83156) | Update dependencies |
| 1.2.56 | 2026-07-21 | [82672](https://github.com/airbytehq/airbyte/pull/82672) | Update dependencies |
| 1.2.55 | 2026-07-14 | [82073](https://github.com/airbytehq/airbyte/pull/82073) | Update dependencies |
| 1.2.54 | 2026-06-30 | [81304](https://github.com/airbytehq/airbyte/pull/81304) | Update dependencies |
| 1.2.53 | 2026-06-23 | [80722](https://github.com/airbytehq/airbyte/pull/80722) | Update dependencies |
| 1.2.52 | 2026-06-16 | [80114](https://github.com/airbytehq/airbyte/pull/80114) | Update dependencies |
| 1.2.51 | 2026-06-09 | [79582](https://github.com/airbytehq/airbyte/pull/79582) | Update dependencies |
| 1.2.50 | 2026-06-02 | [79076](https://github.com/airbytehq/airbyte/pull/79076) | Update dependencies |
| 1.2.49 | 2026-04-28 | [77500](https://github.com/airbytehq/airbyte/pull/77500) | Update dependencies |
| 1.2.48 | 2026-04-21 | [76821](https://github.com/airbytehq/airbyte/pull/76821) | Update dependencies |
| 1.2.47 | 2026-03-31 | [75837](https://github.com/airbytehq/airbyte/pull/75837) | Update dependencies |
| 1.2.46 | 2026-03-24 | [75052](https://github.com/airbytehq/airbyte/pull/75052) | Update dependencies |
| 1.2.45 | 2026-03-10 | [74448](https://github.com/airbytehq/airbyte/pull/74448) | Update dependencies |
| 1.2.44 | 2026-02-24 | [73991](https://github.com/airbytehq/airbyte/pull/73991) | Update dependencies |
| 1.2.43 | 2026-02-17 | [73592](https://github.com/airbytehq/airbyte/pull/73592) | Update dependencies |
| 1.2.42 | 2026-02-10 | [73211](https://github.com/airbytehq/airbyte/pull/73211) | Update dependencies |
| 1.2.41 | 2026-02-03 | [72082](https://github.com/airbytehq/airbyte/pull/72082) | Update dependencies |
| 1.2.40 | 2026-01-14 | [71380](https://github.com/airbytehq/airbyte/pull/71380) | Update dependencies |
| 1.2.39 | 2025-12-18 | [70796](https://github.com/airbytehq/airbyte/pull/70796) | Update dependencies |
| 1.2.38 | 2025-11-25 | [70145](https://github.com/airbytehq/airbyte/pull/70145) | Update dependencies |
| 1.2.37 | 2025-11-18 | [69428](https://github.com/airbytehq/airbyte/pull/69428) | Update dependencies |
| 1.2.36 | 2025-10-29 | [68840](https://github.com/airbytehq/airbyte/pull/68840) | Update dependencies |
| 1.2.35 | 2025-10-21 | [68502](https://github.com/airbytehq/airbyte/pull/68502) | Update dependencies |
| 1.2.34 | 2025-10-14 | [67984](https://github.com/airbytehq/airbyte/pull/67984) | Update dependencies |
| 1.2.33 | 2025-10-07 | [67477](https://github.com/airbytehq/airbyte/pull/67477) | Update dependencies |
| 1.2.32 | 2025-09-30 | [66942](https://github.com/airbytehq/airbyte/pull/66942) | Update dependencies |
| 1.2.31 | 2025-09-24 | [66312](https://github.com/airbytehq/airbyte/pull/66312) | Update dependencies |
| 1.2.30 | 2025-09-09 | [65697](https://github.com/airbytehq/airbyte/pull/65697) | Update dependencies |
| 1.2.29 | 2025-08-24 | [65399](https://github.com/airbytehq/airbyte/pull/65399) | Update dependencies |
| 1.2.28 | 2025-08-10 | [64833](https://github.com/airbytehq/airbyte/pull/64833) | Update dependencies |
| 1.2.27 | 2025-08-02 | [64316](https://github.com/airbytehq/airbyte/pull/64316) | Update dependencies |
| 1.2.26 | 2025-07-27 | [64092](https://github.com/airbytehq/airbyte/pull/64092) | Update dependencies |
| 1.2.25 | 2025-07-20 | [63671](https://github.com/airbytehq/airbyte/pull/63671) | Update dependencies |
| 1.2.24 | 2025-07-12 | [63182](https://github.com/airbytehq/airbyte/pull/63182) | Update dependencies |
| 1.2.23 | 2025-07-05 | [62729](https://github.com/airbytehq/airbyte/pull/62729) | Update dependencies |
| 1.2.22 | 2025-06-28 | [62221](https://github.com/airbytehq/airbyte/pull/62221) | Update dependencies |
| 1.2.21 | 2025-06-21 | [61777](https://github.com/airbytehq/airbyte/pull/61777) | Update dependencies |
| 1.2.20 | 2025-06-15 | [61205](https://github.com/airbytehq/airbyte/pull/61205) | Update dependencies |
| 1.2.19 | 2025-05-24 | [60763](https://github.com/airbytehq/airbyte/pull/60763) | Update dependencies |
| 1.2.18 | 2025-05-10 | [59936](https://github.com/airbytehq/airbyte/pull/59936) | Update dependencies |
| 1.2.17 | 2025-05-04 | [59545](https://github.com/airbytehq/airbyte/pull/59545) | Update dependencies |
| 1.2.16 | 2025-04-26 | [58534](https://github.com/airbytehq/airbyte/pull/58534) | Update dependencies |
| 1.2.15 | 2025-04-12 | [58032](https://github.com/airbytehq/airbyte/pull/58032) | Update dependencies |
| 1.2.14 | 2025-04-05 | [57394](https://github.com/airbytehq/airbyte/pull/57394) | Update dependencies |
| 1.2.13 | 2025-03-29 | [56840](https://github.com/airbytehq/airbyte/pull/56840) | Update dependencies |
| 1.2.12 | 2025-03-22 | [56339](https://github.com/airbytehq/airbyte/pull/56339) | Update dependencies |
| 1.2.11 | 2025-03-09 | [55666](https://github.com/airbytehq/airbyte/pull/55666) | Update dependencies |
| 1.2.10 | 2025-03-01 | [54642](https://github.com/airbytehq/airbyte/pull/54642) | Update dependencies |
| 1.2.9 | 2025-02-15 | [54113](https://github.com/airbytehq/airbyte/pull/54113) | Update dependencies |
| 1.2.8 | 2025-02-08 | [53595](https://github.com/airbytehq/airbyte/pull/53595) | Update dependencies |
| 1.2.7 | 2025-02-01 | [53122](https://github.com/airbytehq/airbyte/pull/53122) | Update dependencies |
| 1.2.6 | 2025-01-25 | [52548](https://github.com/airbytehq/airbyte/pull/52548) | Update dependencies |
| 1.2.5 | 2025-01-18 | [51931](https://github.com/airbytehq/airbyte/pull/51931) | Update dependencies |
| 1.2.4 | 2025-01-11 | [51467](https://github.com/airbytehq/airbyte/pull/51467) | Update dependencies |
| 1.2.3 | 2024-12-28 | [50835](https://github.com/airbytehq/airbyte/pull/50835) | Update dependencies |
| 1.2.2 | 2024-12-21 | [50394](https://github.com/airbytehq/airbyte/pull/50394) | Update dependencies |
| 1.2.1 | 2024-12-14 | [49445](https://github.com/airbytehq/airbyte/pull/49445) | Update dependencies |
| 1.2.0 | 2024-10-29 | [47299](https://github.com/airbytehq/airbyte/pull/47299) | Migrate to manifest only format |
| 1.1.22 | 2024-10-29 | [47755](https://github.com/airbytehq/airbyte/pull/47755) | Update dependencies |
| 1.1.21 | 2024-10-28 | [47094](https://github.com/airbytehq/airbyte/pull/47094) | Update dependencies |
| 1.1.20 | 2024-10-12 | [46824](https://github.com/airbytehq/airbyte/pull/46824) | Update dependencies |
| 1.1.19 | 2024-10-05 | [46412](https://github.com/airbytehq/airbyte/pull/46412) | Update dependencies |
| 1.1.18 | 2024-09-28 | [46196](https://github.com/airbytehq/airbyte/pull/46196) | Update dependencies |
| 1.1.17 | 2024-09-21 | [45737](https://github.com/airbytehq/airbyte/pull/45737) | Update dependencies |
| 1.1.16 | 2024-09-14 | [45523](https://github.com/airbytehq/airbyte/pull/45523) | Update dependencies |
| 1.1.15 | 2024-09-07 | [45220](https://github.com/airbytehq/airbyte/pull/45220) | Update dependencies |
| 1.1.14 | 2024-08-31 | [45037](https://github.com/airbytehq/airbyte/pull/45037) | Update dependencies |
| 1.1.13 | 2024-08-24 | [44676](https://github.com/airbytehq/airbyte/pull/44676) | Update dependencies |
| 1.1.12 | 2024-08-17 | [44249](https://github.com/airbytehq/airbyte/pull/44249) | Update dependencies |
| 1.1.11 | 2024-08-10 | [43578](https://github.com/airbytehq/airbyte/pull/43578) | Update dependencies |
| 1.1.10 | 2024-08-03 | [43149](https://github.com/airbytehq/airbyte/pull/43149) | Update dependencies |
| 1.1.9 | 2024-07-27 | [42652](https://github.com/airbytehq/airbyte/pull/42652) | Update dependencies |
| 1.1.8 | 2024-07-20 | [42212](https://github.com/airbytehq/airbyte/pull/42212) | Update dependencies |
| 1.1.7 | 2024-07-13 | [41813](https://github.com/airbytehq/airbyte/pull/41813) | Update dependencies |
| 1.1.6 | 2024-07-10 | [41486](https://github.com/airbytehq/airbyte/pull/41486) | Update dependencies |
| 1.1.5 | 2024-07-09 | [41316](https://github.com/airbytehq/airbyte/pull/41316) | Update dependencies |
| 1.1.4 | 2024-07-06 | [40986](https://github.com/airbytehq/airbyte/pull/40986) | Update dependencies |
| 1.1.3 | 2024-06-26 | [40509](https://github.com/airbytehq/airbyte/pull/40509) | Update dependencies |
| 1.1.2 | 2024-06-22 | [40141](https://github.com/airbytehq/airbyte/pull/40141) | Update dependencies |
| 1.1.1 | 2024-06-06 | [39279](https://github.com/airbytehq/airbyte/pull/39279) | [autopull] Upgrade base image to v1.2.2 |
| 1.1.0 | 2024-02-22 | [35369](https://github.com/airbytehq/airbyte/pull/35369) | Publish S2S Oauth connector with fixed authenticator |
| 1.0.0   | 2023-7-28  | [25308](https://github.com/airbytehq/airbyte/pull/25308) | Replace JWT Auth methods with server-to-server Oauth |
| 0.1.1   | 2022-11-30 | [19939](https://github.com/airbytehq/airbyte/pull/19939) | Upgrade CDK version to fix bugs with SubStreamSlicer |
| 0.1.0   | 2022-10-25 | [18179](https://github.com/airbytehq/airbyte/pull/18179) | Initial Release                                      |

</details>
