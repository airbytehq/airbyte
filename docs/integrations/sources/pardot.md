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

- **Pardot Business Unit ID** (`pardot_business_unit_id`): The 18-character ID, starting with `0Uv`, of the Account Engagement business unit to sync. In Salesforce Setup, enter `Business Unit Setup` in the **Quick Find** box and select **Business Unit Setup**. See [Find the Account Engagement business unit ID](https://developer.salesforce.com/docs/marketing/pardot/guide/authentication.html).

- **Client ID** (`client_id`): The Consumer Key of the Salesforce External Client App or Connected App used for this connection. Find it in Salesforce Setup, in the app's OAuth settings.

- **Client Secret** (`client_secret`): The Consumer Secret of the Salesforce External Client App or Connected App used for this connection. Find it in Salesforce Setup, in the app's OAuth settings.

- **Refresh Token** (`refresh_token`): Salesforce refresh token that Airbyte uses to access your Account Engagement data. To get one:
  1. In Salesforce Setup, create an [External Client App](https://help.salesforce.com/s/articleView?id=xcloud.external_client_apps.htm&type=5) with OAuth enabled. Since Spring '26, Salesforce no longer lets you create new connected apps by default. Existing connected apps keep working.
  2. Select the **Manage Pardot services (`pardot_api`)** and **Perform requests at any time (`refresh_token`, `offline_access`)** OAuth scopes. Account Engagement rejects tokens that don't have the `pardot_api` scope. See [Account Engagement API authentication](https://developer.salesforce.com/docs/marketing/pardot/guide/authentication.html).
  3. Use the OAuth web server (authorization code) flow to get a refresh token for a user who has access to Account Engagement.
  4. Don't turn on **Refresh Token Rotation** or **Immediately expire refresh token** for this app. The connector stores one refresh token and can't save a new one that Salesforce issues on every refresh.

:::caution Refresh tokens expire after 30 days without use
Starting November 4, 2026, Salesforce expires production refresh tokens that haven't been used for 30 days. Every sync uses the refresh token and restarts that 30-day window. A connection that syncs at least once every 30 days keeps working. If a connection is paused, or scheduled to sync less often than every 30 days, its refresh token expires and syncs fail to authenticate. To recover, generate a new refresh token and update the source.
:::

### Optional configuration options

- **Start Date** (`start_date`): UTC date and time in the format `2020-01-25T00:00:00Z`. Any data before this date will not be replicated. Defaults to `2007-01-01T00:00:00Z` (the year Pardot was launched)

- **Sandbox** (`is_sandbox`): Turn on for a Salesforce sandbox. The connector then signs in at `test.salesforce.com` and reads from `pi.demo.pardot.com`.

- **API host** (`pardot_api_host`): Leave empty to follow **Sandbox**: `pi.demo.pardot.com` for a sandbox, `pi.pardot.com` otherwise. Select `pi.demo.pardot.com` for a Developer Edition or demo org, and `pi.pardot.com` for a training account. To check, find the `b2bmaIntegration` package in Salesforce Setup under **Installed Packages**: the namespace prefix `pi3` means `pi.demo.pardot.com`, and `b2bma` means `pi.pardot.com`. When set, it overrides the host that **Sandbox** selects.

- **Number of concurrent workers** (`num_workers`): How many streams are read at the same time, from 2 to 5. Defaults to 3. Account Engagement allows five concurrent requests per account, so lower it if other integrations use the same account.

## Supported Sync Modes

The Pardot source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes):

- Full Refresh
- Incremental

Most incremental streams use the `updatedAt` field as the cursor. The exceptions are **Emails**, which uses `sentAt`, **Lifecycle Histories** and **Visitor Page Views**, which use `createdAt`, and **Email Clicks**, which uses `created_at`.

### Rate limits

Account Engagement limits the number of API requests your account can make each day, based on your edition.

When Account Engagement returns a rate limit error (HTTP 429, or error code 66 for too many concurrent requests), a server error (5xx), or a request timeout (408), the connector retries the request up to five times, with waits that grow from seconds to minutes, about ten minutes in all. If the last retry also fails, the sync fails.

When the daily limit is used up (error code 122, `Daily API rate limit met`), the sync fails at once with a message that says the limit resets at the start of the next day in the account's time zone. The next sync continues from the last saved position.

### Errors that need a change in your setup

These errors fail the sync at once, with a message that says what to fix:

- Error code 184: Account Engagement rejected the access token. Check that the Salesforce app has the **Manage Pardot services (`pardot_api`)** scope and that the user behind the refresh token is synced to this business unit.
- Error code 201: no active business unit has this Business Unit ID on this host. Check the ID. Turn on **Sandbox** for a sandbox, and set **API host** to `pi.demo.pardot.com` for a Developer Edition or demo org, or to `pi.pardot.com` for a production or training account.
- Error code 49: the user can't read this object. The message names the Account Engagement ability the stream needs. Ask an admin for it, or deselect the stream.
- An expired or revoked refresh token: create a new refresh token and update the source.
- A wrong client ID or client secret: copy the Consumer Key and Consumer Secret of the Salesforce app into **Client ID** and **Client Secret**, and turn on **Sandbox** for a sandbox org.

## Supported Streams

Several output streams are available from this source. Unless noted otherwise, streams are from Pardot's v5 API:

- [Account (Metadata)](https://developer.salesforce.com/docs/marketing/pardot/guide/account-v5.html) (full refresh)
- [Campaigns](https://developer.salesforce.com/docs/marketing/pardot/guide/campaign-v5.html) (incremental)
- [Custom Fields](https://developer.salesforce.com/docs/marketing/pardot/guide/custom-field-v5.html) (incremental)
- [Custom Redirects](https://developer.salesforce.com/docs/marketing/pardot/guide/custom-redirect-v5.html) (full refresh)
- [Dynamic Content](https://developer.salesforce.com/docs/marketing/pardot/guide/dynamic-content-v5.html) (incremental)
- [Dynamic Content Variations](https://developer.salesforce.com/docs/marketing/pardot/guide/dynamic-content-variation.html) (full refresh)
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

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

| Version | Date       | Pull Request                                             | Subject               |
| :------ | :--------- | :------------------------------------------------------- | :-------------------- |
| 1.1.0 | 2026-11-17 | [93055](https://github.com/airbytehq/airbyte/pull/93055) | Faster retries with clear errors, one login at a time, demo host for sandboxes, inclusive cursor filters, up to five workers |
| 1.0.65 | 2026-11-17 | [93309](https://github.com/airbytehq/airbyte/pull/93309) | Update dependencies |
| 1.0.64 | 2026-11-16 | [90951](https://github.com/airbytehq/airbyte/pull/90951) | Show a specific message when the Pardot daily API request limit is reached |
| 1.0.63 | 2026-11-10 | [91648](https://github.com/airbytehq/airbyte/pull/91648) | Update dependencies |
| 1.0.62 | 2026-11-03 | [90699](https://github.com/airbytehq/airbyte/pull/90699) | Update dependencies |
| 1.0.61 | 2026-10-27 | [89997](https://github.com/airbytehq/airbyte/pull/89997) | Update dependencies |
| 1.0.60 | 2026-10-20 | [89350](https://github.com/airbytehq/airbyte/pull/89350) | Update dependencies |
| 1.0.59 | 2026-10-13 | [88747](https://github.com/airbytehq/airbyte/pull/88747) | Update dependencies |
| 1.0.58 | 2026-10-06 | [87980](https://github.com/airbytehq/airbyte/pull/87980) | Update dependencies |
| 1.0.57 | 2026-09-29 | [87294](https://github.com/airbytehq/airbyte/pull/87294) | Update dependencies |
| 1.0.56 | 2026-09-22 | [86757](https://github.com/airbytehq/airbyte/pull/86757) | Update dependencies |
| 1.0.55 | 2026-09-15 | [86177](https://github.com/airbytehq/airbyte/pull/86177) | Update dependencies |
| 1.0.54 | 2026-09-08 | [85565](https://github.com/airbytehq/airbyte/pull/85565) | Update dependencies |
| 1.0.53 | 2026-08-18 | [84703](https://github.com/airbytehq/airbyte/pull/84703) | Update dependencies |
| 1.0.52 | 2026-08-11 | [84070](https://github.com/airbytehq/airbyte/pull/84070) | Update dependencies |
| 1.0.51 | 2026-08-04 | [83553](https://github.com/airbytehq/airbyte/pull/83553) | Update dependencies |
| 1.0.50 | 2026-07-28 | [83046](https://github.com/airbytehq/airbyte/pull/83046) | Update dependencies |
| 1.0.49 | 2026-07-21 | [82532](https://github.com/airbytehq/airbyte/pull/82532) | Update dependencies |
| 1.0.48 | 2026-07-14 | [81946](https://github.com/airbytehq/airbyte/pull/81946) | Update dependencies |
| 1.0.47 | 2026-06-30 | [81183](https://github.com/airbytehq/airbyte/pull/81183) | Update dependencies |
| 1.0.46 | 2026-06-23 | [80586](https://github.com/airbytehq/airbyte/pull/80586) | Update dependencies |
| 1.0.45 | 2026-06-16 | [79997](https://github.com/airbytehq/airbyte/pull/79997) | Update dependencies |
| 1.0.44 | 2026-06-09 | [79466](https://github.com/airbytehq/airbyte/pull/79466) | Update dependencies |
| 1.0.43 | 2026-06-02 | [78883](https://github.com/airbytehq/airbyte/pull/78883) | Update dependencies |
| 1.0.42 | 2026-04-28 | [77362](https://github.com/airbytehq/airbyte/pull/77362) | Update dependencies |
| 1.0.41 | 2026-04-21 | [76711](https://github.com/airbytehq/airbyte/pull/76711) | Update dependencies |
| 1.0.40 | 2026-03-31 | [75820](https://github.com/airbytehq/airbyte/pull/75820) | Update dependencies |
| 1.0.39 | 2026-03-24 | [75021](https://github.com/airbytehq/airbyte/pull/75021) | Update dependencies |
| 1.0.38 | 2026-03-10 | [74501](https://github.com/airbytehq/airbyte/pull/74501) | Update dependencies |
| 1.0.37 | 2026-03-03 | [74170](https://github.com/airbytehq/airbyte/pull/74170) | Update dependencies |
| 1.0.36 | 2026-02-10 | [73068](https://github.com/airbytehq/airbyte/pull/73068) | Update dependencies |
| 1.0.35 | 2026-01-20 | [72176](https://github.com/airbytehq/airbyte/pull/72176) | Update dependencies |
| 1.0.34 | 2026-01-14 | [71683](https://github.com/airbytehq/airbyte/pull/71683) | Update dependencies |
| 1.0.33 | 2025-12-18 | [70501](https://github.com/airbytehq/airbyte/pull/70501) | Update dependencies |
| 1.0.32 | 2025-11-25 | [70091](https://github.com/airbytehq/airbyte/pull/70091) | Update dependencies |
| 1.0.31 | 2025-11-18 | [69674](https://github.com/airbytehq/airbyte/pull/69674) | Update dependencies |
| 1.0.30 | 2025-10-29 | [69020](https://github.com/airbytehq/airbyte/pull/69020) | Update dependencies |
| 1.0.29 | 2025-10-21 | [68326](https://github.com/airbytehq/airbyte/pull/68326) | Update dependencies |
| 1.0.28 | 2025-10-14 | [67800](https://github.com/airbytehq/airbyte/pull/67800) | Update dependencies |
| 1.0.27 | 2025-10-07 | [67342](https://github.com/airbytehq/airbyte/pull/67342) | Update dependencies |
| 1.0.26 | 2025-09-30 | [66393](https://github.com/airbytehq/airbyte/pull/66393) | Update dependencies |
| 1.0.25 | 2025-09-24 | [66592](https://github.com/airbytehq/airbyte/pull/66592) | Fix pagination when >100K records returned |
| 1.0.24 | 2025-09-09 | [65782](https://github.com/airbytehq/airbyte/pull/65782) | Update dependencies |
| 1.0.23 | 2025-08-23 | [65172](https://github.com/airbytehq/airbyte/pull/65172) | Update dependencies |
| 1.0.22 | 2025-08-16 | [64794](https://github.com/airbytehq/airbyte/pull/64794) | Update dependencies |
| 1.0.21 | 2025-08-02 | [64264](https://github.com/airbytehq/airbyte/pull/64264) | Update dependencies |
| 1.0.20 | 2025-07-26 | [63887](https://github.com/airbytehq/airbyte/pull/63887) | Update dependencies |
| 1.0.19 | 2025-07-19 | [63399](https://github.com/airbytehq/airbyte/pull/63399) | Update dependencies |
| 1.0.18 | 2025-07-12 | [63221](https://github.com/airbytehq/airbyte/pull/63221) | Update dependencies |
| 1.0.17 | 2025-07-05 | [62559](https://github.com/airbytehq/airbyte/pull/62559) | Update dependencies |
| 1.0.16 | 2025-06-28 | [61048](https://github.com/airbytehq/airbyte/pull/61048) | Update dependencies |
| 1.0.15 | 2025-06-20 | [61736](https://github.com/airbytehq/airbyte/pull/61736) | Fix lifecycle_stages -  was erroneously top-level instead of a property of column |
| 1.0.14 | 2025-05-24 | [60515](https://github.com/airbytehq/airbyte/pull/60515) | Update dependencies |
| 1.0.13 | 2025-05-10 | [60108](https://github.com/airbytehq/airbyte/pull/60108) | Update dependencies |
| 1.0.12 | 2025-05-04 | [59521](https://github.com/airbytehq/airbyte/pull/59521) | Update dependencies |
| 1.0.11 | 2025-04-27 | [59088](https://github.com/airbytehq/airbyte/pull/59088) | Update dependencies |
| 1.0.10 | 2025-04-19 | [58468](https://github.com/airbytehq/airbyte/pull/58468) | Update dependencies |
| 1.0.9 | 2025-04-12 | [57875](https://github.com/airbytehq/airbyte/pull/57875) | Update dependencies |
| 1.0.8 | 2025-04-05 | [57321](https://github.com/airbytehq/airbyte/pull/57321) | Update dependencies |
| 1.0.7 | 2025-03-29 | [56777](https://github.com/airbytehq/airbyte/pull/56777) | Update dependencies |
| 1.0.6 | 2025-03-22 | [56190](https://github.com/airbytehq/airbyte/pull/56190) | Update dependencies |
| 1.0.5 | 2025-03-08 | [55566](https://github.com/airbytehq/airbyte/pull/55566) | Update dependencies |
| 1.0.4 | 2025-03-01 | [55009](https://github.com/airbytehq/airbyte/pull/55009) | Update dependencies |
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
