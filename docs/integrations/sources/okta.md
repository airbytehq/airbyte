# Okta

The Okta source connector syncs identity data (users, groups, roles, and system logs) from your [Okta](https://www.okta.com/) organization.

## Prerequisites

- An Okta organization and its domain. If your Okta URL is `https://MY_DOMAIN.okta.com/`, then `MY_DOMAIN` is your Okta domain. See [Find your Okta domain](https://developer.okta.com/docs/guides/find-your-domain/main/).
- Credentials for one of the three supported authentication methods (see below). The credentials must belong to an administrator with permission to read the resources you want to sync. API tokens inherit the privilege level of the admin who creates them.

## Setup guide

### Step 1: Set up authentication in Okta

The connector supports three authentication methods. All three work on both Airbyte Cloud and Airbyte Open Source.

#### API Token

Create an API token (SSWS token) in the Okta Admin Console under **Security > API > Tokens**. Record the token value when Okta displays it; you can't view it again later. See [Create an API token](https://developer.okta.com/docs/guides/create-an-api-token/main/).

Okta API tokens expire after 30 days of inactivity. If you restrict API calls to a network zone, make sure requests from Airbyte are allowed.

#### OAuth 2.0

Provide the **Client ID**, **Client Secret**, and a current **Refresh Token** for an OAuth 2.0 web app integration in your Okta org. The connector uses the refresh token to obtain new access tokens when they expire.

#### OAuth 2.0 with private key

Create an [API service app](https://developer.okta.com/docs/guides/implement-oauth-for-okta-serviceapp/main/) in your Okta org, register the public JSON Web Key (JWK) that corresponds to your PEM private key, and grant the app the [OAuth 2.0 scopes](https://developer.okta.com/docs/api/oauth2) for the resources you plan to sync (for example, `okta.users.read`, `okta.groups.read`, `okta.roles.read`, and `okta.logs.read`). You need:

- **Client ID**: the service app's client ID.
- **Key ID**: the `kid` of the registered JWK.
- **Private key**: the corresponding private key in PEM format.
- **Scope**: the granted scopes, separated by spaces.

### Step 2: Set up the Okta source in Airbyte

1. Log in to your Airbyte Cloud or Airbyte Open Source account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. On the source setup page, select **Okta** from the Source type dropdown and enter a name for the connector.
4. Enter your **Okta domain**. Enter only the domain part: if your Okta URL is `https://MY_DOMAIN.okta.com/`, enter `MY_DOMAIN`.
5. Enter a **Start Date** in the format `YYYY-MM-DDTHH:MM:SSZ`. Data before this date isn't replicated. If you leave this field empty, the connector syncs data from the last 7 days only.
6. Choose an authentication method and fill in its fields:
   - **API Token**: enter your **Personal API Token**.
   - **OAuth2.0**: enter your **Client ID**, **Client Secret**, and **Refresh Token**.
   - **OAuth 2.0 with private key**: enter your **Client ID**, **Key ID**, **Private key**, and **Scope**.
7. Click **Set up source**.

## Supported sync modes

The Okta source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- Full Refresh
- Incremental

## Supported streams

| Stream | Incremental | Notes |
|:-------|:------------|:------|
| [Users](https://developer.okta.com/docs/reference/api/users/#list-users) | Yes | Cursor: `lastUpdated` |
| [User Role Assignments](https://developer.okta.com/docs/reference/api/roles/#list-roles-assigned-to-a-user) | No | Roles assigned to each user |
| [Groups](https://developer.okta.com/docs/reference/api/groups/#list-groups) | Yes | Cursor: `lastUpdated` |
| [Group Members](https://developer.okta.com/docs/reference/api/groups/#list-group-members) | No | Members of each group |
| [Group Role Assignments](https://developer.okta.com/docs/reference/api/roles/#list-roles-assigned-to-a-group) | No | Roles assigned to each group |
| [System Log](https://developer.okta.com/docs/reference/api/system-log/#get-started) | Yes | Cursor: `published` |
| [Custom Roles](https://developer.okta.com/docs/reference/api/roles/#list-roles) | No |  |
| [Permissions](https://developer.okta.com/docs/reference/api/roles/#list-permissions) | No | Permissions of each custom role |
| [Resource Sets](https://developer.okta.com/docs/reference/api/roles/#list-resource-sets) | No |  |

## Performance considerations

The connector is subject to standard Okta [rate limits](https://developer.okta.com/docs/reference/rate-limits/). Rate limits vary by endpoint and by your Okta subscription.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| :------ | :--- | :----------- | :------ |
| 0.3.23 | 2026-08-28 | [85169](https://github.com/airbytehq/airbyte/pull/85169) | Remove legacy main.py from poetry package includes to fix Docker image build |
| 0.3.22 | 2026-08-26 | [85086](https://github.com/airbytehq/airbyte/pull/85086) | Support multiline input for private key |
| 0.3.21 | 2025-02-25 | [54167](https://github.com/airbytehq/airbyte/pull/54167) | Remove stream_state interpolation |
| 0.3.20 | 2025-02-01 | [52728](https://github.com/airbytehq/airbyte/pull/52728) | Update dependencies |
| 0.3.19 | 2025-01-25 | [52469](https://github.com/airbytehq/airbyte/pull/52469) | Update dependencies |
| 0.3.18 | 2025-01-18 | [51920](https://github.com/airbytehq/airbyte/pull/51920) | Update dependencies |
| 0.3.17 | 2025-01-11 | [51170](https://github.com/airbytehq/airbyte/pull/51170) | Update dependencies |
| 0.3.16 | 2025-01-04 | [50899](https://github.com/airbytehq/airbyte/pull/50899) | Update dependencies |
| 0.3.15 | 2024-12-28 | [50670](https://github.com/airbytehq/airbyte/pull/50670) | Update dependencies |
| 0.3.14 | 2024-12-21 | [50073](https://github.com/airbytehq/airbyte/pull/50073) | Update dependencies |
| 0.3.13 | 2024-12-14 | [49264](https://github.com/airbytehq/airbyte/pull/49264) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.3.12 | 2024-12-12 | [49145](https://github.com/airbytehq/airbyte/pull/49145) | Update dependencies |
| 0.3.11 | 2024-11-04 | [47900](https://github.com/airbytehq/airbyte/pull/47900) | Update dependencies |
| 0.3.10 | 2024-10-28 | [47058](https://github.com/airbytehq/airbyte/pull/47058) | Update dependencies |
| 0.3.9 | 2024-10-12 | [46804](https://github.com/airbytehq/airbyte/pull/46804) | Update dependencies |
| 0.3.8 | 2024-10-05 | [46481](https://github.com/airbytehq/airbyte/pull/46481) | Update dependencies |
| 0.3.7 | 2024-09-28 | [46148](https://github.com/airbytehq/airbyte/pull/46148) | Update dependencies |
| 0.3.6 | 2024-09-21 | [45763](https://github.com/airbytehq/airbyte/pull/45763) | Update dependencies |
| 0.3.5 | 2024-09-14 | [45543](https://github.com/airbytehq/airbyte/pull/45543) | Update dependencies |
| 0.3.4 | 2024-09-07 | [45319](https://github.com/airbytehq/airbyte/pull/45319) | Update dependencies |
| 0.3.3 | 2024-08-31 | [44977](https://github.com/airbytehq/airbyte/pull/44977) | Update dependencies |
| 0.3.2 | 2024-08-24 | [44741](https://github.com/airbytehq/airbyte/pull/44741) | Update dependencies |
| 0.3.1 | 2024-08-17 | [44332](https://github.com/airbytehq/airbyte/pull/44332) | Update dependencies |
| 0.3.0 | 2024-08-13 | [43382](https://github.com/airbytehq/airbyte/pull/43382) | Support OAuth 2.0 with private key |
| 0.2.11 | 2024-08-12 | [43820](https://github.com/airbytehq/airbyte/pull/43820) | Update dependencies |
| 0.2.10 | 2024-08-10 | [43672](https://github.com/airbytehq/airbyte/pull/43672) | Update dependencies |
| 0.2.9 | 2024-08-03 | [43279](https://github.com/airbytehq/airbyte/pull/43279) | Update dependencies |
| 0.2.8 | 2024-07-27 | [42739](https://github.com/airbytehq/airbyte/pull/42739) | Update dependencies |
| 0.2.7 | 2024-07-20 | [42284](https://github.com/airbytehq/airbyte/pull/42284) | Update dependencies |
| 0.2.6 | 2024-07-13 | [41756](https://github.com/airbytehq/airbyte/pull/41756) | Update dependencies |
| 0.2.5 | 2024-07-10 | [41269](https://github.com/airbytehq/airbyte/pull/41269) | Update dependencies |
| 0.2.4 | 2024-07-06 | [40904](https://github.com/airbytehq/airbyte/pull/40904) | Update dependencies |
| 0.2.3 | 2024-06-25 | [40316](https://github.com/airbytehq/airbyte/pull/40316) | Update dependencies |
| 0.2.2 | 2024-06-22 | [40002](https://github.com/airbytehq/airbyte/pull/40002) | Update dependencies |
| 0.2.1 | 2024-06-04 | [39016](https://github.com/airbytehq/airbyte/pull/39016) | [autopull] Upgrade base image to v1.2.1 |
| 0.2.0 | 2024-05-16 | [36509](https://github.com/airbytehq/airbyte/pull/36509) | Migrate to Low Code |
| 0.1.16 | 2023-07-07 | [20833](https://github.com/airbytehq/airbyte/pull/20833) | Fix infinite loop for GroupMembers stream |
| 0.1.15 | 2023-06-20 | [27533](https://github.com/airbytehq/airbyte/pull/27533) | Fixed group member stream and resource sets stream pagination |
| 0.1.14 | 2022-12-24 | [20877](https://github.com/airbytehq/airbyte/pull/20877) | Disabled OAuth2.0 authorization method |
| 0.1.13 | 2022-08-12 | [14700](https://github.com/airbytehq/airbyte/pull/14700) | Add resource sets |
| 0.1.12 | 2022-08-05 | [15050](https://github.com/airbytehq/airbyte/pull/15050) | Add parameter `start_date` for Logs stream |
| 0.1.11 | 2022-08-03 | [14739](https://github.com/airbytehq/airbyte/pull/14739) | Add permissions for custom roles |
| 0.1.10 | 2022-08-01 | [15179](https://github.com/airbytehq/airbyte/pull/15179) | Fix broken schemas for all streams |
| 0.1.9 | 2022-07-25 | [15001](https://github.com/airbytehq/airbyte/pull/15001) | Return deprovisioned users |
| 0.1.8 | 2022-07-19 | [14710](https://github.com/airbytehq/airbyte/pull/14710) | Implement OAuth2.0 authorization method |
| 0.1.7 | 2022-07-13 | [14556](https://github.com/airbytehq/airbyte/pull/14556) | Add User_Role_Assignments and Group_Role_Assignments streams (full fetch only) |
| 0.1.6 | 2022-07-11 | [14610](https://github.com/airbytehq/airbyte/pull/14610) | Add custom roles stream |
| 0.1.5 | 2022-07-04 | [14380](https://github.com/airbytehq/airbyte/pull/14380) | Add Group_Members stream to okta source |
| 0.1.4 | 2021-11-02 | [7584](https://github.com/airbytehq/airbyte/pull/7584) | Fix incremental params for log stream |
| 0.1.3 | 2021-09-08 | [5905](https://github.com/airbytehq/airbyte/pull/5905) | Fix incremental stream defect |
| 0.1.2 | 2021-07-01 | [4456](https://github.com/airbytehq/airbyte/pull/4456) | Fix infinite pagination in logs stream |
| 0.1.1 | 2021-06-09 | [3973](https://github.com/airbytehq/airbyte/pull/3973) | Add `AIRBYTE_ENTRYPOINT` env variable for kubernetes support |
| 0.1.0 | 2021-05-30 | [3563](https://github.com/airbytehq/airbyte/pull/3563) | Initial Release |

</details>
