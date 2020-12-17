---
description: Be sure to not miss out on new features and improvements!
---

# Changelog

This is the changelog for Airbyte core. For our connector changelog, please visit our [Connector Changelog](integrations/integrations-changelog.md) page.

If you're interested in our progress on the Airbyte platform, please read below!

## 0.8.0 - delivered on 12/17/2020

* **Incremental v1 named "Append"**
  * We now allow sources to replicate only new or modified data. This enables to avoid re-fetching data that you have already replicated from a source. 
  * The delta from a sync will be _appended_ to the existing data in the data warehouse.
  * Here are [all the details of this feature](architecture/incremental.md).
  * It has been released for 15 connectors, including Postgres, MySQL, Intercom, Zendesk, Stripe, Twilio, Marketo, Shopify, GitHub, and all the destination connectors. We will expand it to all the connectors in the next couple of weeks.
* **Other features:**
  * Improve interface for writing python sources \(should make writing new python sources easier and clearer\).
  * Add support for running Standard Source Tests with files \(making them easy to run for any language a source is written in\)
  * Add ability to reset data for a connection.
* **Bug fixes:**
  * Update version of test containers we use to avoid pull issues while running tests.
  * Fix issue where jobs were not sorted by created at in connection detail view.
* **New sources:** Intercom, Mixpanel, Jira Cloud, Zoom, Drift, Microsoft Teams

## 0.7.0 - delivered on 12/07/2020

* **New destination:** our own **Redshift** warehouse connector. You can also use this connector for Panoply.
* **New sources**: 8 additional source connectors including Recurly, Twilio, Freshdesk. Greenhouse, Redshift \(source\), Braintree, Slack, Zendesk Support
* Bug fixes

## 0.6.0 - delivered on 11/23/2020

* Support **multiple destinations** 
* **New source:** Sendgrid
* Support **basic normalization**
* Bug fixes

## 0.5.0 - delivered on 11/18/2020

* **New sources:** 10 additional source connectors, including Files \(CSV, HTML, JSON...\), Shopify, MSSQL, Mailchimp

## 0.4.0 - delivered on 11/04/2020

Here is what we are working on right now:

* **New destination**: our own **Snowflake** warehouse connector
* **New sources:** Facebook Ads, Google Ads.

## 0.3.0 - delivered on 10/30/2020

* **New sources:** Salesforce, GitHub, Google Sheets, Google Analytics, Hubspot, Rest APIs, and MySQL
* Integration test suite for sources
* Improve build speed

## 0.2.0 - delivered on 10/21/2020

* **a new Admin section** to enable users to add their own connectors, in addition to upgrading the ones they currently use 
* improve the developer experience \(DX\) for **contributing new connectors** with additional documentation and a connector protocol 
* our own **BigQuery** warehouse connector 
* our own **Postgres** warehouse connector 
* simplify the process of supporting new Singer taps, ideally make it a 1-day process

## 0.1.0 - delivered on 09/23/2020

This is our very first release after 2 months of work.

* **New sources:** Stripe, Postgres
* **New destinations:** BigQuery, Postgres
* **Only one destination**: we only support one destination in that 1st release, but you will soon be able to add as many as you need. 
* **Logs & monitoring**: you can now see your detailed logs
* **Scheduler:** you now have 10 different frequency options for your recurring syncs
* **Deployment:** you can now deploy Airbyte via a simple Docker image, or directly on AWS and GCP
* **New website**: this is the day we launch our website - airbyte.io. Let us know what you think
* **New documentation:** this is the 1st day for our documentation too
* **New blog:** we published a few articles on our startup journey, but also about our vision to making data integrations a commodity. 

Stay tuned, we will have new sources and destinations very soon! Don't hesitate to subscribe to our [newsletter](https://airbyte.io/#subscribe-newsletter) to receive our product updates and community news.

