# Taboola
This is the Taboola source that ingests data from the Taboola API.

Taboola helps you reach customers that convert. Drive business results by reaching people genuinely, effectively at just the right moment https://www.taboola.com/

In order to use this source, you must first create an account. Once logged in you can contact Taboola support to provide you with a Client ID, Client Secret and Account ID. Once these credentials have been obtained, you can input them into the appropriate fields.

You can learn more about the API here https://developers.taboola.com/backstage-api/reference

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | Client ID.  |  |
| `account_id` | `string` | Account ID. The ID associated with your taboola account |  |
| `client_secret` | `string` | Client secret.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| account | id | No pagination | ✅ |  ❌  |
| campaigns | id | No pagination | ✅ |  ❌  |
| campaign_items | id | No pagination | ✅ |  ❌  |
| audience_rules | id | No pagination | ✅ |  ❌  |
| conversion_rules | id | No pagination | ✅ |  ❌  |
| motion_ads | id | No pagination | ✅ |  ❌  |
| audiences | id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.6 | 2024-12-28 | [50826](https://github.com/airbytehq/airbyte/pull/50826) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50356](https://github.com/airbytehq/airbyte/pull/50356) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49754](https://github.com/airbytehq/airbyte/pull/49754) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49409](https://github.com/airbytehq/airbyte/pull/49409) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49114](https://github.com/airbytehq/airbyte/pull/49114) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-10-28 | | Initial release by [@aazam-gh](https://github.com/aazam-gh) via Connector Builder |

</details>
