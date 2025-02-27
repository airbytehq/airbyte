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
| 0.0.13 | 2025-02-23 | [54602](https://github.com/airbytehq/airbyte/pull/54602) | Update dependencies |
| 0.0.12 | 2025-02-15 | [54001](https://github.com/airbytehq/airbyte/pull/54001) | Update dependencies |
| 0.0.11 | 2025-02-08 | [53474](https://github.com/airbytehq/airbyte/pull/53474) | Update dependencies |
| 0.0.10 | 2025-02-01 | [52991](https://github.com/airbytehq/airbyte/pull/52991) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52499](https://github.com/airbytehq/airbyte/pull/52499) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51861](https://github.com/airbytehq/airbyte/pull/51861) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51309](https://github.com/airbytehq/airbyte/pull/51309) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50715](https://github.com/airbytehq/airbyte/pull/50715) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50275](https://github.com/airbytehq/airbyte/pull/50275) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49695](https://github.com/airbytehq/airbyte/pull/49695) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49328](https://github.com/airbytehq/airbyte/pull/49328) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49057](https://github.com/airbytehq/airbyte/pull/49057) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-10-24 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
