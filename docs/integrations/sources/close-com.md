# Close.com

This page contains the setup guide and reference information for the [Close.com](https://www.close.com/) source connector.

## Prerequisites

- Close.com API Key

We recommend creating a restricted key specifically for Airbyte access. This will allow you to control which resources Airbyte should be able to access. For ease of use, we recommend using read permissions for all resources and configuring which resource to replicate in the Airbyte UI.

## Setup guide

### Step 1: Set up your Close.com API Key

1. [Log in to your Close.com](https://www.close.com) account.
2. At the bottom of the left navbar, select **Settings**.
3. In the left menu, select **Developer**.
4. At the top of the page, click **+ New API Key**.

:::caution
For security purposes, the API Key will only be displayed once upon creation. Be sure to copy and store the key in a secure location.
:::

For further reading on creating and maintaining Close.com API keys, refer to the
[official documentation](https://help.close.com/docs/api-keys-oauth).

### Step 2: Set up the Close.com connector in Airbyte

1. [Log in to your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account, or navigate to the Airbyte Open Source dashboard.
2. From the Airbyte UI, click **Sources**, then click on **+ New Source** and select **Close.com** from the list of available sources.
3. Enter a **Source name** of your choosing.
4. In the **API Key** field, enter your Close.com **API Key**
5. _Optional_ - In the **Replication Start Date** field, you may enter a starting date cutoff for the data you want to replicate. The format for this date should be as such: `YYYY-MM-DD`. Leaving this field blank will replicate all data.
6. Click **Set up source** and wait for the tests to complete.

## Supported sync modes

The Close.com source supports both **Full Refresh** and **Incremental** syncs. You can choose if this connector will copy only the new/updated data, or all rows in the tables and columns you set up for replication. These settings will take effect every time a sync is run.

## Supported streams

This source is capable of syncing the following core streams:

- [Leads](https://developer.close.com/#leads) \(Incremental\)
- [Created Activities](https://developer.close.com/#activities-list-or-filter-all-created-activities) \(Incremental\)
- [Opportunity Status Change Activities](https://developer.close.com/#activities-list-or-filter-all-opportunitystatuschange-activities) \(Incremental\)
- [Note Activities](https://developer.close.com/#activities-list-or-filter-all-note-activities) \(Incremental\)
- [Meeting Activities](https://developer.close.com/#activities-list-or-filter-all-meeting-activities) \(Incremental\)
- [Call Activities](https://developer.close.com/#activities-list-or-filter-all-call-activities) \(Incremental\)
- [Email Activities](https://developer.close.com/#activities-list-or-filter-all-email-activities) \(Incremental\)
- [Email Thread Activities](https://developer.close.com/#activities-list-or-filter-all-emailthread-activities) \(Incremental\)
- [Lead Status Change Activities](https://developer.close.com/#activities-list-or-filter-all-leadstatuschange-activities) \(Incremental\)
- [SMS Activities](https://developer.close.com/#activities-list-or-filter-all-sms-activities) \(Incremental\)
- [Task Completed Activities](https://developer.close.com/#activities-list-or-filter-all-taskcompleted-activities) \(Incremental\)
- [Lead Tasks](https://developer.close.com/#tasks) \(Incremental\)
- [Incoming Email Tasks](https://developer.close.com/#tasks) \(Incremental\)
- [Email Followup Tasks](https://developer.close.com/#tasks) \(Incremental\)
- [Missed Call Tasks](https://developer.close.com/#tasks) \(Incremental\)
- [Answered Detached Call Tasks](https://developer.close.com/#tasks) \(Incremental\)
- [Voicemail Tasks](https://developer.close.com/#tasks) \(Incremental\)
- [Opportunity Due Tasks](https://developer.close.com/#tasks) \(Incremental\)
- [Incoming SMS Tasks](https://developer.close.com/#tasks) \(Incremental\)
- [Events](https://developer.close.com/#event-log) \(Incremental\)
- [Lead Custom Fields](https://developer.close.com/#custom-fields-list-all-the-lead-custom-fields-for-your-organization)
- [Contact Custom Fields](https://developer.close.com/#custom-fields-list-all-the-contact-custom-fields-for-your-organization)
- [Opportunity Custom Fields](https://developer.close.com/#custom-fields-list-all-the-opportunity-custom-fields-for-your-organization)
- [Activity Custom Fields](https://developer.close.com/#custom-fields-list-all-the-activity-custom-fields-for-your-organization)
- [Users](https://developer.close.com/#users)
- [Contacts](https://developer.close.com/#contacts)
- [Opportunities](https://developer.close.com/#opportunities) \(Incremental\)
- [Roles](https://developer.close.com/#roles)
- [Lead Statuses](https://developer.close.com/#lead-statuses)
- [Opportunity Statuses](https://developer.close.com/#opportunity-statuses)
- [Pipelines](https://developer.close.com/#pipelines)
- [Email Templates](https://developer.close.com/#email-templates)
- [Google Connected Accounts](https://developer.close.com/#connected-accounts)
- [Custom Email Connected Accounts](https://developer.close.com/#connected-accounts)
- [Zoom Connected Accounts](https://developer.close.com/#connected-accounts)
- [Send As](https://developer.close.com/#send-as)
- [Email Sequences](https://developer.close.com/#email-sequences)
- [Dialer](https://developer.close.com/#dialer)
- [Smart Views](https://developer.close.com/#smart-views)
- [Email Bulk Actions](https://developer.close.com/#bulk-actions-list-bulk-emails)
- [Sequence Subscription Bulk Actions](https://developer.close.com/#bulk-actions-list-bulk-sequence-subscriptions)
- [Delete Bulk Actions](https://developer.close.com/#bulk-actions-list-bulk-deletes)
- [Edit Bulk Actions](https://developer.close.com/#bulk-actions-list-bulk-edits)
- [Integration Links](https://developer.close.com/#integration-links)
- [Custom Activities](https://developer.close.com/#custom-activities)

### Notes

Leads and Events Incremental streams use the `date_updated` field as a cursor. All other Incremental streams use the `date_created` field for the same purpose.

The `SendAs` stream requires payment.

### Data type mapping

The [Close.com API](https://developer.close.com/) uses the same [JSONSchema](https://json-schema.org/understanding-json-schema/reference/index.html) types that Airbyte uses internally (`string`, `date-time`, `object`, `array`, `boolean`, `integer`, and `number`), so no type conversions happen as part of this source.

### Performance considerations

The Close.com connector is subject to rate limits. For more information on this topic,
[click here](https://developer.close.com/topics/rate-limits/).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                                |
| :------ | :--------- | :------------------------------------------------------- | :----------------------------------------------------------------------------------------------------- |
| 0.5.2   | 2024-06-15 | [39477](https://github.com/airbytehq/airbyte/pull/39477) | Format source, delete requirements.txt                                                                                          |
| 0.5.1   | 2024-05-20 | [38391](https://github.com/airbytehq/airbyte/pull/38391) | [autopull] base image + poetry + up_to_date                                                            |
| 0.5.0   | 2023-11-30 | [32984](https://github.com/airbytehq/airbyte/pull/32984) | Add support for custom fields                                                                          |
| 0.4.3   | 2023-10-28 | [31534](https://github.com/airbytehq/airbyte/pull/31534) | Fixed Email Activities Stream Pagination                                                               |
| 0.4.2   | 2023-08-08 | [29206](https://github.com/airbytehq/airbyte/pull/29206) | Fixed the issue with `DatePicker` format for `start date`                                              |
| 0.4.1   | 2023-07-04 | [27950](https://github.com/airbytehq/airbyte/pull/27950) | Add human readable titles to API Key and Start Date fields                                             |
| 0.4.0   | 2023-06-27 | [27776](https://github.com/airbytehq/airbyte/pull/27776) | Update the `Email Followup Tasks` stream schema                                                        |
| 0.3.0   | 2023-05-12 | [26024](https://github.com/airbytehq/airbyte/pull/26024) | Update the `Email sequences` stream schema                                                             |
| 0.2.2   | 2023-05-05 | [25868](https://github.com/airbytehq/airbyte/pull/25868) | Added `CDK TypeTransformer` to gurantee JSON Schema types, added missing properties for `roles` stream |
| 0.2.1   | 2023-02-15 | [23074](https://github.com/airbytehq/airbyte/pull/23074) | Specified date formatting in specification                                                             |
| 0.2.0   | 2022-11-04 | [18968](https://github.com/airbytehq/airbyte/pull/18968) | Migrate to Low-Code                                                                                    |
| 0.1.0   | 2021-08-10 | [5366](https://github.com/airbytehq/airbyte/pull/5366)   | Initial release of Close.com connector for Airbyte                                                     |

</details>
