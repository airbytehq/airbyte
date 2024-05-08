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

| Version | Date       | Pull Request                                                   | Subject                              |
| :------ | :--------- | :------------------------------------------------------------- | :----------------------------------- |
| 0.2.0   | 2023-10-20 | [31160](https://github.com/airbytehq/airbyte/pull/31160)       | Migrate to low code                  |
| 0.1.23  | 2021-11-12 | [125](https://github.com/faros-ai/airbyte-connectors/pull/125) | Add Pagerduty source and destination |
