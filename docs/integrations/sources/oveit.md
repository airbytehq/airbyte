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
| 0.0.1 | 2024-10-24 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
