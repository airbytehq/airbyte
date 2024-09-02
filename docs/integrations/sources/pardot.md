# Pardot

## Overview

The Airbyte Source for [Salesforce Pardot](https://www.pardot.com/)

The Pardot supports full refresh syncs

### Output schema

Several output streams are available from this source:

- [Campaigns](https://developer.salesforce.com/docs/marketing/pardot/guide/campaigns-v4.html)
- [EmailClicks](https://developer.salesforce.com/docs/marketing/pardot/guide/batch-email-clicks-v4.html)
- [ListMembership](https://developer.salesforce.com/docs/marketing/pardot/guide/list-memberships-v4.html)
- [Lists](https://developer.salesforce.com/docs/marketing/pardot/guide/lists-v4.html)
- [ProspectAccounts](https://developer.salesforce.com/docs/marketing/pardot/guide/prospect-accounts-v4.html)
- [Prospects](https://developer.salesforce.com/docs/marketing/pardot/guide/prospects-v4.html)
- [Users](https://developer.salesforce.com/docs/marketing/pardot/guide/users-v4.html)
- [VisitorActivities](https://developer.salesforce.com/docs/marketing/pardot/guide/visitor-activities-v4.html)
- [Visitors](https://developer.salesforce.com/docs/marketing/pardot/guide/visitors-v4.html)
- [Visits](https://developer.salesforce.com/docs/marketing/pardot/guide/visits-v4.html)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |
| SSL connection    | No         |
| Namespaces        | No         |

### Performance considerations

The Pardot connector should not run into Pardot API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

- Pardot Account
- Pardot Business Unit ID
- Client ID
- Client Secret
- Refresh Token
- Start Date
- Is Sandbox environment?

### Setup guide

- `pardot_business_unit_id`: Pardot Business ID, can be found at Setup > Pardot > Pardot Account Setup
- `client_id`: The Consumer Key that can be found when viewing your app in Salesforce
- `client_secret`: The Consumer Secret that can be found when viewing your app in Salesforce
- `refresh_token`: Salesforce Refresh Token used for Airbyte to access your Salesforce account. If you don't know what this is, follow [this guide](https://medium.com/@bpmmendis94/obtain-access-refresh-tokens-from-salesforce-rest-api-a324fe4ccd9b) to retrieve it.
- `start_date`: UTC date and time in the format 2017-01-25T00:00:00Z. Any data before this date will not be replicated. Leave blank to skip this filter
- `is_sandbox`: Whether or not the app is in a Salesforce sandbox. If you do not know what this is, assume it is false.

## Changelog

| Version | Date       | Pull Request                                             | Subject               |
| :------ | :--------- | :------------------------------------------------------- | :-------------------- |
| 0.1.16 | 2024-08-31 | [45005](https://github.com/airbytehq/airbyte/pull/45005) | Update dependencies |
| 0.1.15 | 2024-08-24 | [44728](https://github.com/airbytehq/airbyte/pull/44728) | Update dependencies |
| 0.1.14 | 2024-08-17 | [44232](https://github.com/airbytehq/airbyte/pull/44232) | Update dependencies |
| 0.1.13 | 2024-08-10 | [43471](https://github.com/airbytehq/airbyte/pull/43471) | Update dependencies |
| 0.1.12 | 2024-08-03 | [43291](https://github.com/airbytehq/airbyte/pull/43291) | Update dependencies |
| 0.1.11 | 2024-07-27 | [42649](https://github.com/airbytehq/airbyte/pull/42649) | Update dependencies |
| 0.1.10 | 2024-07-20 | [42304](https://github.com/airbytehq/airbyte/pull/42304) | Update dependencies |
| 0.1.9 | 2024-07-13 | [41886](https://github.com/airbytehq/airbyte/pull/41886) | Update dependencies |
| 0.1.8 | 2024-07-10 | [41565](https://github.com/airbytehq/airbyte/pull/41565) | Update dependencies |
| 0.1.7 | 2024-07-09 | [40884](https://github.com/airbytehq/airbyte/pull/40884) | Update dependencies |
| 0.1.6 | 2024-06-26 | [40549](https://github.com/airbytehq/airbyte/pull/40549) | Migrate off deprecated auth package |
| 0.1.5 | 2024-06-25 | [40339](https://github.com/airbytehq/airbyte/pull/40339) | Update dependencies |
| 0.1.4 | 2024-06-22 | [40118](https://github.com/airbytehq/airbyte/pull/40118) | Update dependencies |
| 0.1.3 | 2024-06-04 | [39087](https://github.com/airbytehq/airbyte/pull/39087) | [autopull] Upgrade base image to v1.2.1 |
| 0.1.2 | 2024-05-21 | [38521](https://github.com/airbytehq/airbyte/pull/38521) | [autopull] base image + poetry + up_to_date |
| 0.1.1 | 2022-12-16 | [19618](https://github.com/airbytehq/airbyte/pull/19618) | Fix `visitors` stream |
| 0.1.0 | 2021-11-19 | [7091](https://github.com/airbytehq/airbyte/pull/7091) | 🎉 New Source: Pardot |
