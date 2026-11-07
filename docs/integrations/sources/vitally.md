# Vitally

This page contains the setup guide and reference information for the [Vitally](https://www.vitally.io/) source connector. The connector reads data from the [Vitally REST API](https://docs.vitally.io/en/articles/9880649-rest-api-overview).

## Prerequisites

- A Vitally account with access to the **Vitally REST API** integration settings.
- A Vitally REST API secret token. To create one:
  1. In Vitally, select your account logo in the top left, then open **Settings**.
  2. Under **Connectors**, select **Integrations**, then select **Vitally REST API**.
  3. If the integration isn't enabled, turn on the toggle in the top right.
  4. Copy the **Secret Token** for an existing API key, or create a new key and copy its secret token.
- Your Vitally subdomain, if your organization uses one. This is the `yoursubdomain` part of the URL you use to sign in to Vitally, for example `https://yoursubdomain.vitally.io`.

The connector only supports the Vitally US data center (`rest.vitally.io`). Accounts hosted in the Vitally EU data center (`rest.vitally-eu.io`) aren't supported.

## Set up the Vitally connector in Airbyte

1. In Airbyte, create a new source and select **Vitally**.
2. For **Custom Subdomain**, enter only your Vitally subdomain, for example `yoursubdomain`. The connector sends requests to `https://yoursubdomain.rest.vitally.io`. If your organization doesn't use a subdomain, leave this field empty and the connector sends requests to `https://rest.vitally.io`.
3. For **Status**, select which accounts to sync in the `accounts` stream:
   - `active`: tracked accounts that haven't churned.
   - `churned`: tracked accounts that have churned.
   - `activeOrChurned`: all tracked accounts.
4. For **Secret Token**, paste the secret token you copied from Vitally. It starts with `sk_live_`.
5. **Basic Auth Header** is optional. The connector authenticates with HTTP basic authentication, using the secret token as the username and this field, if set, as the password.
6. Select **Set up source**.

## Supported sync modes

The Vitally source connector supports the following sync modes:

- [Full Refresh - Overwrite](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite)
- [Full Refresh - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append)

The connector doesn't support incremental syncs. Each sync reads every record from each selected stream.

## Supported streams

| Stream | Vitally endpoint | Notes |
| :----- | :--------------- | :---- |
| `accounts` | [Accounts](https://docs.vitally.io/en/articles/9880654-rest-api-accounts) | Filtered by the **Status** setting. |
| `admins` | [Admins](https://docs.vitally.io/en/articles/9880663-rest-api-admins) | |
| `conversations` | [Conversations](https://docs.vitally.io/en/articles/9880665-rest-api-conversations) | |
| `notes` | [Notes](https://docs.vitally.io/en/articles/9880672-rest-api-notes) | |
| `tasks` | [Tasks](https://docs.vitally.io/en/articles/9880855-rest-api-tasks) | |
| `users` | [Users](https://docs.vitally.io/en/articles/9880661-rest-api-users) | |

All streams use `id` as the primary key.

## Limitations and performance considerations

- Vitally limits REST API traffic to 1,000 requests per minute by default. The connector requests up to 100 records per page, which is the maximum Vitally allows.
- The connector doesn't set Vitally's `sortBy` parameter, so Vitally returns records sorted by `updatedAt`. According to [Vitally's pagination documentation](https://docs.vitally.io/en/articles/9880649-rest-api-overview), if records change while a sync is paginating, the results can contain duplicates or gaps.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                     |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------ |
| 0.4.4 | 2026-09-30 | [81345](https://github.com/airbytehq/airbyte/pull/81345) | Add missing `airbyte_secret` flag to `secret_token` spec field |
| 0.4.3 | 2026-06-02 | [79008](https://github.com/airbytehq/airbyte/pull/79008) | Update dependencies |
| 0.4.2 | 2025-05-24 | [60783](https://github.com/airbytehq/airbyte/pull/60783) | Update dependencies |
| 0.4.1 | 2025-05-10 | [59942](https://github.com/airbytehq/airbyte/pull/59942) | Update dependencies |
| 0.4.0 | 2025-05-05 | [58062](https://github.com/airbytehq/airbyte/pull/58062) | Fix subdomain parameter config |
| 0.3.10 | 2025-05-04 | [59561](https://github.com/airbytehq/airbyte/pull/59561) | Update dependencies |
| 0.3.9 | 2025-04-26 | [58951](https://github.com/airbytehq/airbyte/pull/58951) | Update dependencies |
| 0.3.8 | 2025-04-20 | [58018](https://github.com/airbytehq/airbyte/pull/58018) | Update dependencies |
| 0.3.7 | 2025-04-05 | [57478](https://github.com/airbytehq/airbyte/pull/57478) | Update dependencies |
| 0.3.6 | 2025-03-29 | [56894](https://github.com/airbytehq/airbyte/pull/56894) | Update dependencies |
| 0.3.5 | 2025-03-22 | [56255](https://github.com/airbytehq/airbyte/pull/56255) | Update dependencies |
| 0.3.4 | 2025-03-08 | [55622](https://github.com/airbytehq/airbyte/pull/55622) | Update dependencies |
| 0.3.3 | 2025-03-01 | [55090](https://github.com/airbytehq/airbyte/pull/55090) | Update dependencies |
| 0.3.2 | 2025-02-22 | [54500](https://github.com/airbytehq/airbyte/pull/54500) | Update dependencies |
| 0.3.1 | 2025-02-15 | [47470](https://github.com/airbytehq/airbyte/pull/47470) | Update dependencies |
| 0.3.0 | 2025-02-12 | [53648](https://github.com/airbytehq/airbyte/pull/53648) | Add support for custom domain. |
| 0.2.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 0.2.0 | 2024-08-14 | [44049](https://github.com/airbytehq/airbyte/pull/44049) | Refactor connector to manifest-only format |
| 0.1.13 | 2024-08-12 | [43850](https://github.com/airbytehq/airbyte/pull/43850) | Update dependencies |
| 0.1.12 | 2024-08-10 | [43505](https://github.com/airbytehq/airbyte/pull/43505) | Update dependencies |
| 0.1.11 | 2024-08-03 | [43189](https://github.com/airbytehq/airbyte/pull/43189) | Update dependencies |
| 0.1.10 | 2024-07-27 | [42607](https://github.com/airbytehq/airbyte/pull/42607) | Update dependencies |
| 0.1.9 | 2024-07-20 | [41877](https://github.com/airbytehq/airbyte/pull/41877) | Update dependencies |
| 0.1.8 | 2024-07-10 | [41378](https://github.com/airbytehq/airbyte/pull/41378) | Update dependencies |
| 0.1.7 | 2024-07-09 | [41223](https://github.com/airbytehq/airbyte/pull/41223) | Update dependencies |
| 0.1.6 | 2024-07-06 | [40808](https://github.com/airbytehq/airbyte/pull/40808) | Update dependencies |
| 0.1.5 | 2024-06-25 | [40287](https://github.com/airbytehq/airbyte/pull/40287) | Update dependencies |
| 0.1.4 | 2024-06-22 | [40189](https://github.com/airbytehq/airbyte/pull/40189) | Update dependencies |
| 0.1.3 | 2024-06-25 | [38605](https://github.com/airbytehq/airbyte/pull/38605) | Make compatible with builder |
| 0.1.2 | 2024-06-06 | [39203](https://github.com/airbytehq/airbyte/pull/39203) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.1 | 2024-05-20 | [38446](https://github.com/airbytehq/airbyte/pull/38446) | [autopull] base image + poetry + up_to_date |
| 0.1.0 | 2022-10-27 | [18545](https://github.com/airbytehq/airbyte/pull/18545) | Add Vitally Source Connector |

</details>
