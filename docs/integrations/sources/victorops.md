# VictorOps

## Overview

The VictorOps (now named Splunk On-Call) source is maintained by [Faros
AI](https://github.com/faros-ai/airbyte-connectors/tree/main/sources/victorops-source).
Please file any support requests on that repo to minimize response time from the
maintainers. The source supports both Full Refresh and Incremental syncs. You
can choose if this source will copy only the new or updated data, or all rows in
the tables and columns you set up for replication, every time a sync is run.

### Output schema

Several output streams are available from this source:

- [Incidents](https://portal.victorops.com/public/api-docs.html#!/Reporting/get_api_reporting_v2_incidents) \(Incremental\)
- [Teams](https://portal.victorops.com/public/api-docs.html#!/Teams/get_api_public_v1_team)
- [Users](https://portal.victorops.com/public/api-docs.html#!/Users/get_api_public_v1_user)

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

The VictorOps source should not run into VictorOps API limitations under normal
usage, however your VictorOps account may be limited to a total number of API
calls per month. Please [create an
issue](https://github.com/faros-ai/airbyte-connectors/issues/new) if you see any
rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

- VictorOps API ID
- VictorOps API Key

Please follow the [their documentation for generating a VictorOps API
Key](https://help.victorops.com/knowledge-base/api/).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                                   | Subject                                                |
| :------ | :--------- | :------------------------------------------------------------- | :----------------------------------------------------- |
| 0.1.23  | 2021-11-17 | [150](https://github.com/faros-ai/airbyte-connectors/pull/150) | Add VictorOps source and Faros destination's conterter |

</details>