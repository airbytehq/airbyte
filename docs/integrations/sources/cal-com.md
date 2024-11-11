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
| 0.0.1 | 2024-11-11 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
