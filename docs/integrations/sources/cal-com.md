# Cal.com
The Cal.com connector enables seamless data synchronization between Cal.com’s scheduling platform and various destinations. It helps extract events, attendees, and booking details from Cal.com, making it easy to analyze scheduling data or integrate it into downstream systems like data warehouses or CRMs. This connector streamlines automated reporting and insights for time management and booking analytics

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `orgId` | `string` | orgId.  |  |
| `api_key` | `string` | API Key. API key to use. Find it at https://cal.com/account |  |
| `start_time` | `string` | Start Time.  |  |
| `end_time` | `string` | End Time.  |  |
| `event_type_id` | `number` | Event Type Id.  |  |
| `event_type_slug` | `string` | Event Type Slug.  |  |
| `user_name_list` | `array` | User Name List.  |  |
| `duration` | `number` | Duration.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| event_types | id | No pagination | ✅ |  ❌  |
| my_profile | id | No pagination | ✅ |  ❌  |
| schedules | id | No pagination | ✅ |  ❌  |
| slots |  | No pagination | ✅ |  ❌  |
| calendars | externalId | No pagination | ✅ |  ❌  |
| bookings | id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-23 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
