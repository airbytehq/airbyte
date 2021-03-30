---
description: Be sure to not miss out on new features and improvements!
---

# Platform

This is the changelog for Airbyte core. For our connector changelog, please visit our [Connector Changelog](connectors.md) page.

If you're interested in our progress on the Airbyte platform, please read below!

* We now handle nested tables with the normalization steps. Check out the video below to see how it works. 

## [03-29-2021 - 0.18.1](https://github.com/airbytehq/airbyte/releases/tag/v0.18.1-alpha)

* Surface the health of each connection so that a user can spot any problems at a glance. 
* Added support for deduplicating records in the destination using a primary key using incremental dedupe -  
* A source’s extraction mode (incremental, full refresh) is now decoupled from the destination’s write mode -- so you can repeatedly append full refreshes to get repeated snapshots of data in your source.
* New “Upgrade all” button in Admin to upgrade all your connectors at once 
* New “Cancel job” button in Connections Status page when a sync job is running, so you can stop never-ending processes.

## [03-22-2021 - 0.17.2](https://github.com/airbytehq/airbyte/releases/tag/v0.17.2-alpha)

* Improved the speed of get spec, check connection, and discover schema by migrating to the Temporal workflow engine.
* Exposed cancellation for sync jobs in the API (will be exposed in the UI in the next week!).
* Bug fix: Fix issue where migration app was OOMing.

## [03-15-2021 - 0.17.1](https://github.com/airbytehq/airbyte/releases/tag/v0.17.1-alpha)

* **Creating and deleting multiple workspaces** is now supported via the API. Thanks to [@Samuel Gordalina](https://github.com/gordalina) for contributing this feature!
* Normalization now supports numeric types with precision greater than 32 bits
* Normalization now supports union data types
* Support longform text inputs in the UI for cases where you need to preserve formatting on connector inputs like .pem keys
* Expose the latest available connector versions in the API
* Airflow: published a new [tutorial](https://docs.airbyte.io/tutorials/using-the-airflow-airbyte-operator) for how to use the Airbyte operator. Thanks [@Marcos Marx](https://github.com/marcosmarxm) for writing the tutorial! 
* Connector Contributions: All connectors now describe how to contribute to them without having to touch Airbyte’s monorepo build system -- just work on the connector in your favorite dev setup!


## [03-08-2021 - 0.17](https://github.com/airbytehq/airbyte/releases/tag/v0.17.0-alpha)

* Integration with Airflow is here. Thanks to @Marcos Marx, you can now run Airbyte jobs from Airflow directly. A tutorial is on the way and should be coming this week!
* Add a prefix for tables, so that tables with the same name don't clobber each other in the destination


## [03-01-2021 - 0.16](https://github.com/airbytehq/airbyte/milestone/22?closed=1)

* We made some progress to address **nested tables in our normalization.**

  Previously, basic normalization would output nested tables as-is and append a number for duplicate tables. For example, Stripe’s nested address fields go from:

  ```text
  Address
  address_1
  ```

  To

  ```text
  Charges_source_owner_755_address
  customers_shipping_c70_address
  ```

  After the change, the parent tables are combined with the name of the nested table to show where the nested table originated. **This is a breaking change for the consumers of nested tables. Consumers will need to update to point at the new tables.**

## [02-19-2021 - 0.15](https://github.com/airbytehq/airbyte/milestone/22?closed=1)

* We now handle nested tables with the normalization steps. Check out the video below to see how it works. 

{% embed url="https://youtu.be/I4fngMnkJzY" caption="" %}

## [02-12-2021 - 0.14](https://github.com/airbytehq/airbyte/milestone/21?closed=1)

* Front-end changes:
  * Display Airbyte's version number
  * Describe schemas using JsonSchema
  * Better feedback on buttons

## [Beta launch - 0.13](https://github.com/airbytehq/airbyte/milestone/15?closed=1) - Released 02/02/2021

* Add connector build status dashboard
* Support Schema Changes in Sources
* Support Import / Export of Airbyte Data in the Admin section of the UI
* Bug fixes:
  * If Airbyte is closed during a sync the running job is not marked as failed
  * Airbyte should fail when instance version doesn't match data version
  * Upgrade Airbyte Version without losing existing configuration / data

## [0.12-alpha](https://github.com/airbytehq/airbyte/milestone/14?closed=1) - Released 01/20/2021

* Ability to skip onboarding
* Miscellaneous bug fixes:
  * A long discovery request causes a timeout in the UI type/bug
  * Out of Memory when replicating large table from MySQL

## 0.11.2-alpha - Released 01/18/2021

* Increase timeout for long running catalog discovery operations from 3 minutes to 30 minutes to avoid prematurely failing long-running operations 

## 0.11.1-alpha - Released 01/17/2021

### Bugfixes

* Writing boolean columns to Redshift destination now works correctly 

## [0.11.0-alpha](https://github.com/airbytehq/airbyte/milestone/12?closed=1) - Delivered 01/14/2021

### New features

* Allow skipping the onboarding flow in the UI
* Add the ability to reset a connection's schema when the underlying data source schema changes

### Bugfixes

* Fix UI race condition which showed config for the wrong connector when rapidly choosing between different connector 
* Fix a bug in MSSQL and Redshift source connectors where custom SQL types weren't being handled correctly. [Pull request](https://github.com/airbytehq/airbyte/pull/1576)
* Support incremental sync for Salesforce, Slack, and Braintree sources
* Gracefully handle invalid nuemric values \(e.g NaN or Infinity\) in MySQL, MSSQL, and Postgtres DB sources
* Fix flashing red sources/destinations fields after success submit
* Fix a bug which caused getting a connector's specification to hang indefinitely if the connector docker image failed to download

### New connectors

* Tempo
* Appstore

## [0.10.0](https://github.com/airbytehq/airbyte/milestone/12?closed=1) - delivered on 01/04/2021

* You can now **deploy Airbyte on** [**Kuberbetes**](https://docs.airbyte.io/deploying-airbyte/on-kubernetes) _\*\*_\(alpha version\)
* **Support incremental sync** for Mixpanel and Hubspot sources
* **Fixes on connectors:**
  * Fixed a bug in the GitHub connector where the connector didn’t verify the provided API token was granted the correct permissions
  * Fixed a bug in the Google Sheets connector where rate limits were not always respected
  * Alpha version of Facebook marketing API v9. This connector is a native Airbyte connector \(current is Singer based\).
* **New source:** Plaid \(contributed by [@tgiardina](https://github.com/tgiardina) - thanks Thomas!\)

## [0.9.0](https://github.com/airbytehq/airbyte/milestone/11?closed=1) - delivered on 12/23/2020

* **New chat app from the web app** so you can directly chat with the team for any issues you run into
* **Debugging** has been made easier in the UI, with checks, discover logs, and sync download logs
* Support of **Kubernetes in local**. GKE will come at the next release.
* **New source:** Looker _\*\*_

## [0.8.0](https://github.com/airbytehq/airbyte/milestone/10?closed=1) - delivered on 12/17/2020

* **Incremental - Append"**
  * We now allow sources to replicate only new or modified data. This enables to avoid re-fetching data that you have already replicated from a source.
  * The delta from a sync will be _appended_ to the existing data in the data warehouse.
  * Here are [all the details of this feature](../architecture/incremental-append.md).
  * It has been released for 15 connectors, including Postgres, MySQL, Intercom, Zendesk, Stripe, Twilio, Marketo, Shopify, GitHub, and all the destination connectors. We will expand it to all the connectors in the next couple of weeks.
* **Other features:**
  * Improve interface for writing python sources \(should make writing new python sources easier and clearer\).
  * Add support for running Standard Source Tests with files \(making them easy to run for any language a source is written in\)
  * Add ability to reset data for a connection.
* **Bug fixes:**
  * Update version of test containers we use to avoid pull issues while running tests.
  * Fix issue where jobs were not sorted by created at in connection detail view.
* **New sources:** Intercom, Mixpanel, Jira Cloud, Zoom, Drift, Microsoft Teams

## [0.7.0](https://github.com/airbytehq/airbyte/milestone/8?closed=1) - delivered on 12/07/2020

* **New destination:** our own **Redshift** warehouse connector. You can also use this connector for Panoply.
* **New sources**: 8 additional source connectors including Recurly, Twilio, Freshdesk. Greenhouse, Redshift \(source\), Braintree, Slack, Zendesk Support
* Bug fixes

## [0.6.0](https://github.com/airbytehq/airbyte/milestone/6?closed=1) - delivered on 11/23/2020

* Support **multiple destinations**
* **New source:** Sendgrid
* Support **basic normalization**
* Bug fixes

## [0.5.0](https://github.com/airbytehq/airbyte/milestone/5?closed=1) - delivered on 11/18/2020

* **New sources:** 10 additional source connectors, including Files \(CSV, HTML, JSON...\), Shopify, MSSQL, Mailchimp

## [0.4.0](https://github.com/airbytehq/airbyte/milestone/4?closed=1) - delivered on 11/04/2020

Here is what we are working on right now:

* **New destination**: our own **Snowflake** warehouse connector
* **New sources:** Facebook Ads, Google Ads.

## [0.3.0](https://github.com/airbytehq/airbyte/milestone/3?closed=1) - delivered on 10/30/2020

* **New sources:** Salesforce, GitHub, Google Sheets, Google Analytics, Hubspot, Rest APIs, and MySQL
* Integration test suite for sources
* Improve build speed

## [0.2.0](https://github.com/airbytehq/airbyte/milestone/2?closed=1) - delivered on 10/21/2020

* **a new Admin section** to enable users to add their own connectors, in addition to upgrading the ones they currently use
* improve the developer experience \(DX\) for **contributing new connectors** with additional documentation and a connector protocol
* our own **BigQuery** warehouse connector
* our own **Postgres** warehouse connector
* simplify the process of supporting new Singer taps, ideally make it a 1-day process

## [0.1.0](https://github.com/airbytehq/airbyte/milestone/1?closed=1) - delivered on 09/23/2020

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

