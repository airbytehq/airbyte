# Outreach

## Overview

The Outreach source supports both `Full Refresh` and `Incremental` syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

### Output schema

Some output streams are available from this source. A list of these streams can be found below in the [Streams](outreach.md#streams) section.

### Features

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | Yes        |
| SSL connection    | Yes        |
| Namespaces        | No         |

## Getting started

### Requirements

- Outreach Account
- Outreach OAuth credentials

### Setup guide

Getting oauth credentials require contacting Outreach to request an account. Check out [here](https://www.outreach.io/lp/watch-demo#request-demo).
Once you have an API application, you can follow the steps [here](https://api.outreach.io/api/v2/docs#authentication) to obtain a refresh token.

## Streams

List of available streams:

- Prospects
- Sequences
- SequenceStates
- SequenceSteps
- Calls
- Mailings
- Accounts
- Opportunities
- Personas
- Mailboxes
- Stages
- Users
- Tasks
- Templates
- Snippets

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request | Subject |
| :------ |:-----------| :----- | :------ |
| 1.0.15 | 2024-08-31 | [45056](https://github.com/airbytehq/airbyte/pull/45056) | Update dependencies |
| 1.0.14 | 2024-08-24 | [44653](https://github.com/airbytehq/airbyte/pull/44653) | Update dependencies |
| 1.0.13 | 2024-08-17 | [44238](https://github.com/airbytehq/airbyte/pull/44238) | Update dependencies |
| 1.0.12 | 2024-08-12 | [43790](https://github.com/airbytehq/airbyte/pull/43790) | Update dependencies |
| 1.0.11 | 2024-08-10 | [43648](https://github.com/airbytehq/airbyte/pull/43648) | Update dependencies |
| 1.0.10 | 2024-08-08 | [41107](https://github.com/airbytehq/airbyte/pull/41107) | Fix pagination |
| 1.0.9 | 2024-08-03 | [43128](https://github.com/airbytehq/airbyte/pull/43128) | Update dependencies |
| 1.0.8 | 2024-07-20 | [42254](https://github.com/airbytehq/airbyte/pull/42254) | Update dependencies |
| 1.0.7 | 2024-07-13 | [41786](https://github.com/airbytehq/airbyte/pull/41786) | Update dependencies |
| 1.0.6 | 2024-07-10 | [41490](https://github.com/airbytehq/airbyte/pull/41490) | Update dependencies |
| 1.0.5 | 2024-07-09 | [41236](https://github.com/airbytehq/airbyte/pull/41236) | Update dependencies |
| 1.0.4 | 2024-07-06 | [40910](https://github.com/airbytehq/airbyte/pull/40910) | Update dependencies |
| 1.0.3 | 2024-06-25 | [40341](https://github.com/airbytehq/airbyte/pull/40341) | Update dependencies |
| 1.0.2 | 2024-06-22 | [39977](https://github.com/airbytehq/airbyte/pull/39977) | Update dependencies |
| 1.0.1 | 2024-06-04 | [38972](https://github.com/airbytehq/airbyte/pull/38972) | [autopull] Upgrade base image to v1.2.1 |
| 1.0.0 | 2024-04-15 | [36602](https://github.com/airbytehq/airbyte/pull/36602) | Migrate to low code |
| 0.5.4 | 2024-04-19 | [37215](https://github.com/airbytehq/airbyte/pull/37215) | Updating to 0.80.0 CDK |
| 0.5.3 | 2024-04-18 | [37215](https://github.com/airbytehq/airbyte/pull/37215) | Manage dependencies with Poetry. |
| 0.5.2 | 2024-04-15 | [37215](https://github.com/airbytehq/airbyte/pull/37215) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.5.1 | 2024-04-12 | [37215](https://github.com/airbytehq/airbyte/pull/37215) | Schema descriptions |
| 0.5.0 | 2023-09-20 | [30639](https://github.com/airbytehq/airbyte/pull/30639) | Add Call Purposes and Call Dispositions streams |
| 0.4.0 | 2023-06-14 | [27343](https://github.com/airbytehq/airbyte/pull/27343) | Add Users, Tasks, Templates, Snippets streams |
| 0.3.0 | 2023-05-17 | [26211](https://github.com/airbytehq/airbyte/pull/26211) | Add SequenceStates Stream |
| 0.2.0 | 2022-10-27 | [17385](https://github.com/airbytehq/airbyte/pull/17385) | Add new streams + page size variable + relationship data |
| 0.1.2 | 2022-07-04 | [14386](https://github.com/airbytehq/airbyte/pull/14386) | Fix stream schema and cursor field |
| 0.1.1 | 2021-12-07 | [8582](https://github.com/airbytehq/airbyte/pull/8582) | Update connector fields title/description |
| 0.1.0 | 2021-11-03 | [7507](https://github.com/airbytehq/airbyte/pull/7507) | Outreach Connector |

</details>
