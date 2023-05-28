# Close.com

## Prerequisites

* Close.com Account
* Close.com API Key

Visit the [Close.com API Keys page](https://app.close.com/settings/api/) in the Close.com dashboard to access the secret key for your account. Secret key will be prefixed with `api_`.
See [this guide](https://help.close.com/docs/api-keys) if you need to create a new one.

We recommend creating a restricted key specifically for Airbyte access. This will allow you to control which resources Airbyte should be able to access. For ease of use, we recommend using read permissions for all resources and configuring which resource to replicate in the Airbyte UI.

## Setup Guide

### Obtain Close.com API Key

To configure the Close.com source connector in Airbyte, you'll need a Close.com API key. Follow the steps below to obtain an API key:

1. [Log in](https://app.close.com/login/) to your Close.com account.
2. Click on your profile icon in the top-right corner and select **Settings**.
3. In the left sidebar, click on **API Keys**.
4. Click **+ New API Key** in the top-right corner.
5. Provide a description for this API key, such as "Airbyte."
6. Save the API key. You'll need it to set up the connector in Airbyte. _Note: The API key is only displayed once when created, so make sure to copy it.

For more details, consult the [Close.com API Key documentation](https://help.close.com/docs/where-to-find-your-api-key).

### Configure the Close.com Connector in Airbyte

With your Close.com API key in hand, you can set up the connector in Airbyte:

1. In the Airbyte new source configuration form, locate the `API Key` field.
2. Paste the API key you obtained from Close.com into the `API Key` field. The key usually starts with `api_`.
3. In the `Start Date` field, enter a start date for the data sync. The format should be "YYYY-MM-DD" (e.g., "2021-01-01"). You can leave this field blank for a full sync of your data.
4. Click **Set up source** to complete the configuration.

With these steps, you have successfully set up the Close.com source connector in Airbyte.

## Supported sync modes

The Close.com source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

## Supported Streams

This Source is capable of syncing the following core Streams:

* [Leads](https://developer.close.com/#leads) \(Incremental\)
* [Created Activities](https://developer.close.com/#activities-list-or-filter-all-created-activities) \(Incremental\)
* [Opportunity Status Change Activities](https://developer.close.com/#activities-list-or-filter-all-opportunitystatuschange-activities) \(Incremental\)
* [Note Activities](https://developer.close.com/#activities-list-or-filter-all-note-activities) \(Incremental\)
* [Meeting Activities](https://developer.close.com/#activities-list-or-filter-all-meeting-activities) \(Incremental\)
* [Call Activities](https://developer.close.com/#activities-list-or-filter-all-call-activities) \(Incremental\)
* [Email Activities](https://developer.close.com/#activities-list-or-filter-all-email-activities) \(Incremental\)
* [Email Thread Activities](https://developer.close.com/#activities-list-or-filter-all-emailthread-activities) \(Incremental\)
* [Lead Status Change Activities](https://developer.close.com/#activities-list-or-filter-all-leadstatuschange-activities) \(Incremental\)
* [SMS Activities](https://developer.close.com/#activities-list-or-filter-all-sms-activities) \(Incremental\)
* [Task Completed Activities](https://developer.close.com/#activities-list-or-filter-all-taskcompleted-activities) \(Incremental\)
* [Lead Tasks](https://developer.close.com/#tasks) \(Incremental\)
* [Incoming Email Tasks](https://developer.close.com/#tasks) \(Incremental\)
* [Email Followup Tasks](https://developer.close.com/#tasks) \(Incremental\)
* [Missed Call Tasks](https://developer.close.com/#tasks) \(Incremental\)
* [Answered Detached Call Tasks](https://developer.close.com/#tasks) \(Incremental\)
* [Voicemail Tasks](https://developer.close.com/#tasks) \(Incremental\)
* [Opportunity Due Tasks](https://developer.close.com/#tasks) \(Incremental\)
* [Incoming SMS Tasks](https://developer.close.com/#tasks) \(Incremental\)
* [Events](https://developer.close.com/#event-log) \(Incremental\)
* [Lead Custom Fields](https://developer.close.com/#custom-fields-list-all-the-lead-custom-fields-for-your-organization)
* [Contact Custom Fields](https://developer.close.com/#custom-fields-list-all-the-contact-custom-fields-for-your-organization)
* [Opportunity Custom Fields](https://developer.close.com/#custom-fields-list-all-the-opportunity-custom-fields-for-your-organization) 
* [Activity Custom Fields](https://developer.close.com/#custom-fields-list-all-the-activity-custom-fields-for-your-organization) 
* [Users](https://developer.close.com/#users) 
* [Contacts](https://developer.close.com/#contacts) 
* [Opportunities](https://developer.close.com/#opportunities) \(Incremental\)
* [Roles](https://developer.close.com/#roles) 
* [Lead Statuses](https://developer.close.com/#lead-statuses) 
* [Opportunity Statuses](https://developer.close.com/#opportunity-statuses) 
* [Pipelines](https://developer.close.com/#pipelines) 
* [Email Templates](https://developer.close.com/#email-templates) 
* [Google Connected Accounts](https://developer.close.com/#connected-accounts) 
* [Custom Email Connected Accounts](https://developer.close.com/#connected-accounts) 
* [Zoom Connected Accounts](https://developer.close.com/#connected-accounts) 
* [Send As](https://developer.close.com/#send-as) 
* [Email Sequences](https://developer.close.com/#email-sequences) 
* [Dialer](https://developer.close.com/#dialer) 
* [Smart Views](https://developer.close.com/#smart-views) 
* [Email Bulk Actions](https://developer.close.com/#bulk-actions-list-bulk-emails) 
* [Sequence Subscription Bulk Actions](https://developer.close.com/#bulk-actions-list-bulk-sequence-subscriptions) 
* [Delete Bulk Actions](https://developer.close.com/#bulk-actions-list-bulk-deletes) 
* [Edit Bulk Actions](https://developer.close.com/#bulk-actions-list-bulk-edits) 
* [Integration Links](https://developer.close.com/#integration-links) 
* [Custom Activities](https://developer.close.com/#custom-activities) 

### Notes

Leads, Events Incremental streams use `date_updated` field as a cursor. All other Incremental streams use `date_created` field for the same purpose.

`SendAs` stream requires payment.

### Data type mapping

The [Close.com API](https://developer.close.com/) uses the same [JSONSchema](https://json-schema.org/understanding-json-schema/reference/index.html) types that Airbyte uses internally (`string`, `date-time`, `object`, `array`, `boolean`, `integer`, and `number`), so no type conversions happen as part of this source.

### Performance considerations

The Close.com Connector has rate limit. There are 60 RPS for Organizations. You can find detailed info [here](https://developer.close.com/#ratelimits).

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                                                |
|:--------|:-----------|:---------------------------------------------------------|:-------------------------------------------------------------------------------------------------------|
| 0.3.0   | 2023-05-12 | [26024](https://github.com/airbytehq/airbyte/pull/26024) | Update the `Email sequences` stream schema                                                             |
| 0.2.2   | 2023-05-05 | [25868](https://github.com/airbytehq/airbyte/pull/25868) | Added `CDK TypeTransformer` to gurantee JSON Schema types, added missing properties for `roles` stream |
| 0.2.1   | 2023-02-15 | [23074](https://github.com/airbytehq/airbyte/pull/23074) | Specified date formatting in specification                                                             |
| 0.2.0   | 2022-11-04 | [18968](https://github.com/airbytehq/airbyte/pull/18968) | Migrate to Low-Code                                                                                    |
| 0.1.0   | 2021-08-10 | [5366](https://github.com/airbytehq/airbyte/pull/5366)   | Initial release of Close.com connector for Airbyte                                                     |

