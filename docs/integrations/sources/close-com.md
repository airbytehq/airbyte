# Close.com

## Prerequisites

* Close.com Account
* Close.com API Key

Visit the [Close.com API Keys page](https://app.close.com/settings/api/) in the Close.com dashboard to access the secret key for your account. Secret key will be prefixed with `api_`.
See [this guide](https://help.close.com/docs/api-keys) if you need to create a new one.

We recommend creating a restricted key specifically for Airbyte access. This will allow you to control which resources Airbyte should be able to access. For ease of use, we recommend using read permissions for all resources and configuring which resource to replicate in the Airbyte UI.

## Setup guide

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Close.com connector and select **Close.com** from the Source type dropdown.
4. Fill in the API Key and Start date fields and click **Set up source**.

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

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.2.0 | 2022-11-04 | [18968](https://github.com/airbytehq/airbyte/pull/18968) | Migrate to Low-Code |
| 0.1.0 | 2021-08-10 | [5366](https://github.com/airbytehq/airbyte/pull/5366) | Initial release of Close.com connector for Airbyte |

