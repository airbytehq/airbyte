# Talkdesk Explore

:::warning

## Deprecation Notice

The Talkdesk Explore source connector is scheduled for deprecation on March 5th, 2024 due to incompatibility with upcoming platform updates as we prepare to launch Airbyte 1.0. This means it will no longer be supported or available for use in Airbyte.

This connector does not support new per-stream features which are vital for ensuring data integrity in Airbyte's synchronization processes. Without these capabilities, we cannot enforce our standards of reliability and correctness for data syncing operations.

### Recommended Actions

Users who still wish to sync data from this connector are advised to explore creating a custom connector as an alternative to continue their data synchronization needs. For guidance, please visit our [Custom Connector documentation](https://docs.airbyte.com/connector-development/).

:::

## Overview

Talkdesk is a software for contact center operations.

The Talkdesk Explore connector uses the [Talkdesk Explore API](https://docs.talkdesk.com/docs/explore-api) to fetch data from usage reports.

### Output schema

The connector supports both Full Refresh and Incremental on the following streams:

- [Calls Report](https://docs.talkdesk.com/docs/calls-report)
- [User Status Report](https://docs.talkdesk.com/docs/user-status-explore)
- [Studio Flow Execution Report](https://docs.talkdesk.com/docs/studio-flow-execution-report)
- [Contacts Report](https://docs.talkdesk.com/docs/contacts-report)
- [Ring Attempts Report](https://docs.talkdesk.com/docs/ring-attempts-report)

### Note on report generation

To request data from one of the endpoints, first you need to generate a report. This is done by a POST request where the payload is the report specifications. Then, the response will be a report ID that you need to use in a GET request to obtain the report's data.

This process is further explained here: [Executing a Report](https://docs.talkdesk.com/docs/executing-a-report)

### Features

| Feature                   | Supported? |
| :------------------------ | :--------- |
| Full Refresh Sync         | Yes        |
| Incremental - Append Sync | Yes        |
| Incremental - Dedupe Sync | No         |
| SSL connection            | Yes        |

### Performance considerations

The Explore API has an account-based quota limit of 15 simultaneous reports (executing + enqueued). If this limit is exceeded, the user will receive a 429 (too many requests) response.

## Getting started

### Requirements

- Talkdesk account
- Talkdesk API key (`Client Credentials` auth method)

### Setup guide

Please refer to the [getting started with the API](https://docs.talkdesk.com/docs/api-access) guide.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request | Subject                      |
| ------- | ---------- | ------------ | ---------------------------- |
| 0.1.0   | 2022-02-07 |              | New Source: Talkdesk Explore |
| :---    | :---       | :---         | :---                         |

</details>