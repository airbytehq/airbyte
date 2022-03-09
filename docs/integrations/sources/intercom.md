# Intercom

## Overview

The Intercom source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This Source Connector is based on a [Airbyte CDK](https://docs.airbyte.io/connector-development/cdk-python).

### Output schema

Several output streams are available from this source:

* [Admins](https://developers.intercom.com/intercom-api-reference/reference#list-admins) \(Full table\)
* [Companies](https://developers.intercom.com/intercom-api-reference/reference#list-companies) \(Incremental\)
  * [Company Segments](https://developers.intercom.com/intercom-api-reference/reference#list-attached-segments-1) \(Incremental\)
* [Conversations](https://developers.intercom.com/intercom-api-reference/reference#list-conversations) \(Incremental\)
  * [Conversation Parts](https://developers.intercom.com/intercom-api-reference/reference#get-a-single-conversation) \(Incremental\)
* [Data Attributes](https://developers.intercom.com/intercom-api-reference/reference#data-attributes) \(Full table\)
  * [Customer Attributes](https://developers.intercom.com/intercom-api-reference/reference#list-customer-data-attributes) \(Full table\)
  * [Company Attributes](https://developers.intercom.com/intercom-api-reference/reference#list-company-data-attributes) \(Full table\)
* [Contacts](https://developers.intercom.com/intercom-api-reference/reference#list-contacts) \(Incremental\)
* [Segments](https://developers.intercom.com/intercom-api-reference/reference#list-segments) \(Incremental\)
* [Tags](https://developers.intercom.com/intercom-api-reference/reference#list-tags-for-an-app) \(Full table\)
* [Teams](https://developers.intercom.com/intercom-api-reference/reference#list-teams) \(Full table\)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | Yes |
| Replicate Incremental Deletes | Coming soon |
| SSL connection | Yes |
| Namespaces | No |

### Performance considerations

The connector is restricted by normal Intercom [requests limitation](https://developers.intercom.com/intercom-api-reference/reference#rate-limiting).

The Intercom connector should not run into Intercom API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Intercom Access Token

### Setup guide

Please read [How to get your Access Token](https://developers.intercom.com/building-apps/docs/authentication-types#section-how-to-get-your-access-token).

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.13 | 2022-01-14 | [9513](https://github.com/airbytehq/airbyte/pull/9513) | Added handling of scroll param when it expired |
| 0.1.12 | 2021-12-14 | [8429](https://github.com/airbytehq/airbyte/pull/8429) | Updated fields and descriptions |
| 0.1.11 | 2021-12-13 | [8685](https://github.com/airbytehq/airbyte/pull/8685) | Remove time.sleep for rate limit |
| 0.1.10 | 2021-12-10 | [8637](https://github.com/airbytehq/airbyte/pull/8637) | Fix 'conversations' order and sorting. Correction of the companies stream |
| 0.1.9 | 2021-12-03 | [8395](https://github.com/airbytehq/airbyte/pull/8395) | Fix backoff of 'companies' stream |
| 0.1.8 | 2021-11-09 | [7060](https://github.com/airbytehq/airbyte/pull/7060) | Added oauth support |
| 0.1.7 | 2021-11-08 | [7499](https://github.com/airbytehq/airbyte/pull/7499) | Remove base-python dependencies |
| 0.1.6 | 2021-10-07 | [6879](https://github.com/airbytehq/airbyte/pull/6879) | Corrected pagination for contacts |
| 0.1.5 | 2021-09-28 | [6082](https://github.com/airbytehq/airbyte/pull/6082) | Corrected android\_last\_seen\_at field data type in schemas |
| 0.1.4 | 2021-09-20 | [6087](https://github.com/airbytehq/airbyte/pull/6087) | Corrected updated\_at field data type in schemas |
| 0.1.3 | 2021-09-08 | [5908](https://github.com/airbytehq/airbyte/pull/5908) | Corrected timestamp and arrays in schemas |
| 0.1.2 | 2021-08-19 | [5531](https://github.com/airbytehq/airbyte/pull/5531) | Corrected pagination |
| 0.1.1 | 2021-07-31 | [5123](https://github.com/airbytehq/airbyte/pull/5123) | Corrected rate limit |
| 0.1.0 | 2021-07-19 | [4676](https://github.com/airbytehq/airbyte/pull/4676) | Release Intercom CDK Connector |
