# Cal.com
The Cal.com connector enables seamless data synchronization between Cal.com’s scheduling platform and various destinations. It helps extract events, attendees, and booking details from Cal.com, making it easy to analyze scheduling data or integrate it into downstream systems like data warehouses or CRMs. This connector streamlines automated reporting and insights for time management and booking analytics

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `orgId` | `string` | Organization ID.  |  |
| `api_key` | `string` | API Key. API key to use. Find it at https://cal.com/account |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| event_types | id | DefaultPaginator | ✅ |  ❌  |
| my_profile | id | No pagination | ✅ |  ❌  |
| schedules | id | DefaultPaginator | ✅ |  ❌  |
| calendars | externalId | No pagination | ✅ |  ❌  |
| bookings | id | DefaultPaginator | ✅ |  ❌  |
| conferencing | id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.7 | 2025-01-18 | [51712](https://github.com/airbytehq/airbyte/pull/51712) | Update dependencies |
| 0.0.6 | 2025-01-11 | [51247](https://github.com/airbytehq/airbyte/pull/51247) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50216](https://github.com/airbytehq/airbyte/pull/50216) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49584](https://github.com/airbytehq/airbyte/pull/49584) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49285](https://github.com/airbytehq/airbyte/pull/49285) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49023](https://github.com/airbytehq/airbyte/pull/49023) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-11-11 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
