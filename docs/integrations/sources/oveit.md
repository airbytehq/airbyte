# Oveit
An Airbyte connector for Oveit enables seamless data synchronization by extracting and integrating data from Oveit’s event management platform into your data warehouse. This connector helps automate the flow of information, providing up-to-date insights on event registrations, ticketing, and attendee information.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `email` | `string` | Email. Oveit&#39;s login Email |  |
| `password` | `string` | Password. Oveit&#39;s login Password |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| events | id | No pagination | ✅ |  ❌  |
| attendees | id | DefaultPaginator | ✅ |  ❌  |
| tickets | code | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.3 | 2024-12-12 | [49328](https://github.com/airbytehq/airbyte/pull/49328) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49057](https://github.com/airbytehq/airbyte/pull/49057) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-10-24 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
