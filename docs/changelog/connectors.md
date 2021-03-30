---
description: Do not miss the new connectors we support!
---

# Connectors

**You can request new connectors directly** [**here**](https://github.com/airbytehq/airbyte/issues/new?assignees=&labels=area%2Fintegration%2C+new-integration&template=new-integration-request.md&title=)**.**

Note: Airbyte is not built on top of Singer, but is compatible with Singer's protocol. Airbyte's ambitions go beyond what Singer enables to do, so we are building our own protocol that will keep its compatibility with Singer's one.

## Currently under construction

Check out our [connector roadmap](https://github.com/airbytehq/airbyte/projects/3) to see what we're currently working on

## 03/29/2021

* We started measuring throughput of connectors. This will help us improve that point for all connectors. 
* **Redshift**: implemented Copy strategy to improve its throughput. 
* **Instagram**: bugfix an issue which caused media and media_insights streams to stop syncing prematurely.
* Support NCHAR and NVCHAR types in SQL-based database sources.
* Add the ability to specify a custom JDBC parameters for the MySQL source connector.

## 03/22/2021

* 2 new source connectors: **[Gitlab](https://docs.airbyte.io/integrations/sources/gitlab)** and **[Airbyte-native Hubspot](https://docs.airbyte.io/integrations/sources/hubspot)**
* Developing connectors now requires almost no interaction with Gradle, Airbyte’s  monorepo build tool. If you’re building a Python connector, you never have to worry about developing outside your typical flow. See [the updated documentation](https://docs.airbyte.io/contributing-to-airbyte/building-new-connector). 

## 03/15/2021

* 2 new source connectors: **[Instagram](https://docs.airbyte.io/integrations/sources/instagram)** and **[Google Directory](https://docs.airbyte.io/integrations/sources/google-directory)**
* **Facebook Marketing**: support of API v10
* **Google Analytics**: support incremental sync
* **Jira**: bug fix to consistently pull all tickets
* **HTTP Source**: bug fix to correctly parse JSON responses consistently

## 03/08/2021

* 1 new source connector: **[MongoDB](https://docs.airbyte.io/integrations/sources/mongodb)**
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

* **Our new** [**Connector Health Status**](../integrations/connector-health.md) **page**
* **1 new source:** App Store \(thanks to [@Muriloo](https://github.com/Muriloo)\)
* Fixes on connectors:
  * Bug fix writing boolean columns to Redshift
  * Bug fix where getting a connector’s input configuration hung indefinitely 
  * Stripe connector now gracefully handles rate limiting from the Stripe API

## 01/12/2021

* **1 new source:** Tempo \(thanks to [@thomasvl](https://github.com/thomasvl)\)
* **Incremental support for 3 new source connectors:** [Salesforce](../integrations/sources/salesforce.md), [Slack](../integrations/sources/slack.md) and [Braintree](../integrations/sources/braintree.md)
* Fixes on connectors:
  * Fix a bug in MSSQL and Redshift source connectors where custom SQL types weren't being handled correctly.
  * Improvement of the Snowflake connector from [@hudsondba](https://github.com/hudsondba) \(batch size and timeout sync\)

## 01/05/2021

* **Incremental support for 2 new source connectors:** [Mixpanel](../integrations/sources/mixpanel.md) and [Hubspot](../integrations/sources/hubspot.md)
* Fixes on connectors:
  * Fixed a bug in the github connector where the connector didn’t verify the provided API token was granted the correct permissions
  * Fixed a bug in the Google sheets connector where rate limits were not always respected
  * Alpha version of Facebook marketing API v9. This connector is a native Airbyte connector \(current is Singer based\).

## 12/30/2020

**New sources:** [Plaid](../integrations/sources/plaid.md) \(contributed by [tgiardina](https://github.com/tgiardina)\), [Looker](../integrations/sources/looker.md)

## 12/18/2020

**New sources:** [Drift](../integrations/sources/drift.md), [Microsoft Teams](../integrations/sources/microsoft-teams.md)

## 12/10/2020

**New sources:** [Intercom](../integrations/sources/intercom.md), [Mixpanel](../integrations/sources/mixpanel.md), [Jira Cloud](../integrations/sources/jira.md), [Zoom](../integrations/sources/zoom.md)

## 12/07/2020

**New sources:** [Slack](../integrations/sources/slack.md), [Braintree](../integrations/sources/braintree.md), [Zendesk Support](../integrations/sources/zendesk-support.md)

## 12/04/2020

**New sources:** [Redshift](../integrations/sources/redshift.md), [Greenhouse](../integrations/sources/greenhouse.md)  
**New destination:** [Redshift](../integrations/destinations/redshift.md)

## 11/30/2020

**New sources:** [Freshdesk](../integrations/sources/freshdesk.md), [Twilio](../integrations/sources/twilio.md)

## 11/25/2020

**New source:** [Recurly](../integrations/sources/recurly.md)

## 11/23/2020

**New source:** [Sendgrid](../integrations/sources/sendgrid.md)

## 11/18/2020

**New source:** [Mailchimp](../integrations/sources/mailchimp.md)

## 11/13/2020

**New source:** [MSSQL](../integrations/sources/mssql.md)

## 11/11/2020

**New source:** [Shopify](../integrations/sources/shopify.md)

## 11/09/2020

**New sources:** [Files \(CSV, JSON, HTML...\)](../integrations/sources/file.md)

## 11/04/2020

**New sources:** [Facebook Ads](connectors.md), [Google Ads](../integrations/sources/google-adwords.md), [Marketo](../integrations/sources/marketo.md)  
**New destination:** [Snowflake](../integrations/destinations/snowflake.md)

## 10/30/2020

**New sources:** [Salesforce](../integrations/sources/salesforce.md), [Google Analytics](../integrations/sources/googleanalytics.md), [Hubspot](../integrations/sources/hubspot.md), [GitHub](../integrations/sources/github.md), [Google Sheets](../integrations/sources/google-sheets.md), [Rest APIs](connectors.md), and [MySQL](../integrations/sources/mysql.md)

## 10/21/2020

**New destinations:** we built our own connectors for [BigQuery](../integrations/destinations/bigquery.md) and [Postgres](../integrations/destinations/postgres.md), to ensure they are of the highest quality.

## 09/23/2020

**New sources:** [Stripe](../integrations/sources/stripe.md), [Postgres](../integrations/sources/postgres.md)  
**New destinations:** [BigQuery](../integrations/destinations/bigquery.md), [Postgres](../integrations/destinations/postgres.md), [local CSV](../integrations/destinations/local-csv.md)

