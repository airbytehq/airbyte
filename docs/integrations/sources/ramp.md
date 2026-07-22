# Ramp
Ramp is a corporate card and finance automation platform designed to help businesses save time and money.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | Ramp Client ID. From AWS Secrets Manager ramp_credentials.CLIENT_ID |  |
| `client_secret` | `string` | Ramp Client Secret. From AWS Secrets Manager ramp_credentials.CLIENT_SECRET |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| cards | id | DefaultPaginator | ✅ |  ❌  |
| transactions | id | DefaultPaginator | ✅ |  ❌  |
| reimbursements | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-07-02 | | Initial release by [@Ella6882](https://github.com/Ella6882) via Connector Builder |

</details>
