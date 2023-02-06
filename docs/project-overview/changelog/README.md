# Changelog

## 1/28/2022 Summary

* New Source: Chartmogul (contributyed by Titas Skrebė)
* New Source: Hellobaton (contributed by Daniel Luftspring)
* New Source: Flexport (contributed by Juozas)
* New Source: PersistIq (contributed by Wadii Zaim)

* ✨ Postgres Source: Users can now select which schemas they wish to sync before discovery. This makes the discovery stage for large instances much more performant.
* ✨ Shopify Source: Now verifies permissions on the token before accessing resources.
* ✨ Snowflake Destination: Users now have access to an option to purge their staging data.
* ✨ HubSpot Source: Added some more fields for the email_events stream.
* ✨ Amazon Seller Partner Source: Added the GET_FLAT_FILE_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL report stream. (contributed by @ron-damon)
* ✨ HubSpot Source: Added the form_submission and property_history streams.
  
* 🐛 DynamoDB Destination: The parameter dynamodb_table_name is now named dynamodb_table_name_prefix to more accurately represent it.
* 🐛 Intercom Source: The handling of scroll param is now fixed when it is expired.
* 🐛 S3 + GCS Destinations: Now support arrays with unknown item type.
* 🐛 Postgres Source: Now supports handling of the Java SQL date type.
* 🐛 Salesforce Source: No longer fails during schema generation.

## 1/13/2022 Summary

⚠️ WARNING ⚠️

Snowflake Source: Normalization with Snowflake now produces permanent tables. [If you want to continue creating transient tables, you will need to create a new transient database for Airbyte.]

* ✨ GitHub Source: PR related streams now support incremental sync.
* ✨ HubSpot Source: We now support ListMemberships in the Contacts stream.
* ✨ Azure Blob Storage Destination: Now has the option to add a BufferedOutputStream to improve performance and fix writing data with over 50GB in a stream. (contributed by @bmatticus)
  
* 🐛 Normalization partitioning now works as expected with FLOAT64 and BigQuery.
* 🐛 Normalization now works properly with quoted and case sensitive columns.
* 🐛 Source MSSQL: Added support for some missing data types.
* 🐛 Snowflake Destination: Schema is now not created if it previously exists.
* 🐛 Postgres Source: Now properly reads materialized views.
* 🐛 Delighted Source: Pagination for survey_responses, bounces and unsubscribes streams now works as expected.
* 🐛 Google Search Console Source: Incremental sync now works as expected.
* 🐛 Recurly Source: Now does not load all accounts when importing account coupon redemptions.
* 🐛 Salesforce Source: Now properly handles 400 when streams don't support query or queryAll.

## 1/6/2022 Summary

* New Source: 3PL Central (contributed by Juozas)
* New Source: My Hours (contributed by Wisse Jelgersma)
* New Source: Qualaroo (contributed by gunu)
* New Source: SearchMetrics
  
* 💎 Salesforce Source: Now supports filtering streams at configuration, making it easier to handle large Salesforce instances.
* 💎 Snowflake Destination: Now supports byte-buffering for staged inserts.
* 💎 Redshift Destination: Now supports byte-buffering for staged inserts.
* ✨ Postgres Source: Now supports all Postgres 14 types.
* ✨ Recurly Source: Now supports incremental sync for all streams.
* ✨ Zendesk Support Source: Added the Brands, CustomRoles, and Schedules streams.
* ✨ Zendesk Support Source: Now uses cursor-based pagination.
* ✨ Kustomer Source: Setup configuration is now more straightforward.
* ✨ Hubspot Source: Now supports incremental sync on all streams where possible.
* ✨ Facebook Marketing Source: Fixed schema for breakdowns fields.
* ✨ Facebook Marketing Source: Added asset_feed_spec to AdCreatives stream.
* ✨ Redshift Destination: Now has an option to toggle the deletion of staging data.

* 🐛 S3 Destination: Avro and Parquet formats are now processed correctly.
* 🐛 Snowflake Destination: Fixed SQL Compliation error.
* 🐛 Kafka Source: SASL configurations no longer throw null pointer exceptions (contributed by Nitesh Kumar)
* 🐛 Salesforce Source: Now throws a 400 for non-queryable streams.
* 🐛 Amazon Ads Source: Polling for report generation is now much more resilient. (contributed by Juozas)
* 🐛 Jira Source: The filters stream now works as expected.
* 🐛 BigQuery Destination: You can now properly configure the buffer size with the part_size config field.
* 🐛 Snowflake Destination: You can now properly configure the buffer size with the part_size config field.
* 🐛 CockroachDB Source: Now correctly only discovers tables the user has permission to access.
* 🐛 Stripe Source: The date and arrival_date fields are now typed correctly.

## 12/16/2021 Summary

🎉  First off... There's a brand new CDK! Menno Hamburg contributed a .NET/C# implementation for our CDK, allowing you to write HTTP API sources and Generic Dotnet sources. Thank you so much Menno, this is huge!

* New Source: OpenWeather
* New Destination: ClickHouse (contributed by @Bo)
* New Destination: RabbitMQ (contributed by @Luis Gomez)
* New Destination: Amazon SQS (contributed by @Alasdair Brown)
* New Destination: Rockset (contributed by @Steve Baldwin)

* ✨ Facebook Marketing Source: Updated the campaign schema with more relevant fields. (contributed by @Maxime Lavoie)
* ✨ TikTok Marketing Source: Now supports the Basic Report stream.
* ✨ MySQL Source: Now supports all MySQL 8.0 data types.
* ✨ Klaviyo Source: Improved performance, added incremental sync support to the Global Exclusions stream.
* ✨ Redshift Destination: You can now specify a bucket path to stage your data in before inserting.
* ✨ Kubernetes deployments: Sidecar memory is now 25Mi, up from 6Mi to cover all usage cases.
* ✨ Kubernetes deployments: The Helm chart can now set up writing logs to S3 easily. (contributed by @Valentin Nourdin)
  
* 🐛 Python CDK: Now shows the stack trace of unhandled exceptions.
* 🐛 Google Analytics Source: Fix data window input validation, fix date type conversion.
* 🐛 Google Ads Source: Data from the end_date for syncs is now included in a sync.
* 🐛 Marketo Source: Fixed issues around input type conversion and conformation to the schema.
* 🐛 Mailchimp Source: Fixed schema conversion error causing sync failures.
* 🐛 PayPal Transactions Source: Now reports full error message details on failure.
* 🐛 Shopify Source: Normalization now works as expected.

## 12/9/2021 Summary

⚠️ WARNING ⚠️

v0.33.0 is a minor version with breaking changes. Take the normal precautions with upgrading safely to this version.
v0.33.0 has a bug that affects GCS logs on Kubernetes. Upgrade straight to v0.33.2 if you are running a K8s deployment of Airbyte.

* New Source: Mailgun

🎉 Snowflake Destination: You can now stage your inserts, making them much faster.

* ✨ Google Ads Source: Source configuration is now more clear.
* ✨ Google Analytics Source: Source configuration is now more clear.
* ✨ S3 Destination: You can now write timestamps in Avro and Parquet formats.
* ✨ BigQuery & BigQuery Denormalized Destinations: Now use byte-based buffering for batch inserts.
* ✨ Iterable Source: Now has email validation on the list_users stream.

* 🐛 Incremental normalization now works properly with empty tables.
* 🐛 LinkedIn Ads Source: 429 response is now properly handled.
* 🐛 Intercom Source: Now handles failed pagination requests with backoffs.
* 🐛 Intercom Source: No longer drops records from the conversation stream.
* 🐛 Google Analytics Source: 400 errors no longer get ignored with custom reports.
* 🐛 Marketo Source: The createdAt and updatedAt fields are now formatted correctly.

## 12/2/2021 Summary

🎃 **Hacktoberfest Submissions** 🎃
-----------------------------------------
* New Destination: Redis (contributed by @Ivica Taseski)
* New Destination: MQTT (contributed by @Mario Molina)
* New Destination: Google Firestore (contributed by @Adam Dobrawy)
* New Destination: Kinesis (contributed by @Ivica Taseski)
* New Source: Zenloop (contributed by @Alexander Batoulis)
* New Source: Outreach (contributed by @Luis Gomez)

* ✨ Zendesk Source: The chats stream now supports incremental sync and added testing for all streams.
* 🐛 Monday Source: Pagination now works as expected and the schema has been fixed.
* 🐛 Postgres Source: Views are now properly listed during schema discovery.
* 🐛 Postgres Source: Using the money type with an amount greater than 1000 works properly now.
* 🐛 Google Search Console Search: We now set a default end_data value.
* 🐛 Mixpanel Source: Normalization now works as expected and streams are now displayed properly in the UI.
* 🐛 MongoDB Source: The DATE_TIME type now uses milliseconds.

## 11/25/2021 Summary
Hey Airbyte Community! Let's go over all the changes from v.32.5 and prior!

🎃 **Hacktoberfest Submissions** 🎃
* New Source: Airtable (contributed by Tuan Nguyen).
* New Source: Notion (contributed by Bo Lu).
* New Source: Pardot (contributed by Tuan Nguyen).

* New Source: Youtube analytics.

* ✨ Source Exchange Rates: add ignore_weekends option.
* ✨ Source Facebook: add the videos stream.
* ✨ Source Freshdesk: removed the limitation in streams pagination.
* ✨ Source Jira: add option to render fields in HTML format.
* ✨ Source MongoDB v2: improve read performance.
* ✨ Source Pipedrive: specify schema for "persons" stream.
* ✨ Source PostgreSQL: exclude tables on which user doesn't have select privileges.
* ✨ Source SurveyMonkey: improve connection check.

* 🐛 Source Salesforce:  improve resiliency of async bulk jobs.
* 🐛 Source Zendesk Support: fix missing ticket_id in ticket_comments stream.
* 🐛 Normalization: optimize incremental normalization runtime with Snowflake.

As usual, thank you so much to our wonderful contributors this week that have made Airbyte into what it is today: Madison Swain-Bowden, Tuan Nguyen, Bo Lu, Adam Dobrawy, Christopher Wu, Luis Gomez, Ivica Taseski, Mario Molina, Ping Yee, Koji Matsumoto, Sujit Sagar, Shadab, Juozas V.([Labanoras Tech](http://labanoras.io)) and Serhii Chvaliuk!

## 11/17/2021 Summary

Hey Airbyte Community! Let's go over all the changes from v.32.1 and prior! But first, there's an important announcement I need to make about upgrading Airbyte to v.32.1.

⚠️ WARNING ⚠️
Upgrading to v.32.0 is equivalent to a major version bump. If your current version is v.32.0, you must upgrade to v.32.0 first before upgrading to any later version

Keep in mind that this upgrade requires your all of your connector Specs to be retrievable, or Airbyte will fail on startup. You can force delete your connector Specs by setting the `VERSION_0_32_0_FORCE_UPGRADE` environment variable to `true`. Steps to specifically check out v.32.0 and details around this breaking change can be found [here](../../operator-guides/upgrading-airbyte#mandatory-intermediate-upgrade).

*Now back to our regularly scheduled programming.*

🎃 Hacktoberfest Submissions 🎃

* New Destination: ScyllaDB (contributed by Ivica Taseski)
* New Source: Azure Table Storage (contributed by geekwhocodes)
* New Source: Linnworks (contributed by Juozas V.([Labanoras Tech](http://labanoras.io)))

* ✨ Source MySQL: Now has basic performance tests.
* ✨ Source Salesforce: We now automatically transform and handle incorrect data for the anyType and calculated types.

* 🐛 IBM Db2 Source: Now handles conversion from DECFLOAT to BigDecimal correctly.
* 🐛 MSSQL Source: Now handles VARBINARY correctly.
* 🐛 CockroachDB Source: Improved parsing of various data types.

As usual, thank you so much to our wonderful contributors this week that have made Airbyte into what it is today: Achmad Syarif Hidayatullah, Tuan Nguyen, Ivica Taseski, Hai To, Juozas, gunu, Shadab, Per-Victor Persson, and Harsha Teja Kanna!

## 11/11/2021 Summary

Time to go over changes from v.30.39! And... let's get another update on Hacktoberfest.

🎃 Hacktoberfest Submissions 🎃

* New Destination: Cassandra (contributed by Ivica Taseski)
* New Destination: Pulsar (contributed by Mario Molina)
* New Source: Confluence (contributed by Tuan Nguyen)
* New Source: Monday (contributed by Tuan Nguyen)
* New Source: Commerce Tools (contributed by James Wilson)
* New Source: Pinterest Marketing (contributed by us!)

* ✨ Shopify Source: Now supports the FulfillmentOrders and Fulfillments streams.
* ✨ Greenhouse Source: Now supports the Demographics stream.
* ✨ Recharge Source: Broken requests should now be re-requested with improved backoff.
* ✨ Stripe Source: Now supports the checkout_sessions, checkout_sessions_line_item, and promotion_codes streams.
* ✨ Db2 Source: Now supports SSL.

* 🐛 We've made some updates to incremental normalization to fix some outstanding issues. [Details](https://github.com/airbytehq/airbyte/pull/7669)
* 🐛 Airbyte Server no longer crashes due to too many open files.
* 🐛 MSSQL Source: Data type conversion with smalldatetime and smallmoney works correctly now.
* 🐛 Salesforce Source: anyType fields can now be retrieved properly with the BULK API
* 🐛 BigQuery-Denormalized Destination: Fixed JSON parsing with $ref fields.

As usual, thank you to our awesome contributors that have done awesome work during the last week: Tuan Nguyen, Harsha Teja Kanna, Aaditya S, James Wilson, Vladimir Remar, Yuhui Shi, Mario Molina, Ivica Taseski, Collin Scangarella, and haoranyu!

## 11/03/2021 Summary

It's patch notes time. Let's go over the changes from 0.30.24 and before. But before we do, let's get a quick update on how Hacktober is going!

🎃 Hacktoberfest Submissions 🎃

* New Destination: Elasticsearch (contributed by Jeremy Branham)
* New Source: Salesloft (contributed by Pras)
* New Source: OneSignal (contributed by Bo)
* New Source: Strava (contributed by terencecho)
* New Source: Lemlist (contributed by Igli Koxha)
* New Source: Amazon SQS (contributed by Alasdair Brown)
* New Source: Freshservices (contributed by Tuan Nguyen)
* New Source: Freshsales (contributed by Tuan Nguyen)
* New Source: Appsflyer (contributed by Achmad Syarif Hidayatullah)
* New Source: Paystack (contributed by Foluso Ogunlana)
* New Source: Sentry (contributed by koji matsumoto)
* New Source: Retently (contributed by Subhash Gopalakrishnan)
* New Source: Delighted! (contributed by Rodrigo Parra)

with 18 more currently in review...

🎉 **Incremental Normalization is here!** 🎉

💎 Basic normalization no longer runs on already normalized data, making it way faster and cheaper. :gem:

🎉 **Airbyte Compiles on M1 Macs!**

Airbyte developers with M1 chips in their MacBooks can now compile the project and run the server. This is a major step towards being able to fully run Airbyte on M1. (contributed by Harsha Teja Kanna)

* ✨ BigQuery Destination: You can now run transformations in batches, preventing queries from hitting BigQuery limits. (contributed by Andrés Bravo)
* ✨ S3 Source: Memory and Performance optimizations, also some fancy new PyArrow CSV configuration options.
* ✨ Zuora Source: Now supports Unlimited as an option for the Data Query Live API.
* ✨ Clickhouse Source: Now supports SSL and connection via SSH tunneling.

* 🐛 Oracle Source: Now handles the LONG RAW data type correctly.
* 🐛 Snowflake Source: Fixed parsing of extreme values for FLOAT and NUMBER data types.
* 🐛 Hubspot Source: No longer fails due to lengthy URI/URLs.
* 🐛 Zendesk Source: The chats stream now pulls data past the first page.
* 🐛 Jira Source: Normalization now works as expected.

As usual, thank you to our awesome contributors that have done awesome work during this productive spooky season: Tuan Nguyen, Achmad Syarif Hidayatullah, Christopher Wu, Andrés Bravo, Harsha Teja Kanna, Collin Scangarella, haoranyu, koji matsumoto, Subhash Gopalakrishnan, Jeremy Branham, Rodrigo Parra, Foluso Ogunlana, EdBizarro, Gergely Lendvai, Rodeoclash, terencecho, Igli Koxha, Alasdair Brown, bbugh, Pras, Bo, Xiangxuan Liu, Hai To, s-mawjee, Mario Molina, SamyPesse, Yuhui Shi, Maciej Nędza, Matt Hoag, and denis-sokolov!

## 10/20/2021 Summary

It's patch notes time! Let's go over changes from 0.30.16! But before we do... I want to remind everyone that Airbyte Hacktoberfest is currently taking place! For every connector that is merged into our codebase, you'll get $500, so make sure to submit before the hackathon ends on November 19th.

* 🎉 New Source: WooCommerce (contributed by James Wilson)
* 🎉 K8s deployments: Worker image pull policy is now configurable (contributed by Mario Molina)

* ✨ MSSQL destination: Now supports basic normalization
* 🐛 LinkedIn Ads source: Analytics streams now work as expected.

We've had a lot of contributors over the last few weeks, so I'd like to thank all of them for their efforts: James Wilson, Mario Molina, Maciej Nędza, Pras, Tuan Nguyen, Andrés Bravo, Christopher Wu, gunu, Harsha Teja Kanna, Jonathan Stacks, darian, Christian Gagnon, Nicolas Moreau, Matt Hoag, Achmad Syarif Hidayatullah, s-mawjee, SamyPesse, heade, zurferr, denis-solokov, and aristidednd!

## 09/29/2021 Summary

It's patch notes time, let's go over the changes from our new minor version, v0.30.0. As usual, bug fixes are in the thread.

* New source: LinkedIn Ads
* New source: Kafka
* New source: Lever Hiring

* 🎉 New License: Nothing changes for users of Airbyte/contributors. You just can't sell your own Airbyte Cloud!

* 💎 New API endpoint: You can now call connections/search in the web backend API to search sources and destinations. (contributed by Mario Molina)
* 💎 K8s: Added support for ImagePullSecrets for connector images.
* 💎 MSSQL, Oracle, MySQL sources & destinations: Now support connection via SSH (Bastion server)

* ✨ MySQL destination: Now supports connection via TLS/SSL
* ✨ BigQuery (denormalized) destination: Supports reading BigQuery types such as date by reading the format field (contributed by Nicolas Moreau)
* ✨ Hubspot source: Added contacts associations to the deals stream.
* ✨ GitHub source: Now supports pulling commits from user-specified branches.
* ✨ Google Search Console source: Now accepts admin email as input when using a service account key.
* ✨ Greenhouse source: Now identifies API streams it has access to if permissions are limited.
* ✨ Marketo source: Now Airbyte native.
* ✨ S3 source: Now supports any source that conforms to the S3 protocol (Non-AWS S3).
* ✨ Shopify source: Now reports pre_tax_price on the line_items stream if you have Shopify Plus.
* ✨ Stripe source: Now actually uses the mandatory start_date config field for incremental syncs.

* 🏗 Python CDK: Now supports passing custom headers to the requests in OAuth2, enabling token refresh calls.
* 🏗 Python CDK: Parent streams can now be configured to cache data for their child streams.
* 🏗 Python CDK: Now has a Transformer class that can cast record fields to the data type expected by the schema.

* 🐛 Amplitude source: Fixed schema for date-time objects.
* 🐛 Asana source: Schema fixed for the sections, stories, tasks, and users streams.
* 🐛 GitHub source: Added error handling for streams not applicable to a repo. (contributed by Christopher Wu)
* 🐛 Google Search Console source: Verifies access to sites when performing the connection check.
* 🐛 Hubspot source: Now conforms to the V3 API, with streams such as owners reflecting the new fields.
* 🐛 Intercom source: Fixed data type for the updated_at field. (contributed by Christian Gagnon)
* 🐛 Iterable source: Normalization now works as expected.
* 🐛 Pipedrive source: Schema now reflects the correct types for date/time fields.
* 🐛 Stripe source: Incorrect timestamp formats removed for coupons and subscriptions streams.
* 🐛 Salesforce source: You can now sync more than 10,000 records with the Bulk API.
* 🐛 Snowflake destination: Now accepts any date-time format with normalization.
* 🐛 Snowflake destination: Inserts are now split into batches to accommodate for large data loads.

Thank you to our awesome contributors. Y'all are amazing: Mario Molina, Pras, Vladimir Remar, Christopher Wu, gunu, Juliano Benvenuto Piovezan, Brian M, Justinas Lukasevicius, Jonathan Stacks, Christian Gagnon, Nicolas Moreau, aristidednd, camro, minimax75, peter-mcconnell, and sashkalife!

## 09/16/2021 Summary

Now let's get to the 0.29.19 changelog. As with last time, bug fixes are in the thread!

* New Destination: Databricks 🎉
* New Source: Google Search Console
* New Source: Close.com

* 🏗 Python CDK: Now supports auth workflows involving query params.
* 🏗 Java CDK: You can now run the connector gradle build script on Macs with M1 chips! (contributed by @Harsha Teja Kanna)

* 💎 Google Ads source: You can now specify user-specified queries in GAQL.
* ✨ GitHub source: All streams with a parent stream use cached parent stream data when possible.
* ✨ Shopify source: Substantial performance improvements to the incremental sync mode.
* ✨ Stripe source: Now supports the PaymentIntents stream.
* ✨ Pipedrive source: Now supports the Organizations stream.
* ✨ Sendgrid source: Now supports the SingleSendStats stream.
* ✨ Bing Ads source: Now supports the Report stream.
* ✨ GitHub source: Now supports the Reactions stream.
* ✨ MongoDB source: Now Airbyte native!
* 🐛 Facebook Marketing source: Numeric values are no longer wrapped into strings.
* 🐛 Facebook Marketing source: Fetching conversion data now works as expected. (contributed by @Manav)
* 🐛 Keen destination: Timestamps are now parsed correctly.
* 🐛 S3 destination: Parquet schema parsing errors are fixed.
* 🐛 Snowflake destination: No longer syncs unnecessary tables with S3.
* 🐛 SurveyMonkey source: Cached responses are now decoded correctly.
* 🐛 Okta source: Incremental sync now works as expected.

Also, a quick shout out to Jinni Gu and their team who made the DynamoDB destination that we announced last week!

As usual, thank you to all of our contributors: Harsha Teja Kanna, Manav, Maciej Nędza, mauro, Brian M, Iakov Salikov, Eliziario (Marcos Santos), coeurdestenebres, and mohammadbolt.

## 09/09/2021 Summary

We're going over the changes from 0.29.17 and before... and there's a lot of big improvements here, so don't miss them!

**New Source**: Facebook Pages **New Destination**: MongoDB **New Destination**: DynamoDB

* 🎉 You can now send notifications via webhook for successes and failures on Airbyte syncs. \(This is a massive contribution by @Pras, thank you\) 🎉
* 🎉 Scheduling jobs and worker jobs are now separated, allowing for workers to be scaled horizontally.
* 🎉 When developing a connector, you can now preview what your spec looks like in real time with this process.
* 🎉 Oracle destination: Now has basic normalization.
* 🎉 Add XLSB \(binary excel\) support to the Files source \(contributed by Muutech\).
* 🎉 You can now properly cancel K8s deployments.
* ✨ S3 source: Support for Parquet format.
* ✨ Github source: Branches, repositories, organization users, tags, and pull request stats streams added \(contributed by @Christopher Wu\).
* ✨ BigQuery destination: Added GCS upload option.
* ✨ Salesforce source: Now Airbyte native.
* ✨ Redshift destination: Optimized for performance.
* 🏗 CDK: 🎉 We’ve released a tool to generate JSON Schemas from OpenAPI specs. This should make specifying schemas for API connectors a breeze! 🎉
* 🏗 CDK: Source Acceptance Tests now verify that connectors correctly format strings which are declared as using date-time and date formats.
* 🏗 CDK: Add private options to help in testing: \_limit and \_page\_size are now accepted by any CDK connector to minimze your output size for quick iteration while testing.
* 🐛 Fixed a bug that made it possible for connector definitions to be duplicated, violating uniqueness.
* 🐛 Pipedrive source: Output schemas no longer remove timestamp from fields.
* 🐛 Github source: Empty repos and negative backoff values are now handled correctly.
* 🐛 Harvest source: Normalization now works as expected.
* 🐛 All CDC sources: Removed sleep logic which caused exceptions when loading data from high-volume sources.
* 🐛 Slack source: Increased number of retries to tolerate flaky retry wait times on the API side.
* 🐛 Slack source: Sync operations no longer hang indefinitely.
* 🐛 Jira source: Now uses updated time as the cursor field for incremental sync instead of the created time.
* 🐛 Intercom source: Fixed inconsistency between schema and output data.
* 🐛 HubSpot source: Streams with the items property now have their schemas fixed.
* 🐛 HubSpot source: Empty strings are no longer handled as dates, fixing the deals, companies, and contacts streams.
* 🐛 Typeform source: Allows for multiple choices in responses now.
* 🐛 Shopify source: The type for the amount field is now fixed in the schema.
* 🐛 Postgres destination: \u0000\(NULL\) value processing is now fixed.

As usual... thank you to our wonderful contributors this week: Pras, Christopher Wu, Brian M, yahu98, Michele Zuccala, jinnig, and luizgribeiro!

## 09/01/2021 Summary

Got the changes from 0.29.13... with some other surprises!

* 🔥 There's a new way to create Airbyte sources! The team at Faros AI has created a Javascript/Typescript CDK which can be found here and in our docs here. This is absolutely awesome and give a huge thanks to Chalenge Masekera, Christopher Wu, eskrm, and Matthew Tovbin!
* ✨ New Destination: Azure Blob Storage ✨

**New Source**: Bamboo HR \(contributed by @Oren Haliva\) **New Source**: BigCommerce \(contributed by @James Wilson\) **New Source**: Trello **New Source**: Google Analytics V4 **New Source**: Amazon Ads

* 💎 Alpine Docker images are the new standard for Python connectors, so image sizes have dropped by around 100 MB!
* ✨ You can now apply tolerations for Airbyte Pods on K8s deployments \(contributed by @Pras\).
* 🐛 Shopify source: Rate limit throttling fixed.
* 📚 We now have a doc on how to deploy Airbyte at scale. Check it out here!
* 🏗 Airbyte CDK: You can now ignore HTTP status errors and override retry parameters.

As usual, thank you to our awesome contributors: Oren Haliva, Pras, James Wilson, and Muutech.

## 08/26/2021 Summary

New Source: Short.io \(contributed by @Apostol Tegko\)

* 💎 GitHub source: Added support for rotating through multiple API tokens!
* ✨ Syncs are now scheduled with a 3 day timeout \(contributed by @Vladimir Remar\).
* ✨ Google Ads source: Added UserLocationReport stream \(contributed by @Max Krog\).
* ✨ Cart.com source: Added the order\_items stream.
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
* ✨ HubSpot source: Updated user-defined custom field schema generation.
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

View the full release highlights here: [Platform](platform.md), [Connectors](connectors.md)

And as always, thank you to our wonderful contributors: Madison Swain-Bowden, Brian Krausz, Apostol Tegko, Matej Hamas, Vladimir Remar, Oren Haliva, satishblotout, jacqueskpoty, wallies

## 07/23/2021 Summary

What's going on? We just released 0.28.0 and here's the main highlights.

* New Destination: Google Cloud Storage ✨
* New Destination: Kafka ✨ \(contributed by @Mario Molina\)
* New Source: Pipedrive
* New Source: US Census \(contributed by @Daniel Mateus Pires \(Earnest Research\)\)
* ✨ Google Ads source: Now supports Campaigns, Ads, AdGroups, and Accounts streams.
* ✨ Stripe source: All subscription types \(including expired and canceled ones\) are now returned.
* 🐛 Facebook source: Improved rate limit management
* 🐛 Square source: The send\_request method is no longer broken due to CDK changes
* 🐛 MySQL destination: Does not fail on columns with JSON data now.

View the full release highlights here: [Platform](platform.md), [Connectors](connectors.md)

And as always, thank you to our wonderful contributors: Mario Molina, Daniel Mateus Pires \(Earnest Research\), gunu, Ankur Adhikari, Vladimir Remar, Madison Swain-Bowden, Maksym Pavlenok, Sam Crowder, mildbyte, avida, and gaart

## 07/16/2021 Summary

As for our changes this week...

* New Source: Zendesk Sunshine
* New Source: Dixa
* New Source: Typeform
* 💎 MySQL destination: Now supports normalization!  
* 💎 MSSQL source: Now supports CDC \(Change Data Capture\)
* ✨ Snowflake destination: Data coming from Airbyte is now identifiable
* 🐛 GitHub source: Now uses the correct cursor field for the IssueEvents stream
* 🐛 Square source: The send\_request method is no longer broken due to CDK changes

View the full release highlights here: [Platform](platform.md), [Connectors](connectors.md)

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
* 🐛 GitHub source: Fixed issue with locked breaking normalization of the pull\_request stream.
* 🐛 Okta source: Fix endless loop when syncing data from logs stream.
* 🐛 PostgreSQL source: Fixed decimal handling with CDC.
* 🐛 Fixed random silent source failures.
* 📚 New document on how the CDK handles schemas.
* 🏗️ Python CDK: Now allows setting of network adapter args on outgoing HTTP requests.

View the full release highlights here: [Platform](platform.md), [Connectors](connectors.md)

As usual, thank you to our awesome community contributors this week: gunu, P.VAD, Rodrigo Parra, Mario Molina, Antonio Grass, sabifranjo, Jaime Farres, shadabshaukat, Rodrigo Menezes, dkelwa, Jonathan Duval, and Augustin Lafanechère.

## 07/01/2021 Summary

* New Destination: Google PubSub
* New Source: AWS CloudTrail

_The risks and issues with upgrading Airbyte are now gone..._

* 🎉 Airbyte automatically upgrades versions safely at server startup 🎉
* 💎 Logs on K8s are now stored in Minio by default, no S3 bucket required
* ✨ Looker Source: Supports the Run Look output stream
* ✨ Slack Source: is now Airbyte native!
* 🐛 Freshdesk Source: No longer fails after 300 pages
* 📚 New tutorial on building Java destinations

Starting from next week, our weekly office hours will now become demo days! Drop by to get sneak peeks and new feature demos.

* We added the \#careers channel, so if you're hiring, post your job reqs there!
* We added a \#understanding-airbyte channel to mirror [this](../../understanding-airbyte/) section on our docs site. Ask any questions about our architecture or protocol there.
* We added a \#contributing-to-airbyte channel. A lot of people ask us about how to contribute to the project, so ask away there!

View the full release highlights here: [Platform](platform.md), [Connectors](connectors.md)

As usual, thank you to our awesome community contributors this week: Harshith Mullapudi, Michael Irvine, and [sabifranjo](https://github.com/sabifranjo).

## 06/24/2021 Summary

* New Source: [IBM Db2](../../integrations/sources/db2.md)
* 💎 We now support Avro and JSONL output for our S3 destination! 💎
* 💎 Brand new BigQuery destination flavor that now supports denormalized STRUCT types.
* ✨ Looker source now supports self-hosted instances.
* ✨ Facebook Marketing source is now migrated to the CDK, massively improving async job performance and error handling.

View the full connector release notes [here](connectors.md).

As usual, thank you to some of our awesome community contributors this week: Harshith Mullapudi, Tyler DeLange, Daniel Mateus Pires, EdBizarro, Tyler Schroeder, and Konrad Schlatte!

## 06/18/2021 Summary

* New Source: [Snowflake](../../integrations/sources/snowflake.md)
* 💎 We now support custom dbt transformations! 💎
* ✨ We now support configuring your destination namespace at the table level when setting up a connection!
* ✨ The S3 destination now supports Minio S3 and Parquet output!

View the full release notes here: [Platform](platform.md), [Connectors](connectors.md)

As usual, thank you to some of our awesome community contributors this week: Tyler DeLange, Mario Molina, Rodrigo Parra, Prashanth Patali, Christopher Wu, Itai Admi, Fred Reimer, and Konrad Schlatte!

## 06/10/2021 Summary

* New Destination: [S3!!](../../integrations/destinations/s3.md) 
* New Sources: [Harvest](../../integrations/sources/harvest.md), [Amplitude](../../integrations/sources/amplitude.md), [Posthog](../../integrations/sources/posthog.md)
* 🐛 Ensure that logs from threads created by replication workers are added to the log file.
* 🐛 Handle TINYINT\(1\) and BOOLEAN correctly and fix target file comparison for MySQL CDC.
* Jira source: now supports all available entities in Jira Cloud.
* 📚 Added a troubleshooting section, a gradle cheatsheet, a reminder on what the reset button does, and a refresh on our docs best practices.

#### Connector Development:

* Containerized connector code generator
* Added JDBC source connector bootstrap template.
* Added Java destination generator.

View the full release notes highlights here: [Platform](platform.md), [Connectors](connectors.md)

As usual, thank you to some of our awesome community contributors this week \(I've noticed that we've had more contributors to our docs, which we really appreciate\). Ping, Harshith Mullapudi, Michael Irvine, Matheus di Paula, jacqueskpoty and P.VAD.

## Overview

Airbyte is comprised of 2 parts:

* Platform \(The scheduler, workers, api, web app, and the Airbyte protocol\). Here is the [changelog for Platform](platform.md). 
* Connectors that run in Docker containers. Here is the [changelog for the connectors](connectors.md). 

## Airbyte Platform Releases

### Production v. Dev Releases

The "production" version of Airbyte is the version of the app specified in `.env`. With each production release, we update the version in the `.env` file. This version will always be available for download on DockerHub. It is the version of the app that runs when a user runs `docker compose up`.

The "development" version of Airbyte is the head of master branch. It is the version of the app that runs when a user runs `./gradlew build && 
VERSION=dev docker compose up`.

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

