# Sendgrid

<HideInUI>

This page contains the setup guide and reference information for the [Sendgrid](https://sendgrid.com/) source connector.

</HideInUI>

## Prerequisites

* [Sendgrid API Key](https://docs.sendgrid.com/ui/account-and-settings/api-keys#creating-an-api-key)

## Setup guide
### Step 1: Set up Sendgrid

* Sendgrid Account
* [Create Sendgrid API Key](https://docs.sendgrid.com/ui/account-and-settings/api-keys#creating-an-api-key) with the following permissions:
  * Read-only access to all resources
  * Full access to marketing resources

### Step 2: Set up the Sendgrid connector in Airbyte

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account or navigate to the Airbyte Open Source dashboard.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. On the Set up the source page, enter the name for the Sendgrid connector and select **Sendgrid** from the Source type dropdown.
4. Enter your `apikey`.
5. Enter your `start_time`.
6. Click **Set up source**.

<HideInUI>

## Supported sync modes

The Sendgrid source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

* [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
* [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
* [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)

## Supported Streams

* [Campaigns](https://docs.sendgrid.com/api-reference/campaigns-api/retrieve-all-campaigns)
* [Lists](https://docs.sendgrid.com/api-reference/lists/get-all-lists)
* [Contacts](https://docs.sendgrid.com/api-reference/contacts/export-contacts)
* [Stats automations](https://docs.sendgrid.com/api-reference/marketing-campaign-stats/get-all-automation-stats)
* [Segments](https://docs.sendgrid.com/api-reference/segmenting-contacts/get-list-of-segments)
* [Single Sends](https://docs.sendgrid.com/api-reference/marketing-campaign-stats/get-all-single-sends-stats)
* [Templates](https://docs.sendgrid.com/api-reference/transactional-templates/retrieve-paged-transactional-templates)
* [Global suppression](https://docs.sendgrid.com/api-reference/suppressions-global-suppressions/retrieve-all-global-suppressions) \(Incremental\)
* [Suppression groups](https://docs.sendgrid.com/api-reference/suppressions-unsubscribe-groups/retrieve-all-suppression-groups-associated-with-the-user)
* [Suppression group members](https://docs.sendgrid.com/api-reference/suppressions-suppressions/retrieve-all-suppressions)
* [Blocks](https://docs.sendgrid.com/api-reference/blocks-api/retrieve-all-blocks) \(Incremental\)
* [Bounces](https://docs.sendgrid.com/api-reference/bounces-api/retrieve-all-bounces) \(Incremental\)
* [Invalid emails](https://docs.sendgrid.com/api-reference/invalid-e-mails-api/retrieve-all-invalid-emails) \(Incremental\)
* [Spam reports](https://docs.sendgrid.com/api-reference/spam-reports-api/retrieve-all-spam-reports)


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
* **Legacy marketing campaigns are not supported by this source connector**. Sendgrid provides two different kinds of marketing campaigns, "legacy marketing campaigns" and "new marketing campaigns". If you are seeing a `403 FORBIDDEN error message for https://api.sendgrid.com/v3/marketing/campaigns`, it might be because your SendGrid account uses legacy marketing campaigns.
* Check out common troubleshooting issues for the Sendgrid source connector on our [Airbyte Forum](https://github.com/airbytehq/airbyte/discussions).

</details>

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                                                                                                                                                                                           |
|:--------|:-----------|:---------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0.4.1 | 2023-10-18 | [31543](https://github.com/airbytehq/airbyte/pull/31543) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.4.0   | 2023-05-19 | [23959](https://github.com/airbytehq/airbyte/pull/23959) | Add `unsubscribe_groups`stream
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

</HideInUI>