# Wasabi
Connector for https://www.wasabi.com stats API. 
API docs: https://docs.wasabi.com/apidocs/wasabi-stats-api

:::info
This connector ingest stats information from Wasabi server. 
It **does not** ingest content from files stored in Wasabi.
:::

## Prerequisites

The Wasabi Stats API authenticates with a Wasabi access key pair sent as `AccessKey:SecretKey` in the `Authorization` header. The keys must either belong to the **Root user** or to a sub-user that has the `WasabiAccountStatsAccess` (account-level stats) and/or `WasabiBucketStatsAccess` (bucket-level stats) policy attached. Wasabi Account Control (WAC) API keys and plain S3-only sub-user keys are rejected with `403 Forbidden`.

See [Generating a Wasabi Stats API Key](https://docs.wasabi.com/apidocs/generating-a-wasabi-stats-api-key) and [Authentication With Wasabi Stats API](https://docs.wasabi.com/apidocs/authentication-with-wasabi-stats-api).

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. The API key format is `AccessKey:SecretKey` |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Standalone Utilizations |  | DefaultPaginator | ✅ |  ✅  |
| Standalone Bucket Utilizations |  | DefaultPaginator | ✅ |  ✅  |

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.0.3 | 2026-10-07 | [PR](https://github.com/airbytehq/airbyte/pull/<n>) | Return an actionable `config_error` on HTTP 401/403 (credentials lacking Stats API access), document key requirements, fix stale Wasabi docs links |
| 0.0.2 | 2026-06-02 | [79045](https://github.com/airbytehq/airbyte/pull/79045) | Update dependencies |
| 0.0.1 | 2024-10-25 | | Initial release by [@dainiussa](https://github.com/dainiussa) via Connector Builder |

</details>
