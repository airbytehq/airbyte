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
| 0.0.41 | 2025-12-09 | [70624](https://github.com/airbytehq/airbyte/pull/70624) | Update dependencies |
| 0.0.40 | 2025-11-25 | [69968](https://github.com/airbytehq/airbyte/pull/69968) | Update dependencies |
| 0.0.39 | 2025-11-18 | [69436](https://github.com/airbytehq/airbyte/pull/69436) | Update dependencies |
| 0.0.38 | 2025-10-29 | [68717](https://github.com/airbytehq/airbyte/pull/68717) | Update dependencies |
| 0.0.37 | 2025-10-21 | [68273](https://github.com/airbytehq/airbyte/pull/68273) | Update dependencies |
| 0.0.36 | 2025-10-14 | [67839](https://github.com/airbytehq/airbyte/pull/67839) | Update dependencies |
| 0.0.35 | 2025-10-07 | [67196](https://github.com/airbytehq/airbyte/pull/67196) | Update dependencies |
| 0.0.34 | 2025-09-30 | [66315](https://github.com/airbytehq/airbyte/pull/66315) | Update dependencies |
| 0.0.33 | 2025-09-09 | [66029](https://github.com/airbytehq/airbyte/pull/66029) | Update dependencies |
| 0.0.32 | 2025-08-23 | [65345](https://github.com/airbytehq/airbyte/pull/65345) | Update dependencies |
| 0.0.31 | 2025-08-09 | [64661](https://github.com/airbytehq/airbyte/pull/64661) | Update dependencies |
| 0.0.30 | 2025-08-02 | [64423](https://github.com/airbytehq/airbyte/pull/64423) | Update dependencies |
| 0.0.29 | 2025-06-26 | [64099](https://github.com/airbytehq/airbyte/pull/64099) | Add support for updatedAt, cancelledByEmail, rescheduledByEmail and cancellationReason fields in GET Bookings |
| 0.0.28 | 2025-07-26 | [63787](https://github.com/airbytehq/airbyte/pull/63787) | Update dependencies |
| 0.0.27 | 2025-07-19 | [63486](https://github.com/airbytehq/airbyte/pull/63486) | Update dependencies |
| 0.0.26 | 2025-07-12 | [63075](https://github.com/airbytehq/airbyte/pull/63075) | Update dependencies |
| 0.0.25 | 2025-07-06 | [62522](https://github.com/airbytehq/airbyte/pull/62522) | Update rescheduled to rescheduledToUid field in GET Bookings |
| 0.0.24 | 2025-07-05 | [62539](https://github.com/airbytehq/airbyte/pull/62539) | Update dependencies |
| 0.0.23 | 2025-06-26 | [61717](https://github.com/airbytehq/airbyte/pull/61717) | Add support for createdAt, rescheduled and absentHost fields in GET Bookings |
| 0.0.22 | 2025-06-15 | [61097](https://github.com/airbytehq/airbyte/pull/61097) | Update dependencies |
| 0.0.21 | 2025-05-17 | [60707](https://github.com/airbytehq/airbyte/pull/60707) | Update dependencies |
| 0.0.20 | 2025-05-10 | [59898](https://github.com/airbytehq/airbyte/pull/59898) | Update dependencies |
| 0.0.19 | 2025-05-03 | [59325](https://github.com/airbytehq/airbyte/pull/59325) | Update dependencies |
| 0.0.18 | 2025-04-26 | [58713](https://github.com/airbytehq/airbyte/pull/58713) | Update dependencies |
| 0.0.17 | 2025-04-19 | [58272](https://github.com/airbytehq/airbyte/pull/58272) | Update dependencies |
| 0.0.16 | 2025-04-12 | [57662](https://github.com/airbytehq/airbyte/pull/57662) | Update dependencies |
| 0.0.15 | 2025-04-05 | [56603](https://github.com/airbytehq/airbyte/pull/56603) | Update dependencies |
| 0.0.14 | 2025-03-22 | [56117](https://github.com/airbytehq/airbyte/pull/56117) | Update dependencies |
| 0.0.13 | 2025-03-08 | [55379](https://github.com/airbytehq/airbyte/pull/55379) | Update dependencies |
| 0.0.12 | 2025-03-01 | [54907](https://github.com/airbytehq/airbyte/pull/54907) | Update dependencies |
| 0.0.11 | 2025-02-22 | [54272](https://github.com/airbytehq/airbyte/pull/54272) | Update dependencies |
| 0.0.10 | 2025-02-15 | [53868](https://github.com/airbytehq/airbyte/pull/53868) | Update dependencies |
| 0.0.9 | 2025-02-08 | [52935](https://github.com/airbytehq/airbyte/pull/52935) | Update dependencies |
| 0.0.8 | 2025-01-25 | [52186](https://github.com/airbytehq/airbyte/pull/52186) | Update dependencies |
| 0.0.7 | 2025-01-18 | [51712](https://github.com/airbytehq/airbyte/pull/51712) | Update dependencies |
| 0.0.6 | 2025-01-11 | [51247](https://github.com/airbytehq/airbyte/pull/51247) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50216](https://github.com/airbytehq/airbyte/pull/50216) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49584](https://github.com/airbytehq/airbyte/pull/49584) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49285](https://github.com/airbytehq/airbyte/pull/49285) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49023](https://github.com/airbytehq/airbyte/pull/49023) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-11-11 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
