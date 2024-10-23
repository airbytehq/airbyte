# Eventbrite
Eventbrite is a global self-service ticketing platform for live experiences that allows anyone to create, share, find and attend events that fuel their passions and enrich their lives. From music festivals, marathons, conferences, community rallies, and fundraisers, to gaming competitions and air guitar contests.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `private_token` | `string` | Private Token. The private token to use for authenticating API requests. |  |
| `start_date` | `string` | Start date.  |  |

To get a Private Token:
- Log in to your Eventbrite account and visit your [API Keys page](https://www.eventbrite.com/platform/api-keys).
- Copy your private token.

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| organizations | id | DefaultPaginator | ✅ |  ✅  |
| events | id | DefaultPaginator | ✅ |  ✅  |
| attendees | id | DefaultPaginator | ✅ |  ✅  |
| categories | id | DefaultPaginator | ✅ |  ❌  |
| formats | id | DefaultPaginator | ✅ |  ❌  |
| orders | id | DefaultPaginator | ✅ |  ✅  |
| organizations_members | user_id | DefaultPaginator | ✅ |  ❌  |
| organizations_roles | id | DefaultPaginator | ✅ |  ❌  |
| default_questions | id.event_id | DefaultPaginator | ✅ |  ❌  |
| custom_questions | id | DefaultPaginator | ✅ |  ❌  |
| ticket_buyer_settings |  | No pagination | ✅ |  ❌  |
| ticket_classes | id | DefaultPaginator | ✅ |  ❌  |
| available_ticket_classes |  | DefaultPaginator | ✅ |  ❌  |
| venues | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.0.1 | 2024-09-21 | | Initial release by [@topefolorunso](https://github.com/topefolorunso) via Connector Builder |

</details>
