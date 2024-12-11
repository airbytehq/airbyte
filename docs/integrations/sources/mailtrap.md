# Mailtrap

Email Delivery Platform for individuals and businesses to test, send and control email infrastructure in one place.

[API Documentation](https://api-docs.mailtrap.io/docs/mailtrap-api-docs/5tjdeg9545058-mailtrap-api)

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_token` | `string` | API Token. API token to use. Find it at https://mailtrap.io/account |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| accounts | id | No pagination | ✅ |  ❌  |
| billing_usage | uuid | No pagination | ✅ |  ❌  |
| resources | id | No pagination | ✅ |  ❌  |
| sending_domains | id | No pagination | ✅ |  ❌  |
| inboxes | id | No pagination | ✅ |  ❌  |
| messages | id | No pagination | ✅ |  ❌  |
| projects | id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.2 | 2024-12-11 | [48968](https://github.com/airbytehq/airbyte/pull/48968) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-10-23 | | Initial release by [@gemsteam](https://github.com/gemsteam) via Connector Builder |

</details>
