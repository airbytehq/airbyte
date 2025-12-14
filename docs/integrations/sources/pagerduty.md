# PagerDuty

## Overview

The PagerDuty source is maintained by [Faros
AI](https://github.com/faros-ai/airbyte-connectors/tree/main/sources/pagerduty-source).
Please file any support requests on that repo to minimize response time from the
maintainers. The source supports both Full Refresh and Incremental syncs. You
can choose if this source will copy only the new or updated data, or all rows in
the tables and columns you set up for replication, every time a sync is run.

### Output schema

Several output streams are available from this source:

- [Incidents](https://developer.pagerduty.com/api-reference/b3A6Mjc0ODEzOA-list-incidents) \(Incremental\)
- [Incident Log Entries](https://developer.pagerduty.com/api-reference/b3A6Mjc0ODE1NA-list-log-entries) \(Incremental\)
- [Priorities](https://developer.pagerduty.com/api-reference/b3A6Mjc0ODE2NA-list-priorities)
- [Users](https://developer.pagerduty.com/api-reference/b3A6Mjc0ODIzMw-list-users)

If there are more endpoints you'd like Faros AI to support, please [create an
issue.](https://github.com/faros-ai/airbyte-connectors/issues/new)

### Features

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | Yes        |
| SSL connection    | Yes        |
| Namespaces        | No         |

### Performance considerations

The PagerDuty source should not run into PagerDuty API limitations under normal
usage. Please [create an
issue](https://github.com/faros-ai/airbyte-connectors/issues/new) if you see any
rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

- PagerDuty API Key

Please follow the [their documentation for generating a PagerDuty API
Key](https://support.pagerduty.com/docs/generating-api-keys#section-generating-a-general-access-rest-api-key).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                                   | Subject                              |
| :------ | :--------- | :------------------------------------------------------------- | :----------------------------------- |
| 0.3.28 | 2025-12-09 | [70522](https://github.com/airbytehq/airbyte/pull/70522) | Update dependencies |
| 0.3.27 | 2025-11-25 | [70092](https://github.com/airbytehq/airbyte/pull/70092) | Update dependencies |
| 0.3.26 | 2025-11-18 | [69672](https://github.com/airbytehq/airbyte/pull/69672) | Update dependencies |
| 0.3.25 | 2025-10-29 | [68998](https://github.com/airbytehq/airbyte/pull/68998) | Update dependencies |
| 0.3.24 | 2025-10-21 | [68290](https://github.com/airbytehq/airbyte/pull/68290) | Update dependencies |
| 0.3.23 | 2025-10-14 | [67782](https://github.com/airbytehq/airbyte/pull/67782) | Update dependencies |
| 0.3.22 | 2025-10-07 | [67345](https://github.com/airbytehq/airbyte/pull/67345) | Update dependencies |
| 0.3.21 | 2025-09-30 | [66395](https://github.com/airbytehq/airbyte/pull/66395) | Update dependencies |
| 0.3.20 | 2025-09-09 | [65858](https://github.com/airbytehq/airbyte/pull/65858) | Update dependencies |
| 0.3.19 | 2025-08-23 | [65170](https://github.com/airbytehq/airbyte/pull/65170) | Update dependencies |
| 0.3.18 | 2025-08-09 | [64767](https://github.com/airbytehq/airbyte/pull/64767) | Update dependencies |
| 0.3.17 | 2025-08-02 | [64253](https://github.com/airbytehq/airbyte/pull/64253) | Update dependencies |
| 0.3.16 | 2025-07-26 | [63884](https://github.com/airbytehq/airbyte/pull/63884) | Update dependencies |
| 0.3.15 | 2025-07-19 | [63435](https://github.com/airbytehq/airbyte/pull/63435) | Update dependencies |
| 0.3.14 | 2025-07-12 | [63161](https://github.com/airbytehq/airbyte/pull/63161) | Update dependencies |
| 0.3.13 | 2025-07-05 | [62552](https://github.com/airbytehq/airbyte/pull/62552) | Update dependencies |
| 0.3.12 | 2025-06-28 | [62388](https://github.com/airbytehq/airbyte/pull/62388) | Update dependencies |
| 0.3.11 | 2025-06-21 | [61923](https://github.com/airbytehq/airbyte/pull/61923) | Update dependencies |
| 0.3.10 | 2025-06-14 | [61027](https://github.com/airbytehq/airbyte/pull/61027) | Update dependencies |
| 0.3.9 | 2025-05-24 | [60123](https://github.com/airbytehq/airbyte/pull/60123) | Update dependencies |
| 0.3.8 | 2025-05-03 | [59469](https://github.com/airbytehq/airbyte/pull/59469) | Update dependencies |
| 0.3.7 | 2025-04-27 | [59103](https://github.com/airbytehq/airbyte/pull/59103) | Update dependencies |
| 0.3.6 | 2025-04-19 | [58486](https://github.com/airbytehq/airbyte/pull/58486) | Update dependencies |
| 0.3.5 | 2025-04-12 | [57925](https://github.com/airbytehq/airbyte/pull/57925) | Update dependencies |
| 0.3.4 | 2025-04-05 | [57302](https://github.com/airbytehq/airbyte/pull/57302) | Update dependencies |
| 0.3.3 | 2025-03-29 | [56736](https://github.com/airbytehq/airbyte/pull/56736) | Update dependencies |
| 0.3.2 | 2025-03-22 | [56208](https://github.com/airbytehq/airbyte/pull/56208) | Update dependencies |
| 0.3.1 | 2025-03-08 | [43794](https://github.com/airbytehq/airbyte/pull/43794) | Update dependencies |
| 0.3.0 | 2024-10-06 | [46528](https://github.com/airbytehq/airbyte/pull/46528) | Converting to manifest-only format |
| 0.2.12 | 2024-08-03 | [43061](https://github.com/airbytehq/airbyte/pull/43061) | Update dependencies |
| 0.2.11 | 2024-07-27 | [42713](https://github.com/airbytehq/airbyte/pull/42713) | Update dependencies |
| 0.2.10 | 2024-07-20 | [42267](https://github.com/airbytehq/airbyte/pull/42267) | Update dependencies |
| 0.2.9 | 2024-07-13 | [41725](https://github.com/airbytehq/airbyte/pull/41725) | Update dependencies |
| 0.2.8 | 2024-07-10 | [41501](https://github.com/airbytehq/airbyte/pull/41501) | Update dependencies |
| 0.2.7 | 2024-07-09 | [41240](https://github.com/airbytehq/airbyte/pull/41240) | Update dependencies |
| 0.2.6 | 2024-07-06 | [40803](https://github.com/airbytehq/airbyte/pull/40803) | Update dependencies |
| 0.2.5 | 2024-06-25 | [40303](https://github.com/airbytehq/airbyte/pull/40303) | Update dependencies |
| 0.2.4 | 2024-06-22 | [39985](https://github.com/airbytehq/airbyte/pull/39985) | Update dependencies |
| 0.2.3 | 2024-06-12 | [39115](https://github.com/airbytehq/airbyte/pull/39115) | Make compatible with builder |
| 0.2.2 | 2024-06-06 | [39169](https://github.com/airbytehq/airbyte/pull/39169) | [autopull] Upgrade base image to v1.2.2 |
| 0.2.1 | 2024-05-20 | [38429](https://github.com/airbytehq/airbyte/pull/38429) | [autopull] base image + poetry + up_to_date |
| 0.2.0 | 2023-10-20 | [31160](https://github.com/airbytehq/airbyte/pull/31160) | Migrate to low code |
| 0.1.23  | 2021-11-12 | [125](https://github.com/faros-ai/airbyte-connectors/pull/125) | Add Pagerduty source and destination |

</details>
