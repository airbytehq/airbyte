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
