# Close Com

## Overview

The Close Com source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

### Output schema

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

### Notes

Leads, Events Incremental streams use `date_updated` field. All other Incremental streams use `date_created` field.

### Data type mapping

The [Close Com API](https://developer.close.com/) uses the same [JSONSchema](https://json-schema.org/understanding-json-schema/reference/index.html) types that Airbyte uses internally \(`string`, `date-time`, `object`, `array`, `boolean`, `integer`, and `number`\), so no type conversions happen as part of this source.

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | Yes |

### Performance considerations

The Close Com Connector has rate limit. There are 60 RPS for Organizations.
You can find detailed info [here](https://developer.close.com/#ratelimits).

## Getting started

### Requirements

* Close Com Account
* Close Com API Key

### Setup guide

Visit the [Close Com API Keys page](https://app.close.com/settings/api/) in the Close Com dashboard to access the secret key for your account. Secret key will be prefixed with `api_`.

We recommend creating a restricted key specifically for Airbyte access. This will allow you to control which resources Airbyte should be able to access. For ease of use, we recommend using read permissions for all resources and configuring which resource to replicate in the Airbyte UI.

## Changelog

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.1.0   | 2021-08-10 | []() | Initial release of Close Com connector for Airbyte |
