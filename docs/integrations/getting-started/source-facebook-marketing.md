# Getting Started: Source Facebook Marketing

## Requirements

Google Ads Account with an approved Developer Token \(note: In order to get API access to Google Ads, you must have a "manager" account. This must be created separately from your standard account. You can find more information about this distinction in the [google ads docs](https://ads.google.com/home/tools/manager-accounts/).\)

* developer_token
* client_id
* client_secret
* refresh_token
* start_date
* customer_id

## Setup guide

This guide will provide information as if starting from scratch. Please skip over any steps you have already completed.

* Create an Google Ads Account. Here are [Google's instruction](https://support.google.com/google-ads/answer/6366720) on how to create one.
* Create an Google Ads MANAGER Account. Here are [Google's instruction](https://ads.google.com/home/tools/manager-accounts/) on how to create one.
* You should now have two Google Ads accounts: a normal account and a manager account. Link the Manager account to the normal account following [Google's documentation](https://support.google.com/google-ads/answer/7459601).
* Apply for a developer token \(**make sure you follow our** [**instructions**](#how-to-apply-for-the-developer-token)\) on your Manager account.  This token allows you to access your data from the Google Ads API. Here are [Google's instructions](https://developers.google.com/google-ads/api/docs/first-call/dev-token). The docs are a little unclear on this point, but you will _not_ be able to access your data via the Google Ads API until this token is approved. You cannot use a test developer token, it has to be at least a basic developer token. It usually takes Google 24 hours to respond to these applications. This developer token is the value you will use in the `developer_token` field.
* Fetch your `client_id`, `client_secret`, and `refresh_token`. Google provides [instructions](https://developers.google.com/google-ads/api/docs/first-call/overview) on how to do this.
* Select your `customer_id`. The `customer_is` refer to the id of each of your Google Ads accounts. This is the 10 digit number in the top corner of the page when you are in google ads ui. The source will only pull data from the accounts for which you provide an id. If you are having trouble finding it, check out [Google's instructions](https://support.google.com/google-ads/answer/1704344).

Wow! That was a lot of steps. We are working on making the OAuth flow for all of our connectors simpler \(allowing you to skip needing to get a `developer_token` and a `refresh_token` which are the most painful / time-consuming steps in this walkthrough\).

## How to apply for the developer token

Google is very picky about which software and which use case can get access to a developer token. The Airbyte team has worked with the Google Ads team to whitelist Airbyte and make sure you can get one \(see [issue 1981](https://github.com/airbytehq/airbyte/issues/1981) for more information\).

When you apply for a token, you need to mention:

* Why you need the token \(eg: want to run some internal analytics...\)
* That you will be using the Airbyte Open Source project
* That you have full access to the code base \(because we're open source\)
* That you have full access to the server running the code \(because you're self-hosting Airbyte\)

If for any reason the request gets denied, let us know and we will be able to unblock you.

## Understanding Google Ads Query Language

The Google Ads Query Language can query the Google Ads API. Check out [Google Ads Query Language](https://developers.google.com/google-ads/api/docs/query/overview)
