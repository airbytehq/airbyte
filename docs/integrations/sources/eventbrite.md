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
| 0.0.41 | 2025-12-09 | [70582](https://github.com/airbytehq/airbyte/pull/70582) | Update dependencies |
| 0.0.40 | 2025-11-25 | [70158](https://github.com/airbytehq/airbyte/pull/70158) | Update dependencies |
| 0.0.39 | 2025-11-18 | [69359](https://github.com/airbytehq/airbyte/pull/69359) | Update dependencies |
| 0.0.38 | 2025-10-29 | [68725](https://github.com/airbytehq/airbyte/pull/68725) | Update dependencies |
| 0.0.37 | 2025-10-21 | [68553](https://github.com/airbytehq/airbyte/pull/68553) | Update dependencies |
| 0.0.36 | 2025-10-14 | [67745](https://github.com/airbytehq/airbyte/pull/67745) | Update dependencies |
| 0.0.35 | 2025-10-07 | [67274](https://github.com/airbytehq/airbyte/pull/67274) | Update dependencies |
| 0.0.34 | 2025-09-30 | [66285](https://github.com/airbytehq/airbyte/pull/66285) | Update dependencies |
| 0.0.33 | 2025-09-09 | [65760](https://github.com/airbytehq/airbyte/pull/65760) | Update dependencies |
| 0.0.32 | 2025-08-23 | [65293](https://github.com/airbytehq/airbyte/pull/65293) | Update dependencies |
| 0.0.31 | 2025-08-09 | [64710](https://github.com/airbytehq/airbyte/pull/64710) | Update dependencies |
| 0.0.30 | 2025-08-02 | [64321](https://github.com/airbytehq/airbyte/pull/64321) | Update dependencies |
| 0.0.29 | 2025-07-26 | [63973](https://github.com/airbytehq/airbyte/pull/63973) | Update dependencies |
| 0.0.28 | 2025-07-19 | [63590](https://github.com/airbytehq/airbyte/pull/63590) | Update dependencies |
| 0.0.27 | 2025-07-12 | [63011](https://github.com/airbytehq/airbyte/pull/63011) | Update dependencies |
| 0.0.26 | 2025-07-05 | [62796](https://github.com/airbytehq/airbyte/pull/62796) | Update dependencies |
| 0.0.25 | 2025-06-28 | [62419](https://github.com/airbytehq/airbyte/pull/62419) | Update dependencies |
| 0.0.24 | 2025-06-21 | [61977](https://github.com/airbytehq/airbyte/pull/61977) | Update dependencies |
| 0.0.23 | 2025-06-14 | [61224](https://github.com/airbytehq/airbyte/pull/61224) | Update dependencies |
| 0.0.22 | 2025-05-24 | [60368](https://github.com/airbytehq/airbyte/pull/60368) | Update dependencies |
| 0.0.21 | 2025-05-10 | [60002](https://github.com/airbytehq/airbyte/pull/60002) | Update dependencies |
| 0.0.20 | 2025-05-03 | [58891](https://github.com/airbytehq/airbyte/pull/58891) | Update dependencies |
| 0.0.19 | 2025-04-19 | [57784](https://github.com/airbytehq/airbyte/pull/57784) | Update dependencies |
| 0.0.18 | 2025-04-05 | [57233](https://github.com/airbytehq/airbyte/pull/57233) | Update dependencies |
| 0.0.17 | 2025-03-29 | [56549](https://github.com/airbytehq/airbyte/pull/56549) | Update dependencies |
| 0.0.16 | 2025-03-22 | [55961](https://github.com/airbytehq/airbyte/pull/55961) | Update dependencies |
| 0.0.15 | 2025-03-08 | [55289](https://github.com/airbytehq/airbyte/pull/55289) | Update dependencies |
| 0.0.14 | 2025-03-01 | [54917](https://github.com/airbytehq/airbyte/pull/54917) | Update dependencies |
| 0.0.13 | 2025-02-22 | [54425](https://github.com/airbytehq/airbyte/pull/54425) | Update dependencies |
| 0.0.12 | 2025-02-15 | [53761](https://github.com/airbytehq/airbyte/pull/53761) | Update dependencies |
| 0.0.11 | 2025-02-08 | [53326](https://github.com/airbytehq/airbyte/pull/53326) | Update dependencies |
| 0.0.10 | 2025-02-01 | [52869](https://github.com/airbytehq/airbyte/pull/52869) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52353](https://github.com/airbytehq/airbyte/pull/52353) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51707](https://github.com/airbytehq/airbyte/pull/51707) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51071](https://github.com/airbytehq/airbyte/pull/51071) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50513](https://github.com/airbytehq/airbyte/pull/50513) | Update dependencies |
| 0.0.5 | 2024-12-21 | [49994](https://github.com/airbytehq/airbyte/pull/49994) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49494](https://github.com/airbytehq/airbyte/pull/49494) | Update dependencies |
| 0.0.3 | 2024-12-12 | [48962](https://github.com/airbytehq/airbyte/pull/48962) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47521](https://github.com/airbytehq/airbyte/pull/47521) | Update dependencies |
| 0.0.1 | 2024-09-21 | | Initial release by [@topefolorunso](https://github.com/topefolorunso) via Connector Builder |

</details>
