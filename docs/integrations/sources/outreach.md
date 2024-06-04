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
| 1.0.0 | 2024-04-15 | [36602](https://github.com/airbytehq/airbyte/pull/36602) | Migrate to low code |
| 0.5.4 | 2024-04-19 | [37215](https://github.com/airbytehq/airbyte/pull/37215) | Updating to 0.80.0 CDK                                                          |
| 0.5.3 | 2024-04-18 | [37215](https://github.com/airbytehq/airbyte/pull/37215) | Manage dependencies with Poetry.                                                |
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