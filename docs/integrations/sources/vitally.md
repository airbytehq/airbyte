# Vitally

## Sync overview

The Vitally source supports Full Refresh only.

This source can sync data from the [Vitally REST API](https://docs.vitally.io/en/articles/9880649-rest-api-overview).

### Output schema

This source syncs the following streams. Each stream uses `id` as its primary key.

- [Accounts](https://docs.vitally.io/pushing-data-to-vitally/rest-api/accounts)
- [Admins](https://docs.vitally.io/pushing-data-to-vitally/rest-api/admins)
- [Conversations](https://docs.vitally.io/pushing-data-to-vitally/rest-api/conversations)
- [Notes](https://docs.vitally.io/pushing-data-to-vitally/rest-api/notes)
- [Tasks](https://docs.vitally.io/pushing-data-to-vitally/rest-api/tasks)
- [Users](https://docs.vitally.io/pushing-data-to-vitally/rest-api/users)

### Features

| Feature                   | Supported?\(Yes/No\) | Notes |
| :------------------------ | :------------------- | :---- |
| Full Refresh Sync         | Yes                  |       |
| Incremental - Append Sync | No                   |       |
| Namespaces                | No                   |       |

### Performance considerations

Vitally's [REST API documentation](https://docs.vitally.io/en/articles/9880649-rest-api-overview) specifies a default limit of 1,000 requests per minute. The connector requests 100 records per page and follows the `next` cursor.

The connector doesn't set `sortBy`, so Vitally uses its default `updatedAt` ordering. Records that change while a sync is paginating can cause duplicates or gaps.

## Requirements

You need a Vitally REST API secret token. In Vitally, open **Settings** > **Integrations** under **Connectors**, select **Vitally REST API**, and enable the integration. Copy the secret token for an API key. See [Vitally's authentication documentation](https://docs.vitally.io/en/articles/9880649-rest-api-overview).

Configure the following fields in Airbyte:

- **Custom Subdomain**: Enter only the subdomain, not a full URL, for example `your-custom-subdomain` for `https://your-custom-subdomain.rest.vitally.io/`.
- **Status**: Select `active`, `churned`, or `activeOrChurned` to filter the `accounts` stream.
- **Secret Token**: Enter the REST API secret token. The connector uses it as the HTTP Basic authentication username.
- **Basic Auth Header**: Despite its label, the connector uses this field as the HTTP Basic authentication password, not as a complete header. Vitally's documented header uses an empty password (`"basic_auth_header": ""` in JSON configuration). Don't paste Vitally's copied Basic Auth header into this field.

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
