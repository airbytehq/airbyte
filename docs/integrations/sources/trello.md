# Trello

## Overview

The Trello source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This Source Connector is based on a [Airbyte CDK](https://docs.airbyte.io/connector-development/cdk-python).

### Output schema

Several output streams are available from this source:

* [Boards](https://developers.intercom.com/intercom-api-reference/reference#list-attached-segments-1) \(Full table\)
  * [Actions](https://developer.atlassian.com/cloud/trello/rest/api-group-boards/#api-boards-boardid-actions-get) \(Incremental\)
  * [Cards](https://developer.atlassian.com/cloud/trello/rest/api-group-boards/#api-boards-id-cards-get) \(Full table\)
  * [Checklists](https://developer.atlassian.com/cloud/trello/rest/api-group-boards/#api-boards-id-checklists-get) \(Full table\)
  * [Lists](https://developer.atlassian.com/cloud/trello/rest/api-group-boards/#api-boards-id-lists-get) \(Full table\)
  * [Users](https://developer.atlassian.com/cloud/trello/rest/api-group-boards/#api-boards-id-members-get) \(Full table\)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | Yes |
| SSL connection | Yes |
| Namespaces | No |

### Performance considerations

The connector is restricted by normal Trello [requests limitation](https://developer.atlassian.com/cloud/trello/guides/rest-api/rate-limits/).

The Trello connector should not run into Trello API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Trello API Token
* Trello API Key

### Setup guide
<!-- markdown-link-check-disable-next-line -->
Please read [How to get your APIs Token and Key](https://developer.atlassian.com/cloud/trello/guides/rest-api/authorization/#using-basic-oauth) or you can log in to Trello and visit [Developer API Keys](https://trello.com/app-key/).

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.6 | 2021-12-28 | [8628](https://github.com/airbytehq/airbyte/pull/8628) | Updated fields in source-connector specifications |
| 0.1.3 | 2021-11-25 | [8183](https://github.com/airbytehq/airbyte/pull/8183) | Enable specifying board ids in configuration |
| 0.1.2 | 2021-11-08 | [7499](https://github.com/airbytehq/airbyte/pull/7499) | Remove base-python dependencies |
| 0.1.1 | 2021-10-12 | [6968](https://github.com/airbytehq/airbyte/pull/6968) | Add oAuth flow support |
| 0.1.0 | 2021-08-18 | [5501](https://github.com/airbytehq/airbyte/pull/5501) | Release Trello CDK Connector |

