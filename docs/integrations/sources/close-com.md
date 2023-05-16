# Close.com

## Prerequisites

* **Close.com Account:** To set up the Close.com connector, you need an active Close.com account.
* **Close.com API Key:** You need to obtain your Close.com API key to configure the Close.com connector. If you don't have an API key, you can easily create one in your account. You can manage your API keys by visiting the [Close.com API Keys](https://app.close.com/settings/api/) page in your Close.com dashboard. 

## Getting Your Close.com API Key

To obtain your Close.com API key, follow these steps:

1. **Log in to your Close.com account**
   
   You can log in to your account by visiting the [Close.com](https://app.close.com/) website and entering your login credentials.

2. **Navigate to the API keys section**
   
   Once you are logged in, navigate to the Close.com API Keys section by clicking on the "Settings" option in the left sidebar and selecting "API Keys" from the dropdown list. 

3. **Create a new API key**
   
   To create a new API key, click on the "New API Key" button on the top right corner of the page. 

4. **Configure your API key**
   
   In the configuration section, you need to give your API key a name and select the desired permissions. We recommend creating a restricted key specifically for Airbyte access. This will allow you to control which resources Airbyte should be able to access. For ease of use, we recommend using read permissions for all resources and configuring which resource to replicate in the Airbyte UI. 

   Once you have configured your API key, click on the "Create API Key" button to generate your key. Your new API key will be displayed on the screen and will be prefixed with 'api_'.

5. **Copy your API key**

   To use your API key in the Close.com connector in Airbyte, you need to copy it to the clipboard. 

   **Note:** Be sure to store your API key in a secure location.

## Set Up Guide

To set up the Close.com connector in Airbyte, follow these steps:

1. **Log in to your Airbyte Cloud account**
   
   You can log in to your Airbyte Cloud account by visiting the [Airbyte Cloud website](https://cloud.airbyte.com/workspaces) and entering your login credentials.

2. **Create a new source**
   
   In the left navigation bar, click on "Sources". In the top-right corner of the page, click on the "+New Source" button.

3. **Configure your source**
   
   In the "Set up the source" page, select "Close.com" from the "Source type" dropdown. Enter the name for the Close.com connector and fill in the "API key" and "Start date" fields. 

   **Note:** The "API key" field requires the API key obtained from your Close.com account following the steps mentioned above.

   The "Start date" field is used to specify the date from when you want to replicate data. If you want to do a full sync from the beginning of time, leave this field blank. Otherwise, specify the date from which you want to start syncing data. The format for this field is "YYYY-MM-DD".

4. **Set up your source**
   
   Click on the "Set up source" button to create the Close.com connector in Airbyte.

## Connector Configuration

The Close.com connector in Airbyte uses the following configuration:

```
{
  "api_key": {
    "airbyte_secret": true,
    "description": "Close.com API key (usually starts with 'api_'; find yours here: https://app.close.com/settings/api/)",
    "type": "string"
  },
  "start_date": {
    "default": "2021-01-01",
    "description": "The start date to sync data. Leave blank for full sync. Format: YYYY-MM-DD.",
    "examples": ["2021-01-01"],
    "format": "date-time",
    "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$",
    "type": "string"
  }
}
```

### Supported Streams

The Close.com connector in Airbyte supports the following core Streams:

* Leads (Incremental)
* Created Activities (Incremental)
* Opportunity Status Change Activities (Incremental)
* Note Activities (Incremental)
* Meeting Activities (Incremental)
* Call Activities (Incremental)
* Email Activities (Incremental)
* Email Thread Activities (Incremental)
* Lead Status Change Activities (Incremental)
* SMS Activities (Incremental)
* Task Completed Activities (Incremental)
* Lead Tasks (Incremental)
* Incoming Email Tasks (Incremental)
* Email Followup Tasks (Incremental)
* Missed Call Tasks (Incremental)
* Answered Detached Call Tasks (Incremental)
* Voicemail Tasks (Incremental)
* Opportunity Due Tasks (Incremental)
* Incoming SMS Tasks (Incremental)
* Events (Incremental)
* Lead Custom Fields
* Contact Custom Fields
* Opportunity Custom Fields
* Activity Custom Fields
* Users
* Contacts
* Opportunities (Incremental)
* Roles
* Lead Statuses
* Opportunity Statuses
* Pipelines
* Email Templates
* Google Connected Accounts
* Custom Email Connected Accounts
* Zoom Connected Accounts
* Send As
* Email Sequences
* Dialer
* Smart Views
* Email Bulk Actions
* Sequence Subscription Bulk Actions
* Delete Bulk Actions
* Edit Bulk Actions
* Integration Links
* Custom Activities

### Supported Sync Modes

The Close.com connector in Airbyte supports both Full Refresh and Incremental sync modes. You can choose whether to sync only new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

### Data Type Mapping

The Close.com API uses the same JSONSchema types that Airbyte uses internally (string, date-time, object, array, boolean, integer, and number), so no type conversions will occur as part of this source.

### Performance Considerations

The Close.com connector in Airbyte has a rate limit. Organizations have a limit of 60 RPS. Additional information on this can be found [here](https://developer.close.com/#ratelimits).

## Changelog

| Version | Date       | Pull Request                                     | Subject                                                 |
| :------ | :--------- | :----------------------------------------------- | :------------------------------------------------------ |
| 0.2.1   | 2023-02-15 | [23074](https://github.com/airbytehq/airbyte/pull/23074) | Specified date formatting in specification |
| 0.2.0   | 2022-11-04 | [18968](https://github.com/airbytehq/airbyte/pull/18968) | Migrated to Low-Code |
| 0.1.0   | 2021-08-10 | [5366](https://github.com/airbytehq/airbyte/pull/5366)  | Initial release of Close.com connector for Airbyte | 

---

This document is meant to provide clarifications and guidance on setting up the Close.com connector on the Airbyte platform. If you face any technical or operational issues while setting up this connector, please refer to the [Close.com documentation](https://developer.close.com/) or contact Close.com customer support for further assistance.