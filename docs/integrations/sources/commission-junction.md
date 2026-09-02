# Commission Junction (CJ Affiliate)
CJ Affiliate (formerly known as Commission Junction) is one of the world&#39;s largest and most established affiliate marketing networks.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `cid` | `string` | CID.  |  |
| `start_date` | `string` | start_date.  | 2025-02-01T00:00:00Z |
| `personal_access_token` | `string` | Personal Access Token. Your CJ API personal access token. You can create and manage tokens at https://developers.cj.com/account/personal-access-tokens. Make sure to keep this token secure and do not share it publicly. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| AdvertiserCommissions | commissionId | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.5 | 2026-08-18 | [84537](https://github.com/airbytehq/airbyte/pull/84537) | Update dependencies |
| 0.0.4 | 2026-08-11 | [83873](https://github.com/airbytehq/airbyte/pull/83873) | Update dependencies |
| 0.0.3 | 2026-08-04 | [83420](https://github.com/airbytehq/airbyte/pull/83420) | Update dependencies |
| 0.0.2 | 2026-07-28 | [82883](https://github.com/airbytehq/airbyte/pull/82883) | Update dependencies |
| 0.0.1 | 2026-06-30 | [81336](https://github.com/airbytehq/airbyte/pull/81336) | Initial release by [@Ella6882](https://github.com/Ella6882) via Connector Builder |

</details>
