---
description: Do not miss the new connectors we support!
---

# Connectors

**You can request new connectors directly** [**here**](https://github.com/airbytehq/airbyte/issues/new?assignees=&labels=area%2Fintegration%2C+new-integration&template=new-integration-request.md&title=)**.**

Note: Airbyte is not built on top of Singer, but is compatible with Singer's protocol. Airbyte's ambitions go beyond what Singer enables to do, so we are building our own protocol that will keep its compatibility with Singer's one.

## Currently under construction

Check out our [connector roadmap](https://github.com/airbytehq/airbyte/projects/3) to see what we're currently working on

## 06/3/2021

2 new sources:
* [**Okta**](https://docs.airbyte.io/integrations/sources/okta)
* [**Amazon Seller Partner**](https://docs.airbyte.io/integrations/sources/amazon-seller-partner)

New features:
* **MySQL CDC** now only polls for 5 minutes if we haven't received any records ([#3789](https://github.com/airbytehq/airbyte/pull/3789))
* **Python CDK** now supports Python 3.7.X ([#3692](https://github.com/airbytehq/airbyte/pull/3692))
* **File** source: now supports Azure Blob Storage ([#3660](https://github.com/airbytehq/airbyte/pull/3660))

Bugfixes:
* **Recurly** source: now uses type `number` instead of `integer` ([#3769](https://github.com/airbytehq/airbyte/pull/3769))
* **Stripe** source: fix types in schema ([#3744](https://github.com/airbytehq/airbyte/pull/3744))
* **Stripe** source: output `number` instead of `int` ([#3728](https://github.com/airbytehq/airbyte/pull/3728))
* **MSSQL** destination: fix issue with unicode symbols handling ([#3671](https://github.com/airbytehq/airbyte/pull/3671))

***

## 05/25/2021

4 new sources: 
* [**Asana**](https://docs.airbyte.io/integrations/sources/asana)
* [**Klaviyo**](https://docs.airbyte.io/integrations/sources/klaviyo)
* [**Recharge**](https://docs.airbyte.io/integrations/sources/recharge)
* [**Tempo**](https://docs.airbyte.io/integrations/sources/tempo)

Progress on connectors:
* **CDC for MySQL** is now available!
* **Sendgrid** source: support incremental sync, as rewritten using HTTP CDK ([#3445](https://github.com/airbytehq/airbyte/pull/3445)) 
* **Github** source bugfix: exception when parsing null date values, use `created_at` as cursor value for issue_milestones ([#3314](https://github.com/airbytehq/airbyte/pull/3314))
* **Slack** source bugfix: don't overwrite thread_ts in threads stream  ([#3483](https://github.com/airbytehq/airbyte/pull/3483))
* **Facebook Marketing** source: allow configuring insights lookback window ([#3396](https://github.com/airbytehq/airbyte/pull/3396))
* **Freshdesk** source: fix discovery ([#3591](https://github.com/airbytehq/airbyte/pull/3591))

## 05/18/2021

1 new destination: [**MSSQL**](https://docs.airbyte.io/integrations/destinations/mssql)

1 new source: [**ClickHouse**](https://docs.airbyte.io/integrations/sources/clickhouse)

Progress on connectors:
* **Shopify**: make this source more resilient to timeouts ([#3409](https://github.com/airbytehq/airbyte/pull/3409))
* **Freshdesk** bugfix: output correct schema for various streams ([#3376](https://github.com/airbytehq/airbyte/pull/3376))
* **Iterable**: update to use latest version of CDK ([#3378](https://github.com/airbytehq/airbyte/pull/3378))

## 05/11/2021

1 new destination: [**MySQL**](https://docs.airbyte.io/integrations/destinations/mysql)

2 new sources:
* [**Google Search Console**](https://docs.airbyte.io/integrations/sources/google-search-console)
* [**PokeAPI**](https://docs.airbyte.io/integrations/sources/pokeapi) \(talking about long tail and having fun ;\)\)

Progress on connectors:
* **Zoom**: bugfix on declaring correct types to match data coming from API \([\#3159](https://github.com/airbytehq/airbyte/pull/3159)\), thanks to [vovavovavovavova](https://github.com/vovavovavovavova) 
* **Smartsheets**: bugfix on gracefully handling empty cell values \([\#3337](https://github.com/airbytehq/airbyte/pull/3337)\), thanks to [Nathan Nowack](https://github.com/zzstoatzz)
* **Stripe**: fix date property name, only add connected account header when set, and set primary key \(\#3210\), thanks to [Nathan Yergler](https://github.com/nyergler)

## 05/04/2021

2 new sources:

* [**Smartsheets**](https://docs.airbyte.io/integrations/sources/smartsheets), thanks to [Nathan Nowack](https://github.com/zzstoatzz)
* [**Zendesk Chat**](https://docs.airbyte.io/integrations/sources/zendesk-chat)

Progress on connectors:

* **Appstore**: bugfix private key handling in the UI \([\#3201](https://github.com/airbytehq/airbyte/pull/3201)\)
* **Facebook marketing**: Wait longer \(5 min\) for async jobs to start \([\#3116](https://github.com/airbytehq/airbyte/pull/3116)\), thanks to [Max Krog](https://github.com/MaxKrog)
* **Stripe**: support reading data from connected accounts \(\#3121\), and 2 new streams with Refunds & Bank Accounts \([\#3030](https://github.com/airbytehq/airbyte/pull/3030)\) \([\#3086](https://github.com/airbytehq/airbyte/pull/3086)\)
* **Redshift destination**: Ignore records that are too big \(instead of failing\) \([\#2988](https://github.com/airbytehq/airbyte/pull/2988)\)
* **MongoDB**: add supporting TLS and Replica Sets \([\#3111](https://github.com/airbytehq/airbyte/pull/3111)\)
* **HTTP sources**: bugfix on handling array responses gracefully \([\#3008](https://github.com/airbytehq/airbyte/pull/3008)\)

## 04/27/2021

* **Zendesk Talk**: fix normalization failure \([\#3022](https://github.com/airbytehq/airbyte/pull/3022)\), thanks to [yevhenii-ldv](https://github.com/yevhenii-ldv)
* **Github**: pull\_requests stream only incremental syncs \([\#2886](https://github.com/airbytehq/airbyte/pull/2886)\) \([\#3009](https://github.com/airbytehq/airbyte/pull/3009)\), thanks to [Zirochkaa](https://github.com/Zirochkaa)
* Create streaming writes to a file and manage the issuance of copy commands for the destination \([\#2921](https://github.com/airbytehq/airbyte/pull/2921)\)
* **Redshift**: make Redshift part size configurable. \([\#3053](https://github.com/airbytehq/airbyte/pull/23053)\)
* **Hubspot**: fix argument error in log call \(\#3087\) \([\#3087](https://github.com/airbytehq/airbyte/pull/3087)\) , thanks to [Nathan Yergler](https://github.com/nyergler)

## 04/20/2021

3 new source connectors!

* [**Zendesk Talk**](https://docs.airbyte.io/integrations/sources/zendesk-talk)
* [**Iterable**](https://docs.airbyte.io/integrations/sources/iterable) 
* [**Quickbooks**](https://docs.airbyte.io/integrations/sources/quickbooks)

Other progress on connectors:

* **Postgres source/destination**: add SSL option, thanks to [Marcos Marx](https://github.com/marcosmarxm) \([\#2757](https://github.com/airbytehq/airbyte/pull/2757)\)
* **Google sheets bugfix**: handle duplicate sheet headers, thanks to [Aneesh Makala](https://github.com/makalaaneesh) \([\#2905](https://github.com/airbytehq/airbyte/pull/2905)\)
* **Source Google Adwords**: support specifying the lookback window for conversions, thanks to [Harshith Mullapudi](https://github.com/harshithmullapudi) \([\#2918](https://github.com/airbytehq/airbyte/pull/2918)\)
* **MongoDB improvement**: speed up mongodb schema discovery, thanks to [Yury Koleda](https://github.com/FUT) \([\#2851](https://github.com/airbytehq/airbyte/pull/2851)\)
* **MySQL bugfix**: parsing Mysql jdbc params, thanks to [Vasily Safronov](https://github.com/gingeard) \([\#2891](https://github.com/airbytehq/airbyte/pull/2891)\)
* **CSV bugfix**: discovery takes too much memory \([\#2089](https://github.com/airbytehq/airbyte/pull/2851)\)
* A lot of work was done on improving the standard tests for the connectors, for better standardization and maintenance!

## 04/13/2021

* New connector: [**Oracle DB**](https://docs.airbyte.io/integrations/sources/oracle), thanks to [Marcos Marx](https://github.com/marcosmarxm) 

## 04/07/2021

* New connector: [**Google Workspace Admin Reports**](https://docs.airbyte.io/integrations/sources/google-workspace-admin-reports) \(audit logs\)
* Bugfix in the base python connector library that caused errors to be silently skipped rather than failing the sync
* **Exchangeratesapi.io** bugfix: to point to the updated API URL
* **Redshift destination** bugfix: quote keywords “DATETIME” and “TIME” when used as identifiers
* **GitHub** bugfix: syncs failing when a personal repository doesn’t contain collaborators or team streams available
* **Mixpanel** connector: sync at most the last 90 days of data in the annotations stream to adhere to API limits

## 03/29/2021

* We started measuring throughput of connectors. This will help us improve that point for all connectors. 
* **Redshift**: implemented Copy strategy to improve its throughput. 
* **Instagram**: bugfix an issue which caused media and media\_insights streams to stop syncing prematurely.
* Support NCHAR and NVCHAR types in SQL-based database sources.
* Add the ability to specify a custom JDBC parameters for the MySQL source connector.

## 03/22/2021

* 2 new source connectors: [**Gitlab**](https://docs.airbyte.io/integrations/sources/gitlab) and [**Airbyte-native Hubspot**](https://docs.airbyte.io/integrations/sources/hubspot)
* Developing connectors now requires almost no interaction with Gradle, Airbyte’s  monorepo build tool. If you’re building a Python connector, you never have to worry about developing outside your typical flow. See [the updated documentation](https://docs.airbyte.io/contributing-to-airbyte/building-new-connector). 

## 03/15/2021

* 2 new source connectors: [**Instagram**](https://docs.airbyte.io/integrations/sources/instagram) and [**Google Directory**](https://docs.airbyte.io/integrations/sources/google-directory)
* **Facebook Marketing**: support of API v10
* **Google Analytics**: support incremental sync
* **Jira**: bug fix to consistently pull all tickets
* **HTTP Source**: bug fix to correctly parse JSON responses consistently

## 03/08/2021

* 1 new source connector: [**MongoDB**](https://docs.airbyte.io/integrations/sources/mongodb)
* **Google Analytics**: Support chunked syncs to avoid sampling
* **AppStore**: fix bug where the catalog was displayed incorrectly

## 03/01/2021

* **New native Hubspot connector** with schema folder populated
* Facebook Marketing connector: add option to include deleted records

## 02/22/2021

* Bug fixes:
  * **Google Analytics:** add the ability to sync custom reports
  * **Apple Appstore:** bug fix to correctly run incremental syncs
  * **Exchange rates:** UI now correctly validates input date pattern
  * **File Source:** Support JSONL \(newline-delimited JSON\) format
  * **Freshdesk:** Enable controlling how many requests per minute the connector makes to avoid overclocking rate limits

## 02/15/2021

* 1 new destination connector: [MeiliSearch](https://docs.airbyte.io/integrations/destinations/meilisearch)
* 2 new sources that support incremental append: [Freshdesk](https://docs.airbyte.io/integrations/sources/freshdesk) and [Sendgrid](https://docs.airbyte.io/integrations/sources/sendgrid)
* Other fixes:
  * Thanks to [@ns-admetrics](https://github.com/ns-admetrics) for contributing an upgrade to the **Shopify** source connector which now provides the landing\_site field containing UTM parameters in the Orders table.
  * **Sendgrid** source connector supports most available endpoints available in the API
  * **Facebook** Source connector now supports syncing Ad Insights data 
  * **Freshdesk** source connector now supports syncing satisfaction ratings and conversations
  * **Microsoft Teams** source connector now gracefully handles rate limiting 
  * Bug fix in **Slack** source where the last few records in a sync were sporadically dropped 
  * Bug fix in **Google Analytics** source where the last few records in sync were sporadically dropped
  * In **Redshift source**, support non alpha-numeric table names 
  * Bug fix in **Github Source** to fix instances where syncs didn’t always fail if there was an error while reading data from the API 

## 02/02/2021

* Sources that we improved reliability for \(and that became “certified”\):
  * [Certified sources](https://docs.airbyte.io/integrations/connector-health): Files and Shopify
  * Enhanced continuous testing for Tempo and Looker sources
* Other fixes / features:
  * Correctly handle boolean types in the File Source
  * Add docs for [App Store](https://docs.airbyte.io/integrations/sources/appstore) source 
  * Fix a bug in Snowflake destination where the connector didn’t check for all needed write permissions, causing some syncs to fail

## 01/26/2021

* Improved reliability with our best practices on : Google Sheets, Google Ads, Marketo, Tempo
* Support incremental for Facebook and Google Ads
* The Facebook connector now supports the FB marketing API v9

## 01/19/2021

* **Our new** [**Connector Health Status**](../../integrations/connector-health.md) **page**
* **1 new source:** App Store \(thanks to [@Muriloo](https://github.com/Muriloo)\)
* Fixes on connectors:
  * Bug fix writing boolean columns to Redshift
  * Bug fix where getting a connector’s input configuration hung indefinitely 
  * Stripe connector now gracefully handles rate limiting from the Stripe API

## 01/12/2021

* **1 new source:** Tempo \(thanks to [@thomasvl](https://github.com/thomasvl)\)
* **Incremental support for 3 new source connectors:** [Salesforce](../../integrations/sources/salesforce.md), [Slack](../../integrations/sources/slack.md) and [Braintree](../../integrations/sources/braintree.md)
* Fixes on connectors:
  * Fix a bug in MSSQL and Redshift source connectors where custom SQL types weren't being handled correctly.
  * Improvement of the Snowflake connector from [@hudsondba](https://github.com/hudsondba) \(batch size and timeout sync\)

## 01/05/2021

* **Incremental support for 2 new source connectors:** [Mixpanel](../../integrations/sources/mixpanel.md) and [Hubspot](../../integrations/sources/hubspot.md)
* Fixes on connectors:
  * Fixed a bug in the github connector where the connector didn’t verify the provided API token was granted the correct permissions
  * Fixed a bug in the Google sheets connector where rate limits were not always respected
  * Alpha version of Facebook marketing API v9. This connector is a native Airbyte connector \(current is Singer based\).

## 12/30/2020

**New sources:** [Plaid](../../integrations/sources/plaid.md) \(contributed by [tgiardina](https://github.com/tgiardina)\), [Looker](../../integrations/sources/looker.md)

## 12/18/2020

**New sources:** [Drift](../../integrations/sources/drift.md), [Microsoft Teams](../../integrations/sources/microsoft-teams.md)

## 12/10/2020

**New sources:** [Intercom](../../integrations/sources/intercom.md), [Mixpanel](../../integrations/sources/mixpanel.md), [Jira Cloud](../../integrations/sources/jira.md), [Zoom](../../integrations/sources/zoom.md)

## 12/07/2020

**New sources:** [Slack](../../integrations/sources/slack.md), [Braintree](../../integrations/sources/braintree.md), [Zendesk Support](../../integrations/sources/zendesk-support.md)

## 12/04/2020

**New sources:** [Redshift](../../integrations/sources/redshift.md), [Greenhouse](../../integrations/sources/greenhouse.md)  
**New destination:** [Redshift](../../integrations/destinations/redshift.md)

## 11/30/2020

**New sources:** [Freshdesk](../../integrations/sources/freshdesk.md), [Twilio](../../integrations/sources/twilio.md)

## 11/25/2020

**New source:** [Recurly](../../integrations/sources/recurly.md)

## 11/23/2020

**New source:** [Sendgrid](../../integrations/sources/sendgrid.md)

## 11/18/2020

**New source:** [Mailchimp](../../integrations/sources/mailchimp.md)

## 11/13/2020

**New source:** [MSSQL](../../integrations/sources/mssql.md)

## 11/11/2020

**New source:** [Shopify](../../integrations/sources/shopify.md)

## 11/09/2020

**New sources:** [Files \(CSV, JSON, HTML...\)](../../integrations/sources/file.md)

## 11/04/2020

**New sources:** [Facebook Ads](connectors.md), [Google Ads](../../integrations/sources/google-adwords.md), [Marketo](../../integrations/sources/marketo.md)  
**New destination:** [Snowflake](../../integrations/destinations/snowflake.md)

## 10/30/2020

**New sources:** [Salesforce](../../integrations/sources/salesforce.md), [Google Analytics](../../integrations/sources/googleanalytics.md), [Hubspot](../../integrations/sources/hubspot.md), [GitHub](../../integrations/sources/github.md), [Google Sheets](../../integrations/sources/google-sheets.md), [Rest APIs](connectors.md), and [MySQL](../../integrations/sources/mysql.md)

## 10/21/2020

**New destinations:** we built our own connectors for [BigQuery](../../integrations/destinations/bigquery.md) and [Postgres](../../integrations/destinations/postgres.md), to ensure they are of the highest quality.

## 09/23/2020

**New sources:** [Stripe](../../integrations/sources/stripe.md), [Postgres](../../integrations/sources/postgres.md)  
**New destinations:** [BigQuery](../../integrations/destinations/bigquery.md), [Postgres](../../integrations/destinations/postgres.md), [local CSV](../../integrations/destinations/local-csv.md)

