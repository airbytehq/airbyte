# Sendgrid

<HideInUI>

This page contains the setup guide and reference information for the [Sendgrid](https://sendgrid.com/) source connector.

</HideInUI>

## Prerequisites

- A SendGrid account
- A [SendGrid API Key](https://docs.sendgrid.com/ui/account-and-settings/api-keys#creating-an-api-key) with the required permissions

## Setup guide

### Step 1: Set up SendGrid

Create a SendGrid API Key with the permissions required for the streams you want to sync. The connector uses the [SendGrid v3 API](https://docs.sendgrid.com/api-reference/how-to-use-the-sendgrid-v3-api/authentication).

The following API key scopes are required depending on which streams you enable:

| Streams | Required Scopes |
|---------|-----------------|
| Bounces, Blocks, Spam Reports, Invalid Emails, Global Suppressions | `suppression.read` or the specific `suppression.{type}.read` scopes |
| Suppression Groups, Suppression Group Members | `asm.groups.read` |
| Templates | `templates.read` |
| Contacts, Lists, Segments, Single Sends, Single Send Stats, Stats Automations, Campaigns | `marketing.read` |

For simplicity, you can create an API key with **Full Access** to ensure all streams work correctly. If you prefer more granular permissions, enable only the scopes listed above for the streams you need.

### Step 2: Set up the Sendgrid connector in Airbyte

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account or navigate to the Airbyte Open Source dashboard.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. On the Set up the source page, enter the name for the Sendgrid connector and select **Sendgrid** from the Source type dropdown.
4. Enter your `api_key`.
5. Enter your `start_date`.
6. Click **Set up source**.

<HideInUI>

## Supported sync modes

The Sendgrid source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)

## Supported Streams

- [Blocks](https://docs.sendgrid.com/api-reference/blocks-api/retrieve-all-blocks) \(Incremental\)
- [Bounces](https://docs.sendgrid.com/api-reference/bounces-api/retrieve-all-bounces) \(Incremental\)
- [Campaigns](https://docs.sendgrid.com/api-reference/campaigns-api/retrieve-all-campaigns)
- [Contacts](https://docs.sendgrid.com/api-reference/contacts/export-contacts)
- [Global Suppressions](https://docs.sendgrid.com/api-reference/suppressions-global-suppressions/retrieve-all-global-suppressions) \(Incremental\)
- [Invalid Emails](https://docs.sendgrid.com/api-reference/invalid-e-mails-api/retrieve-all-invalid-emails) \(Incremental\)
- [Lists](https://docs.sendgrid.com/api-reference/lists/get-all-lists)
- [Segments](https://docs.sendgrid.com/api-reference/segmenting-contacts/get-list-of-segments)
- [Single Sends](https://docs.sendgrid.com/api-reference/single-sends/get-all-single-sends)
- [Single Send Stats](https://docs.sendgrid.com/api-reference/marketing-campaign-stats/get-all-single-sends-stats)
- [Spam Reports](https://docs.sendgrid.com/api-reference/spam-reports-api/retrieve-all-spam-reports) \(Incremental\)
- [Stats Automations](https://docs.sendgrid.com/api-reference/marketing-campaign-stats/get-all-automation-stats)
- [Suppression Groups](https://docs.sendgrid.com/api-reference/suppressions-unsubscribe-groups/retrieve-all-suppression-groups-associated-with-the-user)
- [Suppression Group Members](https://docs.sendgrid.com/api-reference/suppressions-suppressions/retrieve-all-suppressions) \(Incremental\)
- [Templates](https://docs.sendgrid.com/api-reference/transactional-templates/retrieve-paged-transactional-templates)

## Create a read-only API key (Optional)

While you can set up the SendGrid connector using any API key with read permission, we recommend creating a dedicated read-only API key for Airbyte. This allows you to granularly control which resources Airbyte can read.

The API key should have read-only access to the resources you want to sync. For marketing streams (Contacts, Lists, Segments, Single Sends, Campaigns), the API key needs the `marketing.read` scope.

## Limitations & Troubleshooting

<details>
<summary>
Expand to see details about Sendgrid connector limitations and troubleshooting.
</summary>

### Connector limitations

#### Rate limiting

The connector is restricted by normal Sendgrid [requests limitation](https://docs.sendgrid.com/api-reference/how-to-use-the-sendgrid-v3-api/rate-limits).

### Troubleshooting

#### 403 Forbidden errors

If you encounter 403 errors, check the following:

1. **Verify API key permissions**: Ensure your API key has the required scopes for the streams you're trying to sync. See the [Setup guide](#step-1-set-up-sendgrid) for the specific scopes needed for each stream.

2. **Legacy vs. New Marketing Campaigns**: This connector uses the New Marketing Campaigns API (`/v3/marketing/*`), which requires the `marketing.read` scope. If your SendGrid account uses Legacy Marketing Campaigns, you will receive 403 errors when syncing marketing streams. Legacy Marketing Campaigns use different API endpoints and permission scopes (`marketing_campaigns.read`) that are not compatible with this connector.

3. **Account type limitations**: Some SendGrid account types may not have access to all API endpoints. Verify that your SendGrid plan includes access to the features you're trying to sync.

</details>

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                                                                                                                                                                           |
|:--------|:-----------| :------------------------------------------------------- |:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1.3.20 | 2025-11-25 | [69988](https://github.com/airbytehq/airbyte/pull/69988) | Update dependencies |
| 1.3.19 | 2025-11-18 | [69685](https://github.com/airbytehq/airbyte/pull/69685) | Update dependencies |
| 1.3.18 | 2025-10-29 | [68852](https://github.com/airbytehq/airbyte/pull/68852) | Update dependencies |
| 1.3.17 | 2025-10-22 | [68591](https://github.com/airbytehq/airbyte/pull/68591) | Add `suggestedStreams` |
| 1.3.16 | 2025-10-21 | [68410](https://github.com/airbytehq/airbyte/pull/68410) | Update dependencies |
| 1.3.15 | 2025-10-14 | [67931](https://github.com/airbytehq/airbyte/pull/67931) | Update dependencies |
| 1.3.14 | 2025-10-07 | [67227](https://github.com/airbytehq/airbyte/pull/67227) | Update dependencies |
| 1.3.13 | 2025-09-30 | [66871](https://github.com/airbytehq/airbyte/pull/66871) | Update dependencies |
| 1.3.12 | 2025-09-23 | [62286](https://github.com/airbytehq/airbyte/pull/62286) | Update dependencies |
| 1.3.11 | 2025-09-11 | [66078](https://github.com/airbytehq/airbyte/pull/66078) | Update to CDK v7 |
| 1.3.10 | 2025-06-21 | [61826](https://github.com/airbytehq/airbyte/pull/61826) | Update dependencies |
| 1.3.9 | 2025-06-14 | [61314](https://github.com/airbytehq/airbyte/pull/61314) | Update dependencies |
| 1.3.8 | 2025-05-25 | [60199](https://github.com/airbytehq/airbyte/pull/60199) | Update dependencies |
| 1.3.7 | 2025-05-04 | [58982](https://github.com/airbytehq/airbyte/pull/58982) | Update dependencies |
| 1.3.6 | 2025-04-19 | [58405](https://github.com/airbytehq/airbyte/pull/58405) | Update dependencies |
| 1.3.5 | 2025-04-12 | [57952](https://github.com/airbytehq/airbyte/pull/57952) | Update dependencies |
| 1.3.4 | 2025-04-05 | [57415](https://github.com/airbytehq/airbyte/pull/57415) | Update dependencies |
| 1.3.3 | 2025-03-29 | [56746](https://github.com/airbytehq/airbyte/pull/56746) | Update dependencies |
| 1.3.2 | 2025-03-22 | [55038](https://github.com/airbytehq/airbyte/pull/55038) | Update dependencies |
| 1.3.1 | 2025-03-13 | [55744](https://github.com/airbytehq/airbyte/pull/55744) | Increase max concurrent async job count to 2 |
| 1.3.0 | 2025-03-04 | [55185](https://github.com/airbytehq/airbyte/pull/55185) | Update manifest for adapting changes with AsyncRetriever |
| 1.2.9 | 2025-02-23 | [54625](https://github.com/airbytehq/airbyte/pull/54625) | Update dependencies |
| 1.2.8 | 2025-02-15 | [54013](https://github.com/airbytehq/airbyte/pull/54013) | Update dependencies |
| 1.2.7 | 2025-02-08 | [53508](https://github.com/airbytehq/airbyte/pull/53508) | Update dependencies |
| 1.2.6 | 2025-02-01 | [52995](https://github.com/airbytehq/airbyte/pull/52995) | Update dependencies |
| 1.2.5 | 2025-01-25 | [52535](https://github.com/airbytehq/airbyte/pull/52535) | Update dependencies |
| 1.2.4 | 2025-01-18 | [51892](https://github.com/airbytehq/airbyte/pull/51892) | Update dependencies |
| 1.2.3 | 2025-01-11 | [48238](https://github.com/airbytehq/airbyte/pull/48238) | Update dependencies |
| 1.2.2 | 2024-10-29 | [47836](https://github.com/airbytehq/airbyte/pull/47836) | Update dependencies |
| 1.2.1 | 2024-10-28 | [47588](https://github.com/airbytehq/airbyte/pull/47588) | Update dependencies |
| 1.2.0 | 2024-10-13 | [46870](https://github.com/airbytehq/airbyte/pull/46870) | Migrate to Manifest-only |
| 1.1.5 | 2024-10-12 | [46781](https://github.com/airbytehq/airbyte/pull/46781) | Update dependencies |
| 1.1.4 | 2024-10-05 | [46460](https://github.com/airbytehq/airbyte/pull/46460) | Update dependencies |
| 1.1.3 | 2024-09-28 | [46105](https://github.com/airbytehq/airbyte/pull/46105) | Update dependencies |
| 1.1.2 | 2024-09-21 | [45782](https://github.com/airbytehq/airbyte/pull/45782) | Update dependencies |
| 1.1.1 | 2024-09-14 | [45525](https://github.com/airbytehq/airbyte/pull/45525) | Update dependencies |
| 1.1.0 | 2024-09-11 | [45191](https://github.com/airbytehq/airbyte/pull/45191) | Move Contacts stream to declarative async job |
| 1.0.18 | 2024-09-07 | [45239](https://github.com/airbytehq/airbyte/pull/45239) | Update dependencies |
| 1.0.17 | 2024-08-31 | [44953](https://github.com/airbytehq/airbyte/pull/44953) | Update dependencies |
| 1.0.16 | 2024-08-24 | [44753](https://github.com/airbytehq/airbyte/pull/44753) | Update dependencies |
| 1.0.15 | 2024-08-17 | [44233](https://github.com/airbytehq/airbyte/pull/44233) | Update dependencies |
| 1.0.14 | 2024-08-12 | [43751](https://github.com/airbytehq/airbyte/pull/43751) | Update dependencies |
| 1.0.13 | 2024-08-10 | [43635](https://github.com/airbytehq/airbyte/pull/43635) | Update dependencies |
| 1.0.12 | 2024-08-03 | [43269](https://github.com/airbytehq/airbyte/pull/43269) | Update dependencies |
| 1.0.11 | 2024-07-27 | [42729](https://github.com/airbytehq/airbyte/pull/42729) | Update dependencies |
| 1.0.10 | 2024-07-20 | [42310](https://github.com/airbytehq/airbyte/pull/42310) | Update dependencies |
| 1.0.9 | 2024-07-13 | [41753](https://github.com/airbytehq/airbyte/pull/41753) | Update dependencies |
| 1.0.8 | 2024-07-10 | [41531](https://github.com/airbytehq/airbyte/pull/41531) | Update dependencies |
| 1.0.7 | 2024-07-09 | [41137](https://github.com/airbytehq/airbyte/pull/41137) | Update dependencies |
| 1.0.6 | 2024-07-06 | [40898](https://github.com/airbytehq/airbyte/pull/40898) | Update dependencies |
| 1.0.5 | 2024-06-25 | [40356](https://github.com/airbytehq/airbyte/pull/40356) | Update dependencies |
| 1.0.4 | 2024-06-22 | [40155](https://github.com/airbytehq/airbyte/pull/40155) | Update dependencies |
| 1.0.3 | 2024-06-06 | [39197](https://github.com/airbytehq/airbyte/pull/39197) | [autopull] Upgrade base image to v1.2.2 |
| 1.0.2 | 2024-05-21 | [38478](https://github.com/airbytehq/airbyte/pull/38478) | Update deprecated authenticator package |
| 1.0.1 | 2024-05-20 | [38264](https://github.com/airbytehq/airbyte/pull/38264) | Replace AirbyteLogger with logging.Logger |
| 1.0.0 | 2024-04-15 | [35776](https://github.com/airbytehq/airbyte/pull/35776) | Migration to low-code CDK. Breaking change that updates configuration keys, removes unsubscribe_groups stream, renames a stream to singlesend_stats, and adds the singlesends stream. |
| 0.5.0 | 2024-03-26 | [36455](https://github.com/airbytehq/airbyte/pull/36455) | Unpin CDK version, add record counts to state messages |
| 0.4.3   | 2024-02-21 | [35181](https://github.com/airbytehq/airbyte/pull/35343) | Handle uncompressed contacts downloads.                                                                                                                                                                                                           |
| 0.4.2   | 2024-02-12 | [35181](https://github.com/airbytehq/airbyte/pull/35181) | Manage dependencies with Poetry.                                                                                                                                                                                                                  |
| 0.4.1   | 2023-10-18 | [31543](https://github.com/airbytehq/airbyte/pull/31543) | Base image migration: remove Dockerfile and use the python-connector-base image                                                                                                                                                                   |
| 0.4.0   | 2023-05-19 | [23959](https://github.com/airbytehq/airbyte/pull/23959) | Add `unsubscribe_groups`stream                                                                                                                                                                                                                    |
| 0.3.1   | 2023-01-27 | [21939](https://github.com/airbytehq/airbyte/pull/21939) | Fix contacts missing records; Remove Messages stream                                                                                                                                                                                              |
| 0.3.0   | 2023-01-25 | [21587](https://github.com/airbytehq/airbyte/pull/21587) | Make sure spec works as expected in UI - make start_time parameter an ISO string instead of an integer interpreted as timestamp (breaking, update your existing connections and set the start_time parameter to ISO 8601 date time string in UTC) |
| 0.2.16  | 2022-11-02 | [18847](https://github.com/airbytehq/airbyte/pull/18847) | Skip the stream on `400, 401 - authorization required` with log message                                                                                                                                                                           |
| 0.2.15  | 2022-10-19 | [18182](https://github.com/airbytehq/airbyte/pull/18182) | Mark the sendgrid api key secret in the spec                                                                                                                                                                                                      |
| 0.2.14  | 2022-09-07 | [16400](https://github.com/airbytehq/airbyte/pull/16400) | Change Start Time config parameter to datetime string                                                                                                                                                                                             |
| 0.2.13  | 2022-08-29 | [16112](https://github.com/airbytehq/airbyte/pull/16112) | Revert back to Python CDK                                                                                                                                                                                                                         |
| 0.2.12  | 2022-08-24 | [15911](https://github.com/airbytehq/airbyte/pull/15911) | Bugfix to allowing reading schemas at runtime                                                                                                                                                                                                     |
| 0.2.11  | 2022-08-19 | [15800](https://github.com/airbytehq/airbyte/pull/15800) | Bugfix to allow reading sentry.yaml at runtime                                                                                                                                                                                                    |
| 0.2.10  | 2022-08-17 | [15734](https://github.com/airbytehq/airbyte/pull/15734) | Fix yaml based on the new schema validator                                                                                                                                                                                                        |
| 0.2.9   | 2022-08-11 | [15257](https://github.com/airbytehq/airbyte/pull/15257) | Migrate to config-based framework                                                                                                                                                                                                                 |
| 0.2.8   | 2022-06-07 | [13571](https://github.com/airbytehq/airbyte/pull/13571) | Add Message stream                                                                                                                                                                                                                                |
| 0.2.7   | 2021-09-08 | [5910](https://github.com/airbytehq/airbyte/pull/5910)   | Add Single Sends Stats stream                                                                                                                                                                                                                     |
| 0.2.6   | 2021-07-19 | [4839](https://github.com/airbytehq/airbyte/pull/4839)   | Gracefully handle malformed responses from the API                                                                                                                                                                                                |

</details>

</HideInUI>
