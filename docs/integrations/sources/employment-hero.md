# Employment Hero

This page contains the setup guide and reference information for the Employment Hero source connector. The connector syncs HR data, including organisations, employees, leave requests, teams, policies, certifications, custom fields, and pay details, from the [Employment Hero API](https://developer.employmenthero.com/api-references/introduction).

## Prerequisites

- An Employment Hero **Platinum** subscription or above. Employment Hero only offers API access on these plans.
- Access to the Employment Hero **Developer Portal**, so you can create an OAuth 2.0 application.
- An Employment Hero account to authorize the application. Employment Hero recommends an admin or owner account, because the connector can only read data that the authorizing account has permission to see.
- An OAuth 2.0 client that supports the authorization code flow with PKCE, such as Postman, to obtain a refresh token.

## Authentication setup

The Employment Hero API uses OAuth 2.0, and access tokens expire after 15 minutes. The connector authenticates with your OAuth application's **Client ID**, **Client Secret**, and a **Refresh Token**. It exchanges the refresh token for a new access token at `https://oauth.employmenthero.com/oauth2/token` whenever it needs one. For details, see the [Employment Hero authentication docs](https://developer.employmenthero.com/api-references/authentication).

### Step 1: Create an OAuth 2.0 application

1. Sign in to Employment Hero and open the **Developer Portal** from the menu under your profile name in the top right corner. You can also go directly to `https://secure.employmenthero.com/app/v2/organisations/<your-org-id>/developer_portal/api`.
2. Select **Add Application** and give the application a name.
3. Select the read scopes for every resource you plan to sync. Scopes use the format `urn:mainapp:<resource>:read`, for example `urn:mainapp:organisations:read` and `urn:mainapp:employees:read`.

   :::warning
   You can't change an application's scopes after you create it. If you need more scopes later, create a new application.
   :::

4. Enter a redirect URI. Employment Hero requires HTTPS redirect URIs. If you use Postman to obtain the refresh token, enter `https://oauth.pstmn.io/v1/callback`.
5. Copy the **Client ID** and **Client Secret** from the application details page.

### Step 2: Obtain a refresh token

Since 2026-09-30, Employment Hero requires PKCE for all authorization flows. A refresh token works only if it was issued through the PKCE flow, so a refresh token you obtained without PKCE before that date fails.

To obtain a refresh token with Postman:

1. Open a new request in Postman, go to the **Authorization** tab, and select **OAuth 2.0**.
2. Set **Grant Type** to `Authorization Code (With PKCE)` and **Code Challenge Method** to `SHA-256`.
3. Set **Auth URL** to `https://oauth.employmenthero.com/oauth2/authorize` and **Access Token URL** to `https://oauth.employmenthero.com/oauth2/token`.
4. Enter your Client ID and Client Secret, and set **Client Authentication** to **Send client credentials in body**. Leave **Scope** and **State** blank.
5. Select **Get New Access Token**, sign in to Employment Hero, and approve the request in your browser.
6. Copy the `refresh_token` value from the token response. Don't use the `access_token`, which expires after 15 minutes.

Employment Hero refresh tokens don't currently expire, and you can reuse the same refresh token for every token request.

If your account belongs to more than one organisation that enforces single sign-on (SSO), each token can include only one SSO organisation. Organisations that don't enforce SSO are included automatically. To sync more than one SSO organisation, authorize each one separately and use each resulting refresh token in its own source.

### Step 3: Set up the source in Airbyte

1. Enter the **Client ID**, **Client Secret**, and **Refresh Token**.
2. Optional: To sync the `employee_certifications`, `pay_details`, and `employee_custom_fields` streams, enter **Organization ID** and **Employees ID** values. See [Organization and employee IDs](#organization-and-employee-ids).
3. Select **Set up source**.

## Organization and employee IDs

Most streams discover their parent records automatically. The connector reads the `organisations` stream and then requests employees, leave requests, teams, policies, certifications, and custom fields for every organisation it returns.

The `employee_certifications`, `pay_details`, and `employee_custom_fields` streams work differently. They only read data for the IDs you enter in the **Organization ID** (`organization_configids`) and **Employees ID** (`employees_configids`) fields. The connector requests every combination of the organisation IDs and employee IDs you enter, so each employee ID is requested under each organisation ID.

To find these IDs, sync the `organisations` and `employees` streams first and copy the `id` values from the results.

## Configuration

| Input | Type | Description |
| --- | --- | --- |
| `client_id` | `string` | Client ID of the OAuth 2.0 application created in the Employment Hero Developer Portal. |
| `client_secret` | `string` | Client Secret of the OAuth 2.0 application created in the Employment Hero Developer Portal. |
| `refresh_token` | `string` | Refresh token obtained from the Employment Hero OAuth 2.0 authorization code flow with PKCE. |
| `organization_configids` | `array` | Organization ID. IDs of the organisations to read the `employee_certifications`, `pay_details`, and `employee_custom_fields` streams for. Find them in the `organisations` stream. |
| `employees_configids` | `array` | Employees ID. IDs of the employees to read the `employee_certifications`, `pay_details`, and `employee_custom_fields` streams for. Find them in the `employees` stream. |

## Supported streams

All streams support the **Full Refresh** sync mode only. Incremental sync isn't supported.

| Stream name | Employment Hero endpoint | Primary key |
| --- | --- | --- |
| organisations | `/api/v1/organisations` | id |
| employees | `/api/v1/organisations/{organisation_id}/employees` | id |
| leave_requests | `/api/v1/organisations/{organisation_id}/leave_requests` | id |
| employee_certifications | `/api/v1/organisations/{organisation_id}/employees/{employee_id}/certifications` | id |
| pay_details | `/api/v1/organisations/{organisation_id}/employees/{employee_id}/pay_details` | id |
| teams | `/api/v1/organisations/{organisation_id}/teams` | id |
| policies | `/api/v1/organisations/{organisation_id}/policies` | id |
| certifications | `/api/v1/organisations/{organisation_id}/certifications` | id |
| custom_fields | `/api/v1/organisations/{organisation_id}/custom_fields` | id |
| employee_custom_fields | `/api/v1/organisations/{organisation_id}/employees/{employee_id}/custom_fields` | id |

The Employment Hero interface calls teams "Groups," but the API and the `teams` stream still use the term "teams."

## Limitations

- **Rate limits**: Employment Hero allows 20 requests per second and 100 requests per minute. The connector requests 20 records per page and retries rate-limited (HTTP 429) responses up to three times with exponential backoff.
- **Permissions**: The connector only returns data that the account you authorized with can access. A non-admin account can return partial data or `403 Forbidden` errors.
- **Regional fields**: Some fields only apply to employees in specific regions (Australia, Malaysia, Singapore, New Zealand, United Kingdom, or Canada). Employment Hero omits these fields from records for employees outside the matching region.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| ------------------ | ------------ | --- | ---------------- |
| 0.1.0 | 2026-10-09 | [88211](https://github.com/airbytehq/airbyte/pull/88211) | Replace static access-token auth with OAuth 2.0 refresh-token flow (access tokens expire after 15 minutes) |
| 0.0.66 | 2026-10-06 | [87860](https://github.com/airbytehq/airbyte/pull/87860) | Update dependencies |
| 0.0.65 | 2026-09-29 | [87167](https://github.com/airbytehq/airbyte/pull/87167) | Update dependencies |
| 0.0.64 | 2026-09-22 | [86634](https://github.com/airbytehq/airbyte/pull/86634) | Update dependencies |
| 0.0.63 | 2026-09-15 | [86035](https://github.com/airbytehq/airbyte/pull/86035) | Update dependencies |
| 0.0.62 | 2026-09-08 | [85480](https://github.com/airbytehq/airbyte/pull/85480) | Update dependencies |
| 0.0.61 | 2026-08-18 | [84556](https://github.com/airbytehq/airbyte/pull/84556) | Update dependencies |
| 0.0.60 | 2026-08-11 | [83920](https://github.com/airbytehq/airbyte/pull/83920) | Update dependencies |
| 0.0.59 | 2026-08-04 | [83450](https://github.com/airbytehq/airbyte/pull/83450) | Update dependencies |
| 0.0.58 | 2026-07-28 | [82927](https://github.com/airbytehq/airbyte/pull/82927) | Update dependencies |
| 0.0.57 | 2026-07-21 | [82420](https://github.com/airbytehq/airbyte/pull/82420) | Update dependencies |
| 0.0.56 | 2026-07-14 | [81805](https://github.com/airbytehq/airbyte/pull/81805) | Update dependencies |
| 0.0.55 | 2026-06-30 | [81067](https://github.com/airbytehq/airbyte/pull/81067) | Update dependencies |
| 0.0.54 | 2026-06-23 | [80448](https://github.com/airbytehq/airbyte/pull/80448) | Update dependencies |
| 0.0.53 | 2026-06-16 | [79850](https://github.com/airbytehq/airbyte/pull/79850) | Update dependencies |
| 0.0.52 | 2026-06-09 | [79324](https://github.com/airbytehq/airbyte/pull/79324) | Update dependencies |
| 0.0.51 | 2026-06-02 | [78697](https://github.com/airbytehq/airbyte/pull/78697) | Update dependencies |
| 0.0.50 | 2026-04-28 | [77200](https://github.com/airbytehq/airbyte/pull/77200) | Update dependencies |
| 0.0.49 | 2026-04-21 | [76563](https://github.com/airbytehq/airbyte/pull/76563) | Update dependencies |
| 0.0.48 | 2026-03-31 | [75776](https://github.com/airbytehq/airbyte/pull/75776) | Update dependencies |
| 0.0.47 | 2026-03-24 | [75338](https://github.com/airbytehq/airbyte/pull/75338) | Update dependencies |
| 0.0.46 | 2026-03-10 | [74440](https://github.com/airbytehq/airbyte/pull/74440) | Update dependencies |
| 0.0.45 | 2026-02-24 | [73901](https://github.com/airbytehq/airbyte/pull/73901) | Update dependencies |
| 0.0.44 | 2026-02-17 | [73460](https://github.com/airbytehq/airbyte/pull/73460) | Update dependencies |
| 0.0.43 | 2026-02-10 | [73012](https://github.com/airbytehq/airbyte/pull/73012) | Update dependencies |
| 0.0.42 | 2026-01-20 | [71917](https://github.com/airbytehq/airbyte/pull/71917) | Update dependencies |
| 0.0.41 | 2026-01-14 | [71556](https://github.com/airbytehq/airbyte/pull/71556) | Update dependencies |
| 0.0.40 | 2025-12-18 | [70568](https://github.com/airbytehq/airbyte/pull/70568) | Update dependencies |
| 0.0.39 | 2025-11-25 | [70162](https://github.com/airbytehq/airbyte/pull/70162) | Update dependencies |
| 0.0.38 | 2025-11-18 | [69391](https://github.com/airbytehq/airbyte/pull/69391) | Update dependencies |
| 0.0.37 | 2025-10-29 | [68707](https://github.com/airbytehq/airbyte/pull/68707) | Update dependencies |
| 0.0.36 | 2025-10-21 | [68566](https://github.com/airbytehq/airbyte/pull/68566) | Update dependencies |
| 0.0.35 | 2025-10-14 | [67739](https://github.com/airbytehq/airbyte/pull/67739) | Update dependencies |
| 0.0.34 | 2025-10-07 | [67270](https://github.com/airbytehq/airbyte/pull/67270) | Update dependencies |
| 0.0.33 | 2025-09-30 | [65842](https://github.com/airbytehq/airbyte/pull/65842) | Update dependencies |
| 0.0.32 | 2025-08-23 | [65290](https://github.com/airbytehq/airbyte/pull/65290) | Update dependencies |
| 0.0.31 | 2025-08-09 | [64694](https://github.com/airbytehq/airbyte/pull/64694) | Update dependencies |
| 0.0.30 | 2025-08-02 | [64327](https://github.com/airbytehq/airbyte/pull/64327) | Update dependencies |
| 0.0.29 | 2025-07-26 | [64022](https://github.com/airbytehq/airbyte/pull/64022) | Update dependencies |
| 0.0.28 | 2025-07-19 | [63552](https://github.com/airbytehq/airbyte/pull/63552) | Update dependencies |
| 0.0.27 | 2025-07-12 | [63015](https://github.com/airbytehq/airbyte/pull/63015) | Update dependencies |
| 0.0.26 | 2025-07-05 | [62795](https://github.com/airbytehq/airbyte/pull/62795) | Update dependencies |
| 0.0.25 | 2025-06-28 | [62339](https://github.com/airbytehq/airbyte/pull/62339) | Update dependencies |
| 0.0.24 | 2025-06-22 | [61989](https://github.com/airbytehq/airbyte/pull/61989) | Update dependencies |
| 0.0.23 | 2025-06-14 | [61251](https://github.com/airbytehq/airbyte/pull/61251) | Update dependencies |
| 0.0.22 | 2025-05-24 | [60021](https://github.com/airbytehq/airbyte/pull/60021) | Update dependencies |
| 0.0.21 | 2025-05-03 | [59446](https://github.com/airbytehq/airbyte/pull/59446) | Update dependencies |
| 0.0.20 | 2025-04-26 | [58910](https://github.com/airbytehq/airbyte/pull/58910) | Update dependencies |
| 0.0.19 | 2025-04-19 | [57832](https://github.com/airbytehq/airbyte/pull/57832) | Update dependencies |
| 0.0.18 | 2025-04-05 | [57283](https://github.com/airbytehq/airbyte/pull/57283) | Update dependencies |
| 0.0.17 | 2025-03-29 | [56521](https://github.com/airbytehq/airbyte/pull/56521) | Update dependencies |
| 0.0.16 | 2025-03-22 | [55970](https://github.com/airbytehq/airbyte/pull/55970) | Update dependencies |
| 0.0.15 | 2025-03-08 | [55320](https://github.com/airbytehq/airbyte/pull/55320) | Update dependencies |
| 0.0.14 | 2025-03-01 | [54455](https://github.com/airbytehq/airbyte/pull/54455) | Update dependencies |
| 0.0.13 | 2025-02-15 | [53716](https://github.com/airbytehq/airbyte/pull/53716) | Update dependencies |
| 0.0.12 | 2025-02-08 | [53322](https://github.com/airbytehq/airbyte/pull/53322) | Update dependencies |
| 0.0.11 | 2025-02-01 | [52817](https://github.com/airbytehq/airbyte/pull/52817) | Update dependencies |
| 0.0.10 | 2025-01-25 | [52347](https://github.com/airbytehq/airbyte/pull/52347) | Update dependencies |
| 0.0.9 | 2025-01-18 | [51681](https://github.com/airbytehq/airbyte/pull/51681) | Update dependencies |
| 0.0.8 | 2025-01-11 | [51081](https://github.com/airbytehq/airbyte/pull/51081) | Update dependencies |
| 0.0.7 | 2024-12-28 | [50526](https://github.com/airbytehq/airbyte/pull/50526) | Update dependencies |
| 0.0.6 | 2024-12-21 | [50024](https://github.com/airbytehq/airbyte/pull/50024) | Update dependencies |
| 0.0.5 | 2024-12-14 | [49489](https://github.com/airbytehq/airbyte/pull/49489) | Update dependencies |
| 0.0.4 | 2024-12-12 | [49190](https://github.com/airbytehq/airbyte/pull/49190) | Update dependencies |
| 0.0.3 | 2024-11-04 | [47819](https://github.com/airbytehq/airbyte/pull/47819) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47632](https://github.com/airbytehq/airbyte/pull/47632) | Update dependencies |
| 0.0.1 | 2024-09-25 | [45888](https://github.com/airbytehq/airbyte/pull/45888) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
