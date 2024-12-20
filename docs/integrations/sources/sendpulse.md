# SendPulse
Airbyte connector for [SendPulse](https://sendpulse.com/) allows you to seamlessly sync data from SendPulse to your data warehouse. It retrieves essential information from various SendPulse streams, including mailing lists, campaigns, templates, senders, webhooks, balance details, and balance. This enables you to analyze and manage your SendPulse email marketing and communication efforts effectively in a centralized location.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | OAuth Client ID.  |  |
| `client_secret` | `string` | OAuth Client Secret.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| mailing_lists | id | DefaultPaginator | ✅ |  ❌  |
| campaigns | id | DefaultPaginator | ✅ |  ❌  |
| templates | id | No pagination | ✅ |  ❌  |
| senders | email | No pagination | ✅ |  ❌  |
| webhooks | id | No pagination | ✅ |  ❌  |
| balance_details |  | No pagination | ✅ |  ❌  |
| balance | currency | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.4 | 2024-12-14 | [49677](https://github.com/airbytehq/airbyte/pull/49677) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49323](https://github.com/airbytehq/airbyte/pull/49323) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49061](https://github.com/airbytehq/airbyte/pull/49061) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-11-08 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
