# Sendgrid

<HideInUI>

This page contains the setup guide and reference information for the [Sendgrid](https://sendgrid.com/) source connector.

</HideInUI>

## Prerequisites

- [Sendgrid API Key](https://docs.sendgrid.com/ui/account-and-settings/api-keys#creating-an-api-key)

## Setup guide

### Step 1: Set up Sendgrid

- Sendgrid Account
- [Create Sendgrid API Key](https://docs.sendgrid.com/ui/account-and-settings/api-keys#creating-an-api-key) with the following permissions:
- Read-only access to all resources
- Full access to marketing resources

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

- [Campaigns](https://docs.sendgrid.com/api-reference/campaigns-api/retrieve-all-campaigns)
- [Lists](https://docs.sendgrid.com/api-reference/lists/get-all-lists)
- [Contacts](https://docs.sendgrid.com/api-reference/contacts/export-contacts)
- [Stats automations](https://docs.sendgrid.com/api-reference/marketing-campaign-stats/get-all-automation-stats)
- [Segments](https://docs.sendgrid.com/api-reference/segmenting-contacts/get-list-of-segments)
- [Single Sends](https://docs.sendgrid.com/api-reference/marketing-campaign-stats/get-all-single-sends-stats)
- [Templates](https://docs.sendgrid.com/api-reference/transactional-templates/retrieve-paged-transactional-templates)
- [Global suppression](https://docs.sendgrid.com/api-reference/suppressions-global-suppressions/retrieve-all-global-suppressions) \(Incremental\)
- [Suppression groups](https://docs.sendgrid.com/api-reference/suppressions-unsubscribe-groups/retrieve-all-suppression-groups-associated-with-the-user)
- [Suppression group members](https://docs.sendgrid.com/api-reference/suppressions-suppressions/retrieve-all-suppressions) \(Incremental\)
- [Blocks](https://docs.sendgrid.com/api-reference/blocks-api/retrieve-all-blocks) \(Incremental\)
- [Bounces](https://docs.sendgrid.com/api-reference/bounces-api/retrieve-all-bounces) \(Incremental\)
- [Invalid emails](https://docs.sendgrid.com/api-reference/invalid-e-mails-api/retrieve-all-invalid-emails) \(Incremental\)
- [Spam reports](https://docs.sendgrid.com/api-reference/spam-reports-api/retrieve-all-spam-reports)
- [Unsubscribe Groups](https://docs.sendgrid.com/api-reference/suppressions-unsubscribe-groups/retrieve-all-suppression-groups-associated-with-the-user)

## Create a read-only API key (Optional)

While you can set up the Sendgrid connector using any Salesforce user with read permission, we recommend creating a dedicated read-only user for Airbyte. This allows you to granularly control the which resources Airbyte can read.

The API key should be read-only on all resources except Marketing, where it needs Full Access.

## Limitations & Troubleshooting

<details>
<summary>
Expand to see details about Sendgrid connector limitations and troubleshooting.
</summary>

### Connector limitations

#### Rate limiting

The connector is restricted by normal Sendgrid [requests limitation](https://docs.sendgrid.com/api-reference/how-to-use-the-sendgrid-v3-api/rate-limits).

### Troubleshooting

- **Legacy marketing campaigns are not supported by this source connector**. Sendgrid provides two different kinds of marketing campaigns, "legacy marketing campaigns" and "new marketing campaigns". If you are seeing a `403 FORBIDDEN error message for https://api.sendgrid.com/v3/marketing/campaigns`, it might be because your SendGrid account uses legacy marketing campaigns.
- Check out common troubleshooting issues for the Sendgrid source connector on our [Airbyte Forum](https://github.com/airbytehq/airbyte/discussions).

</details>

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                                                                                                                                                                           |
|:--------|:-----------| :------------------------------------------------------- |:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
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
