# Google Adwords

## Overview

The Adwords source supports Full Refresh syncs. That is, every time a sync is run, Airbyte will copy all rows in the tables and columns you set up for replication into the destination in a new table.

This Adwords source wraps the [Singer Adwords Tap](https://github.com/singer-io/tap-adwords).

### Output schema

Several output streams are available from this source \(accounts, campaigns, ads, etc.\) For a comprehensive output schema [look at the Singer tap schema files](https://github.com/singer-io/tap-adwords/tree/master/tap_adwords/schemas).

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | Coming soon |
| Replicate Incremental Deletes | Coming soon |
| SSL connection | Yes |

### Performance considerations

This source is constrained by whatever API limits are set for the Google Adwords Manager that is used. You can read more about those limits in the [google developer docs](https://developers.google.com/adwords/api/faq#access).

## Getting started

### Requirements

* Google Adwords Manager Account with an approved Developer Token \(note: In order to get API access to Google Adwords, you must have a "manager" account. This must be created separately from your standard account. You can find more information about this distinction in the [google ads docs](https://ads.google.com/home/tools/manager-accounts/).\)

### Setup guide

This guide will provide information as if starting from scratch. Please skip over any steps you have already completed.

* Create an Adwords Account. Here are [Google's instruction](https://support.google.com/google-ads/answer/6366720) on how to create one.
* Create an Adwords MANAGER Account. Here are [Google's instruction](https://ads.google.com/home/tools/manager-accounts/) on how to create one.
* You should now have two Google Ads accounts: a normal account and a manager account. Link the Manager account to the normal account following [Google's documentation](https://support.google.com/google-ads/answer/7459601).
* Apply for a developer token on your Manager account. This token allows you to access your data from the Google Ads API. Here are [Google's instructions](https://developers.google.com/google-ads/api/docs/first-call/dev-token). The docs are a little unclear on this point, but you will _not_ be able to access your data via the Google Ads API until this token is approved. You cannot use a test developer token, it has to be at least a basic developer token. It usually takes Google 24 hours to respond to these applications.
  * Do not mention Airbyte in your application. Google currently mistakes Airbyte for a 3rd-party tool and will decline your request. See [issue 1981](https://github.com/airbytehq/airbyte/issues/1981) for more information.
  * This is the value you will use in the `developer_token` field.
* Fetch your `client_id`, `client_secret`, and `refresh_token`. Google provides [instructions](https://developers.google.com/adwords/api/docs/guides/first-api-call#set_up_oauth2_authentication) on how to do this.
* Select your `customer_ids`. The `customer_ids` refer to the id of each of your Google Ads accounts. This is the 10 digit number in the top corner of the page when you are in google ads ui. The source will only pull data from the accounts for which you provide an id. If you are having trouble finding it, check out [Google's instructions](https://support.google.com/google-ads/answer/1704344).

Wow! That was a lot of steps. We are working on making the OAuth flow for all of our connectors simpler \(allowing you to skip needing to get a `developer_token` and a `refresh_token` which are the most painful / time-consuming steps in this walkthrough\).
