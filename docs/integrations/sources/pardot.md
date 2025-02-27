# Pardot (Salesforce Marketing Cloud Account Engagement)

## Overview

This page contains the setup guide and reference information for the [Pardot (Salesforce Marketing Cloud Account Engagement)](https://www.salesforce.com/marketing/b2b-automation/) source connector.

## Prerequisites

- Pardot/Marketing Cloud Account Engagement account
- Pardot Business Unit ID
- Client ID
- Client Secret
- Refresh Token

## Setup Guide

### Required configuration options
- **Pardot Business Unit ID** (`pardot_business_unit_id`): This value uniquely identifies your account, and can be found at Setup > Pardot > Pardot Account Setup

- **Client ID** (`client_id`): The Consumer Key that can be found when viewing your app in Salesforce

- **Client Secret** (`client_secret`): The Consumer Secret that can be found when viewing your app in Salesforce

- **Refresh Token** (`refresh_token`): Salesforce Refresh Token used for Airbyte to access your Salesforce account. If you don't know what this is, follow [this guide](https://medium.com/@bpmmendis94/obtain-access-refresh-tokens-from-salesforce-rest-api-a324fe4ccd9b) to retrieve it.

### Optional configuration options
- **Start Date** (`start_date`): UTC date and time in the format `2020-01-25T00:00:00Z`. Any data before this date will not be replicated. Defaults to `2007-01-01T00:00:00Z` (the year Pardot was launched)

- **Page Size Limit** (`page_size`): The default page size to return; defaults to `1000` (which is Pardot's maximum). Does not apply to the Email Clicks stream which uses the v4 API and is limited to 200 per page.

- **Is Sandbox App?** (`is_sandbox`): Whether or not the app is in a Salesforce sandbox. If you do not know what this is, assume it is false.

## Supported Sync Modes

The Pardot source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes):

- Full Refresh
- Incremental

Incremental streams are based on the Pardot API's `UpdatedAt` field when the object is updateable and the API supports it; otherwise `CreatedAt` or `Id` are used in that order of preference.

### Performance Considerations

The Pardot connector should not run into Pardot API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

:::tip

Pardot has daily API limits based on plan level. If one of these limits is hit, the connector will retry every two hours until quota is replenished.

:::

## Supported Streams

Several output streams are available from this source. Unless noted otherwise, streams are from Pardot's v5 API:

- [Account (Metadata)](https://developer.salesforce.com/docs/marketing/pardot/guide/account-v5.html) (full refresh)
- [Campaigns](https://developer.salesforce.com/docs/marketing/pardot/guide/campaign-v5.html) (incremental)
- [Custom Fields](https://developer.salesforce.com/docs/marketing/pardot/guide/custom-field-v5.html) (incremental)
- [Custom Redirects](https://developer.salesforce.com/docs/marketing/pardot/guide/custom-redirect-v5.html) (full refresh)
- [Dynamic Content](https://developer.salesforce.com/docs/marketing/pardot/guide/dynamic-content-v5.html) (incremental)
- [Dynamic Content Variations](https://developer.salesforce.com/docs/marketing/pardot/guide/dynamic-content-variation.html) (incremental parent)
- [Emails](https://developer.salesforce.com/docs/marketing/pardot/guide/email-v5.html) (incremental)
- [Email Clicks (v4 API)](https://developer.salesforce.com/docs/marketing/pardot/guide/batch-email-clicks-v4.html) (incremental)
- [Engagement Studio Programs](https://developer.salesforce.com/docs/marketing/pardot/guide/engagement-studio-program-v5.html) (incremental)
- [Files](https://developer.salesforce.com/docs/marketing/pardot/guide/export-v5.html) (full refresh)
- [Folders](https://developer.salesforce.com/docs/marketing/pardot/guide/folder-v5.html) (full refresh)
- [Folder Contents](https://developer.salesforce.com/docs/marketing/pardot/guide/folder-contents-v5.html) (incremental)
- [Forms](https://developer.salesforce.com/docs/marketing/pardot/guide/form-v5.html) (full refresh)
- [Form Fields](https://developer.salesforce.com/docs/marketing/pardot/guide/form-field-v5.html) (incremental)
- [Form Handlers](https://developer.salesforce.com/docs/marketing/pardot/guide/form-handler-v5.html) (full refresh)
- [Form Handler Fields](https://developer.salesforce.com/docs/marketing/pardot/guide/form-handler-field-v5.html) (full refresh)
- [Landing Pages](https://developer.salesforce.com/docs/marketing/pardot/guide/landing-page-v5.html) (incremental)
- [Layout Templates](https://developer.salesforce.com/docs/marketing/pardot/guide/layout-template-v5.html) (full refresh)
- [Lifecycle Stages](https://developer.salesforce.com/docs/marketing/pardot/guide/lifecycle-stage-v5.html) (incremental)
- [Lifecycle Histories](https://developer.salesforce.com/docs/marketing/pardot/guide/lifecycle-history-v5.html) (incremental)
- [Lists](https://developer.salesforce.com/docs/marketing/pardot/guide/list-v5.html) (incremental)
- [List Emails](https://developer.salesforce.com/docs/marketing/pardot/guide/list-email-v5.html) (incremental)
- [List Memberships](https://developer.salesforce.com/docs/marketing/pardot/guide/list-membership-v5.html) (incremental)
- [Opportunities](https://developer.salesforce.com/docs/marketing/pardot/guide/opportunity-v5.html) (incremental)
- [Prospects](https://developer.salesforce.com/docs/marketing/pardot/guide/prospect-v5.html) (incremental)
- [Prospect Accounts](https://developer.salesforce.com/docs/marketing/pardot/guide/prospect-account-v5.html) (full refresh)
- [Tags](https://developer.salesforce.com/docs/marketing/pardot/guide/tag-v5.html) (incremental)
- [Tracker Domains](https://developer.salesforce.com/docs/marketing/pardot/guide/tracker-domain-v5.html) (full refresh)
- [Users](https://developer.salesforce.com/docs/marketing/pardot/guide/user-v5.html) (incremental)
- [Visitors](https://developer.salesforce.com/docs/marketing/pardot/guide/visitor-v5.html) (incremental)
- [Visitor Activity](https://developer.salesforce.com/docs/marketing/pardot/guide/visitor-activity-v5.html) (incremental)
- [Visitor Page Views](https://developer.salesforce.com/docs/marketing/pardot/guide/visitor-page-view-v5.html) (incremental)
- [Visits](https://developer.salesforce.com/docs/marketing/pardot/guide/visit-v5.html) (incremental)

If there are more endpoints you'd like Airbyte to support, please [create an issue](https://github.com/airbytehq/airbyte/issues/new/choose).

## Changelog

| Version | Date       | Pull Request                                             | Subject               |
| :------ | :--------- | :------------------------------------------------------- | :-------------------- |
| 1.0.3 | 2025-02-23 | [54624](https://github.com/airbytehq/airbyte/pull/54624) | Update dependencies |
| 1.0.2 | 2025-02-15 | [47530](https://github.com/airbytehq/airbyte/pull/47530) | Update dependencies |
| 1.0.1 | 2025-01-10 | [51040](https://github.com/airbytehq/airbyte/pull/51040) | Fix schemas, adjust error handling, remove split-up interval |
| 1.0.0 | 2024-12-12 | [49424](https://github.com/airbytehq/airbyte/pull/49424) | Update streams to API V5. Fix auth flow |
| 0.2.0 | 2024-10-13 | [44528](https://github.com/airbytehq/airbyte/pull/44528) | Migrate to LowCode then Manifest-only |
| 0.1.22 | 2024-10-12 | [46778](https://github.com/airbytehq/airbyte/pull/46778) | Update dependencies |
| 0.1.21 | 2024-10-05 | [46441](https://github.com/airbytehq/airbyte/pull/46441) | Update dependencies |
| 0.1.20 | 2024-09-28 | [46109](https://github.com/airbytehq/airbyte/pull/46109) | Update dependencies |
| 0.1.19 | 2024-09-21 | [45799](https://github.com/airbytehq/airbyte/pull/45799) | Update dependencies |
| 0.1.18 | 2024-09-14 | [45509](https://github.com/airbytehq/airbyte/pull/45509) | Update dependencies |
| 0.1.17 | 2024-09-07 | [45307](https://github.com/airbytehq/airbyte/pull/45307) | Update dependencies |
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
