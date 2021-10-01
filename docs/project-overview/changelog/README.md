# Changelog

## 09/09/2021 Summary

We're going over the changes from 0.29.17 and before... and there's a lot of big improvements here, so don't miss them!

**New Source**: Facebook Pages
**New Destination**: MongoDB
**New Destination**: DynamoDB

* 🎉 You can now send notifications via webhook for successes and failures on Airbyte syncs. (This is a massive contribution by @Pras, thank you) :tada:
* 🎉 Scheduling jobs and worker jobs are now separated, allowing for workers to be scaled horizontally.
* 🎉 When developing a connector, you can now preview what your spec looks like in real time with this process.
* 🎉 Oracle destination: Now has basic normalization.
* 🎉 Add XLSB (binary excel) support to the Files source (contributed by Muutech).
* 🎉 You can now properly cancel K8s deployments.

* ✨ S3 source: Support for Parquet format.
* ✨ Github source: Branches, repositories, organization users, tags, and pull request stats streams added (contributed by @Christopher Wu).
* ✨ BigQuery destination: Added GCS upload option.
* ✨ Salesforce source: Now Airbyte native.
* ✨ Redshift destination: Optimized for performance.

* 🏗 CDK: :tada: We’ve released a tool to generate JSON Schemas from OpenAPI specs. This should make specifying schemas for API connectors a breeze! :tada:
* 🏗 CDK: Source Acceptance Tests now verify that connectors correctly format strings which are declared as using date-time and date formats.
* 🏗 CDK: Add private options to help in testing: _limit and _page_size are now accepted by any CDK connector to minimze your output size for quick iteration while testing.

* 🐛 Fixed a bug that made it possible for connector definitions to be duplicated, violating uniqueness.
* 🐛 Pipedrive source: Output schemas no longer remove timestamp from fields.
* 🐛 Github source: Empty repos and negative backoff values are now handled correctly.
* 🐛 Harvest source: Normalization now works as expected.
* 🐛 All CDC sources: Removed sleep logic which caused exceptions when loading data from high-volume sources.
* 🐛 Slack source: Increased number of retries to tolerate flaky retry wait times on the API side.
* 🐛 Slack source: Sync operations no longer hang indefinitely.
* 🐛 Jira source: Now uses updated time as the cursor field for incremental sync instead of the created time.
* 🐛 Intercom source: Fixed inconsistency between schema and output data.
* 🐛 Hubspot source: Streams with the items property now have their schemas fixed.
* 🐛 Hubspot source: Empty strings are no longer handled as dates, fixing the deals, companies, and contacts streams.
* 🐛 Typeform source: Allows for multiple choices in responses now.
* 🐛 Shopify source: The type for the amount field is now fixed in the schema.
* 🐛 Postgres destination: \u0000(NULL) value processing is now fixed.

As usual... thank you to our wonderful contributors this week: Pras, Christopher Wu, Brian M, yahu98, Michele Zuccala, jinnig, and luizgribeiro!

## 09/01/2021 Summary

Got the changes from 0.29.13... with some other surprises!

* 🔥 There's a new way to create Airbyte sources! The team at Faros AI has created a Javascript/Typescript CDK which can be found here and in our docs here. This is absolutely awesome and give a huge thanks to Chalenge Masekera, Christopher Wu, eskrm, and Matthew Tovbin!
* ✨ New Destination: Azure Blob Storage :sparkles:

**New Source**: Bamboo HR (contributed by @Oren Haliva)
**New Source**: BigCommerce (contributed by @James Wilson)
**New Source**: Trello
**New Source**: Google Analytics V4
**New Source**: Amazon Ads

* 💎 Alpine Docker images are the new standard for Python connectors, so image sizes have dropped by around 100 MB!
* ✨ You can now apply tolerations for Airbyte Pods on K8s deployments (contributed by @Pras).
* 🐛 Shopify source: Rate limit throttling fixed.
* 📚 We now have a doc on how to deploy Airbyte at scale. Check it out here!
* 🏗 Airbyte CDK: You can now ignore HTTP status errors and override retry parameters.

As usual, thank you to our awesome contributors: Oren Haliva, Pras, James Wilson, and Muutech.

## 08/26/2021 Summary

New Source: Short.io (contributed by @Apostol Tegko)
* 💎 GitHub source: Added support for rotating through multiple API tokens!
* ✨ Syncs are now scheduled with a 3 day timeout (contributed by @Vladimir Remar).
* ✨ Google Ads source: Added UserLocationReport stream (contributed by @Max Krog).
* ✨ Cart source: Added the order_items stream.
* 🐛 Postgres source: Fixed out-of-memory issue with CDC interacting with large JSON blobs.
* 🐛 Intercom source: Pagination now works as expected.

As always, thank you to our awesome community contributors this week: Apostol Tegko, Vladimir Remar, Max Krog, Pras, Marco Fontana, Troy Harvey, and damianlegawiec!
## 08/20/2021 Summary

Hey Airbyte community, we got some patch notes for y'all. Here's all the changes we've pushed since the last update.

* **New Source**: S3/Abstract Files
* **New Source**: Zuora
* **New Source**: Kustomer
* **New Source**: Apify
* **New Source**: Chargebee
* **New Source**: Bing Ads

New Destination: Keen

* ✨ Shopify source: The `status` property is now in the `Products` stream.
* ✨ Amazon Seller Partner source: Added support for `GET_MERCHANT_LISTINGS_ALL_DATA` and `GET_FBA_INVENTORY_AGED_DATA` stream endpoints.
* ✨ GitHub source: Existing streams now don't minify the user property.
* ✨ Hubspot source: Updated user-defined custom field schema generation.
* ✨ Zendesk source: Migrated from Singer to the Airbyte CDK.
* ✨ Amazon Seller Partner source: Migrated to the Airbyte CDK.
* 🐛 Shopify source: Fixed the `products` schema to be in accordance with the API.
* 🐛 S3 source: Fixed bug where syncs could hang indefinitely.

And as always... we'd love to shout out the awesome contributors that have helped push Airbyte forward. As a reminder, you can now see your contributions publicly reflected on our [contributors page](https://airbyte.io/contributors).

Thank you to Rodrigo Parra, Brian Krausz, Max Krog, Apostol Tegko, Matej Hamas, Vladimir Remar, Marco Fontana, Nicholas Bull, @mildbyte, @subhaklp, and Maciej Nędza!

## 07/30/2021 Summary

For this week's update, we got... a few new connectors this week in 0.29.0. We found that a lot of sources can pull data directly from the underlying db instance, which we naturally already supported.

* New Source: PrestaShop ✨
* New Source: Snapchat Marketing ✨
* New Source: Drupal
* New Source: Magento
* New Source: Microsoft Dynamics AX
* New Source: Microsoft Dynamics Customer Engagement
* New Source: Microsoft Dynamics GP
* New Source: Microsoft Dynamics NAV
* New Source: Oracle PeopleSoft
* New Source: Oracle Siebel CRM
* New Source: SAP Business One
* New Source: Spree Commerce
* New Source: Sugar CRM
* New Source: Wordpress
* New Source: Zencart


* 🐛 Shopify source: Fixed the products schema to be in accordance with the API
* 🐛 BigQuery source: No longer fails with nested array data types.

View the full release highlights here: [Platform](./platform.md), [Connectors](./connectors.md)

And as always, thank you to our wonderful contributors: Madison Swain-Bowden, Brian Krausz, Apostol Tegko, Matej Hamas, Vladimir Remar, Oren Haliva, satishblotout, jacqueskpoty, wallies

## 07/23/2021 Summary

What's going on? We just released 0.28.0 and here's the main highlights.


* New Destination: Google Cloud Storage ✨
* New Destination: Kafka ✨ (contributed by @Mario Molina)
* New Source: Pipedrive
* New Source: US Census (contributed by @Daniel Mateus Pires (Earnest Research))


* ✨ Google Ads source: Now supports Campaigns, Ads, AdGroups, and Accounts streams.
* ✨ Stripe source: All subscription types (including expired and canceled ones) are now returned.
* 🐛 Facebook source: Improved rate limit management
* 🐛 Square source: The send_request method is no longer broken due to CDK changes
* 🐛 MySQL destination: Does not fail on columns with JSON data now.

View the full release highlights here: [Platform](./platform.md), [Connectors](./connectors.md)

And as always, thank you to our wonderful contributors: Mario Molina, Daniel Mateus Pires (Earnest Research), gunu, Ankur Adhikari, Vladimir Remar, Madison Swain-Bowden, Maksym Pavlenok, Sam Crowder, mildbyte, avida, and gaart

## 07/16/2021 Summary

As for our changes this week...

* New Source: Zendesk Sunshine
* New Source: Dixa
* New Source: Typeform


* 💎 MySQL destination: Now supports normalization!  
* 💎 MSSQL source: Now supports CDC (Change Data Capture)
* ✨ Snowflake destination: Data coming from Airbyte is now identifiable
* 🐛 GitHub source: Now uses the correct cursor field for the IssueEvents stream
* 🐛 Square source: The send_request method is no longer broken due to CDK changes

View the full release highlights here: [Platform](./platform.md), [Connectors](./connectors.md)

As usual, thank you to our awesome community contributors this week: Oliver Meyer, Varun, Brian Krausz, shadabshaukat, Serhii Lazebnyi, Juliano Benvenuto Piovezan, mildbyte, and Sam Crowder!

## 07/09/2021 Summary

* New Source: PayPal Transaction
* New Source: Square
* New Source: SurveyMonkey
* New Source: CockroachDB
* New Source: Airbyte-Native GitHub
* New Source: Airbyte-Native GitLab
* New Source: Airbyte-Native Twilio


* ✨ S3 destination: Now supports anyOf, oneOf and allOf schema fields.
* ✨ Instagram source: Migrated to the CDK and has improved error handling.
* ✨ Shopify source: Add support for draft orders.
* ✨ K8s Deployments: Now support logging to GCS.
* 🐛 GitHub source: Fixed issue with locked breaking normalization of the pull_request stream.
* 🐛 Okta source: Fix endless loop when syncing data from logs stream.
* 🐛 PostgreSQL source: Fixed decimal handling with CDC.
* 🐛 Fixed random silent source failures.
* 📚 New document on how the CDK handles schemas.
* 🏗️ Python CDK: Now allows setting of network adapter args on outgoing HTTP requests.

View the full release highlights here: [Platform](./platform.md), [Connectors](./connectors.md)

As usual, thank you to our awesome community contributors this week: gunu, P.VAD, Rodrigo Parra, Mario Molina, Antonio Grass, sabifranjo, Jaime Farres, shadabshaukat, Rodrigo Menezes, dkelwa, Jonathan Duval, and Augustin Lafanechère.

## 07/01/2021 Summary

* New Destination: Google PubSub
* New Source: AWS CloudTrail

*The risks and issues with upgrading Airbyte are now gone...*
* 🎉 Airbyte automatically upgrades versions safely at server startup 🎉


* 💎 Logs on K8s are now stored in Minio by default, no S3 bucket required
* ✨ Looker Source: Supports the Run Look output stream
* ✨ Slack Source: is now Airbyte native!
* 🐛 Freshdesk Source: No longer fails after 300 pages
* 📚 New tutorial on building Java destinations

Starting from next week, our weekly office hours will now become demo days! Drop by to get sneak peeks and new feature demos.

* We added the #careers channel, so if you're hiring, post your job reqs there!
* We added a #understanding-airbyte channel to mirror [this](../../understanding-airbyte) section on our docs site. Ask any questions about our architecture or protocol there.
* We added a #contributing-to-airbyte channel. A lot of people ask us about how to contribute to the project, so ask away there!

View the full release highlights here: [Platform](./platform.md), [Connectors](./connectors.md)

As usual, thank you to our awesome community contributors this week: Harshith Mullapudi, Michael Irvine, and [sabifranjo](https://github.com/sabifranjo).

## 06/24/2021 Summary

* New Source: [IBM Db2](../../integrations/sources/db2.md)
* 💎 We now support Avro and JSONL output for our S3 destination! 💎
* 💎 Brand new BigQuery destination flavor that now supports denormalized STRUCT types.
* ✨ Looker source now supports self-hosted instances.
* ✨ Facebook Marketing source is now migrated to the CDK, massively improving async job performance and error handling.

View the full connector release notes [here](./connectors.md).

As usual, thank you to some of our awesome community contributors this week: Harshith Mullapudi, Tyler DeLange, Daniel Mateus Pires, EdBizarro, Tyler Schroeder, and Konrad Schlatte!

## 06/18/2021 Summary

* New Source: [Snowflake](../../integrations/sources/snowflake.md)
* 💎 We now support custom dbt transformations! 💎
* ✨ We now support configuring your destination namespace at the table level when setting up a connection!
* ✨ The S3 destination now supports Minio S3 and Parquet output!

View the full release notes here: [Platform](./platform.md), [Connectors](./connectors.md)

As usual, thank you to some of our awesome community contributors this week: Tyler DeLange, Mario Molina, Rodrigo Parra, Prashanth Patali, Christopher Wu, Itai Admi, Fred Reimer, and Konrad Schlatte!

## 06/10/2021 Summary

* New Destination: [S3!!](../../integrations/destinations/s3.md) 
* New Sources: [Harvest](../../integrations/sources/harvest.md), [Amplitude](../../integrations/sources/amplitude.md), [Posthog](../../integrations/sources/posthog.md)
* 🐛 Ensure that logs from threads created by replication workers are added to the log file.
* 🐛 Handle TINYINT(1) and BOOLEAN correctly and fix target file comparison for MySQL CDC.
* Jira source: now supports all available entities in Jira Cloud.
* 📚 Added a troubleshooting section, a gradle cheatsheet, a reminder on what the reset button does, and a refresh on our docs best practices.

#### Connector Development:
* Containerized connector code generator
* Added JDBC source connector bootstrap template.
* Added Java destination generator.

View the full release notes highlights here: [Platform](./platform.md), [Connectors](./connectors.md)

As usual, thank you to some of our awesome community contributors this week (I've noticed that we've had more contributors to our docs, which we really appreciate).
Ping, Harshith Mullapudi, Michael Irvine, Matheus di Paula, jacqueskpoty and P.VAD.

## Overview

Airbyte is comprised of 2 parts:

* Platform (The scheduler, workers, api, web app, and the Airbyte protocol). Here is the [changelog for Platform](platform.md). 
* Connectors that run in Docker containers. Here is the [changelog for the connectors](connectors.md). 

## Airbyte Platform Releases

### Production v. Dev Releases

The "production" version of Airbyte is the version of the app specified in `.env`. With each production release, we update the version in the `.env` file. This version will always be available for download on DockerHub. It is the version of the app that runs when a user runs `docker-compose up`.

The "development" version of Airbyte is the head of master branch. It is the version of the app that runs when a user runs `./gradlew composeBuild && VERSION=dev docker compose up`.

### Production Release Schedule

#### Scheduled Releases

Airbyte currently releases a new minor version of the application on a weekly basis. Generally this weekly release happens on Monday or Tuesday.

#### Hotfixes

Airbyte releases a new version whenever it discovers and fixes a bug that blocks any mission critical functionality.

**Mission Critical**

e.g. Non-ASCII characters break the Salesforce source.

**Non-Mission Critical**

e.g. Buttons in the UI are offset.

#### Unscheduled Releases

We will often release more frequently than the weekly cadence if we complete a feature that we know that a user is waiting on.

### Development Release Schedule

As soon as a feature is on master, it is part of the development version of Airbyte. We merge features as soon as they are ready to go \(have been code reviewed and tested\). We attempt to keep the development version of the app working all the time. We are iterating quickly, however, and there may be intermittent periods where the development version is broken.

If there is ever a feature that is only on the development version, and you need it on the production version, please let us know. We are very happy to do ad-hoc production releases if it unblocks a specific need for one of our users.

## Airbyte Connector Releases

Each connector is tracked with its own version. These versions are separate from the versions of Airbyte Platform. We generally will bump the version of a connector anytime we make a change to it. We rely on a large suite of tests to make sure that these changes do not cause regressions in our connectors.

When we updated the version of a connector, we usually update the connector's version in Airbyte Platform as well. Keep in mind that you might not see the updated version of that connector in the production version of Airbyte Platform until after a production release of Airbyte Platform.

