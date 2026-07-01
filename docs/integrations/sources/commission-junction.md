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
| AdvertiserCommissions | commissionId.originalActionId | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-06-30 | | Initial release by [@Ella6882](https://github.com/Ella6882) via Connector Builder |

</details>
