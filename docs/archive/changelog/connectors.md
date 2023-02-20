---
description: Do not miss the new connectors we support!
---

# Connectors

**You can request new connectors directly** [**here**](https://github.com/airbytehq/airbyte/issues/new?assignees=&labels=area%2Fintegration%2C+new-integration&template=new-integration-request.md&title=)**.**

Note: Airbyte is not built on top of Singer but is compatible with Singer's protocol. Airbyte's ambitions go beyond what Singer enables us to do, so we are building our own protocol that maintains compatibility with Singer's protocol.

Check out our [connector roadmap](https://github.com/airbytehq/airbyte/projects/3) to see what we're currently working on.

## 1/28/2022

New sources:

- [**Chartmogul**](https://docs.airbyte.io/integrations/sources/chartmogul)
- [**Hellobaton**](https://docs.airbyte.io/integrations/sources/hellobaton)
- [**Flexport**](https://docs.airbyte.io/integrations/sources/flexport)
- [**PersistIq**](https://docs.airbyte.io/integrations/sources/persistiq)

## 1/6/2022

New sources:

- [**3PL Central**](https://docs.airbyte.io/integrations/sources/tplcentral)
- [**My Hours**](https://docs.airbyte.io/integrations/sources/my-hours)
- [**Qualaroo**](https://docs.airbyte.io/integrations/sources/qualaroo)
- [**SearchMetrics**](https://docs.airbyte.io/integrations/sources/search-metrics)

## 12/16/2021

New source:

- [**OpenWeather**](https://docs.airbyte.io/integrations/sources/openweather)

New destinations:

- [**ClickHouse**](https://docs.airbyte.io/integrations/destinations/clickhouse)
- [**RabbitMQ**](https://docs.airbyte.io/integrations/destinations/rabbitmq)
- [**Amazon SQS**](https://docs.airbyte.io/integrations/destinations/amazon-sqs)
- [**Rockset**](https://docs.airbyte.io/integrations/destinations/rockset)

## 12/9/2021

New source:

- [**Mailgun**](https://docs.airbyte.io/integrations/sources/mailgun)

## 12/2/2021

New destinations:

- [**Redis**](https://docs.airbyte.io/integrations/destinations/redis)
- [**MQTT**](https://docs.airbyte.io/integrations/destinations/mqtt)
- [**Google Firestore**](https://docs.airbyte.io/integrations/destinations/google-firestore)
- [**Kinesis**](https://docs.airbyte.io/integrations/destinations/kinesis)

## 11/25/2021

New sources:

- [**Airtable**](https://docs.airbyte.io/integrations/sources/airtable)
- [**Notion**](https://docs.airbyte.io/integrations/sources/notion)
- [**Pardot**](https://docs.airbyte.io/integrations/sources/pardot)
- [**Notion**](https://docs.airbyte.io/integrations/sources/linnworks)
- [**YouTube Analytics**](https://docs.airbyte.io/integrations/sources/youtube-analytics)

New features:

- **Exchange Rates** Source: add `ignore_weekends` option.
- **Facebook** Source: add the videos stream.
- **Freshdesk** Source: removed the limitation in streams pagination.
- **Jira** Source: add option to render fields in HTML format.
- **MongoDB v2** Source: improve read performance.
- **Pipedrive** Source: specify schema for "persons" stream.
- **PostgreSQL** Source: exclude tables on which user doesn't have select privileges.
- **SurveyMonkey** Source: improve connection check.

## 11/17/2021

New destination:

- [**ScyllaDB**](https://docs.airbyte.io/integrations/destinations/scylla)

New sources:

- [**Azure Table Storage**](https://docs.airbyte.io/integrations/sources/azure-table)
- [**Linnworks**](https://docs.airbyte.io/integrations/sources/linnworks)

New features:

- **MySQL** Source: Now has basic performance tests.
- **Salesforce** Source: We now automatically transform and handle incorrect data for the anyType and calculated types.

## 11/11/2021

New destinations:

- [**Cassandra**](https://docs.airbyte.io/integrations/destinations/cassandra)
- [**Pulsar**](https://docs.airbyte.io/integrations/destinations/pulsar)

New sources:

- [**Confluence**](https://docs.airbyte.io/integrations/sources/confluence)
- [**Monday**](https://docs.airbyte.io/integrations/sources/monday)
- [**Commerce Tools**](https://github.com/airbytehq/airbyte/tree/master/airbyte-integrations/connectors/source-commercetools)
- [**Pinterest**](https://docs.airbyte.io/integrations/sources/pinterest)

New features:

- **Shopify** Source: Now supports the FulfillmentOrders and Fulfillments streams.
- **Greenhouse** Source: Now supports the Demographics stream.
- **Recharge** Source: Broken requests should now be re-requested with improved backoff.
- **Stripe** Source: Now supports the checkout_sessions, checkout_sessions_line_item, and promotion_codes streams.
- **Db2** Source: Now supports SSL.

## 11/3/2021

New destination:

- [**Elasticsearch**](https://docs.airbyte.io/integrations/destinations/elasticsearch)

New sources:

- [**Salesloft**](https://docs.airbyte.io/integrations/sources/salesloft)
- [**OneSignal**](https://docs.airbyte.io/integrations/sources/onesignal)
- [**Strava**](https://docs.airbyte.io/integrations/sources/strava)
- [**Lemlist**](https://docs.airbyte.io/integrations/sources/lemlist)
- [**Amazon SQS**](https://docs.airbyte.io/integrations/sources/amazon-sqs)
- [**Freshservices**](https://docs.airbyte.io/integrations/source/freshservices)
- [**Freshsales**](https://docs.airbyte.io/integrations/sources/freshsales)
- [**Appsflyer**](https://github.com/airbytehq/airbyte/tree/master/airbyte-integrations/connectors/source-appsflyer)
- [**Paystack**](https://docs.airbyte.io/integrations/sources/paystack)
- [**Sentry**](https://docs.airbyte.io/integrations/sources/sentry)
- [**Retently**](https://github.com/airbytehq/airbyte/tree/master/airbyte-integrations/connectors/source-retently)
- [**Delighted!**](https://github.com/airbytehq/airbyte/tree/master/airbyte-integrations/connectors/source-delighted)

New features:

- **BigQuery** Destination: You can now run transformations in batches, preventing queries from hitting BigQuery limits. (contributed by @Andrés Bravo)
- **S3** Source: Memory and Performance optimizations, also some fancy new PyArrow CSV configuration options.
- **Zuora** Source: Now supports Unlimited as an option for the Data Query Live API.
- **Clickhouse** Source: Now supports SSL and connection via SSH tunneling.

## 10/20/2021

New source:

- [**WooCommerce**](https://docs.airbyte.io/integrations/sources/woocommerce)

New feature:

- **MSSQL** destination: Now supports basic normalization

## 9/29/2021

New sources:

- [**LinkedIn Ads**](https://docs.airbyte.io/integrations/sources/linkedin-ads)
- [**Kafka**](https://docs.airbyte.io/integrations/sources/kafka)
- [**Lever Hiring**](https://docs.airbyte.io/integrations/sources/lever-hiring)

New features:

- **MySQL** destination: Now supports connection via TLS/SSL
- **BigQuery** (denormalized) destination: Supports reading BigQuery types such as date by reading the format field (contributed by @Nicolas Moreau)
- **Hubspot** source: Added contacts associations to the deals stream.
- **GitHub** source: Now supports pulling commits from user-specified branches.
- **Google Search Console** source: Now accepts admin email as input when using a service account key.
- **Greenhouse** source: Now identifies API streams it has access to if permissions are limited.
- **Marketo** source: Now Airbyte native.
- **S3** source: Now supports any source that conforms to the S3 protocol (Non-AWS S3).
- **Shopify** source: Now reports pre_tax_price on the line_items stream if you have Shopify Plus.
- **Stripe** source: Now actually uses the mandatory start_date config field for incremental syncs.

## 9/16/2021

New destinations:

- [**Databricks**](https://docs.airbyte.io/integrations/destinations/databricks)

New sources:

- [**Close.com**](https://docs.airbyte.io/integrations/sources/close-com)
- [**Google Search Console**](https://docs.airbyte.io/integrations/sources/google-search-console)

New features:

- **Google Ads** source: You can now specify user-specified queries in GAQL.
- **GitHub** source: All streams with a parent stream use cached parent stream data when possible.
- **Shopify** source: Substantial performance improvements to the incremental sync mode.
- **Stripe** source: Now supports the PaymentIntents stream.
- **Pipedrive** source: Now supports the Organizations stream.
- **Sendgrid** source: Now supports the SingleSendStats stream.
- **Bing Ads** source: Now supports the Report stream.
- **GitHub** source: Now supports the Reactions stream.
- **MongoDB** source: Now Airbyte native!

## 9/9/2021

New source:

- [**Facebook Pages**](https://docs.airbyte.io/integrations/sources/facebook-pages)

New destinations:

- [**MongoDB**](https://docs.airbyte.io/integrations/destinations/mongodb)
- [**DynamoDB**](https://docs.airbyte.io/integrations/destinations/dynamodb)

New features:

- **S3** source: Support for Parquet format.
- **Github** source: Branches, repositories, organization users, tags, and pull request stats streams added \(contributed by @Christopher Wu\).
- **BigQuery** destination: Added GCS upload option.
- **Salesforce** source: Now Airbyte native.
- **Redshift** destination: Optimized for performance.

Bug fixes:

- **Pipedrive** source: Output schemas no longer remove timestamp from fields.
- **Github** source: Empty repos and negative backoff values are now handled correctly.
- **Harvest** source: Normalization now works as expected.
- **All CDC sources**: Removed sleep logic which caused exceptions when loading data from high-volume sources.
- **Slack** source: Increased number of retries to tolerate flaky retry wait times on the API side.
- **Slack** source: Sync operations no longer hang indefinitely.
- **Jira** source: Now uses updated time as the cursor field for incremental sync instead of the created time.
- **Intercom** source: Fixed inconsistency between schema and output data.
- **HubSpot** source: Streams with the items property now have their schemas fixed.
- **HubSpot** source: Empty strings are no longer handled as dates, fixing the deals, companies, and contacts streams.
- **Typeform** source: Allows for multiple choices in responses now.
- **Shopify** source: The type for the amount field is now fixed in the schema.
- **Postgres** destination: \u0000\(NULL\) value processing is now fixed.

## 9/1/2021

New sources:

- [**Bamboo HR**](https://docs.airbyte.io/integrations/sources/bamboo-hr)
- [**BigCommerce**](https://docs.airbyte.io/integrations/sources/bigcommerce)
- [**Trello**](https://docs.airbyte.io/integrations/sources/trello)
- [**Google Analytics V4**](https://docs.airbyte.io/integrations/sources/google-analytics-v4)
- [**Amazon Ads**](https://docs.airbyte.io/integrations/sources/google-analytics-v4)

Bug fixes:

- **Shopify** source: Rate limit throttling fixed.

## 8/26/2021

New source:

- [**Short.io**](https://docs.airbyte.io/integrations/sources/shortio)

New features:

- **GitHub** source: Add support for rotating through multiple API tokens.
- **Google Ads** source: Added `UserLocationReport` stream.
- **Cart.com** source: Added the `order_items` stream.

Bug fixes:

- **Postgres** source: Fix out-of-memory issue with CDC interacting with large JSON blobs.
- **Intercom** source: Pagination now works as expected.

## 8/18/2021

New source:

- [**Bing Ads**](https://docs.airbyte.io/integrations/sources/bing-ads)

New destination:

- [**Keen**](https://docs.airbyte.io/integrations/destinations/keen)

New features:

- **Chargebee** source: Adds support for the `items`, `item prices` and `attached items` endpoints.

Bug fixes:

- **QuickBooks** source: Now uses the number data type for decimal fields.
- **HubSpot** source: Fixed `empty string` inside of the `number` and `float` datatypes.
- **GitHub** source: Validation fixed on non-required fields.
- **BigQuery** destination: Now supports processing of arrays of records properly.
- **Oracle** destination: Fixed destination check for users without DBA role.

## 8/9/2021

New sources:

- [**S3/Abstract Files**](https://docs.airbyte.io/integrations/sources/s3)
- [**Zuora**](https://docs.airbyte.io/integrations/sources/zuora)
- [**Kustomer**](https://docs.airbyte.io/integrations/sources/kustomer)
- [**Apify**](https://docs.airbyte.io/integrations/sources/apify-dataset)
- [**Chargebee**](https://docs.airbyte.io/integrations/sources/chargebee)

New features:

- **Shopify** source: The `status` property is now in the `Products` stream.
- **Amazon Seller Partner** source: Added support for `GET_MERCHANT_LISTINGS_ALL_DATA` and `GET_FBA_INVENTORY_AGED_DATA` stream endpoints.
- **GitHub** source: Existing streams now don't minify the `user` property.
- **HubSpot** source: Updated user-defined custom field schema generation.
- **Zendesk** source: Migrated from Singer to the Airbyte CDK.
- **Amazon Seller Partner** source: Migrated to the Airbyte CDK.

Bug fixes:

- **HubSpot** source: Casting exceptions are now logged correctly.
- **S3** source: Fixed bug where syncs could hang indefinitely.
- **Shopify** source: Fixed the `products` schema to be in accordance with the API.
- **PayPal Transactions** source: Fixed the start date minimum to be 3 years rather than 45 days.
- **Google Ads** source: Added the `login-customer-id` setting.
- **Intercom** source: Rate limit corrected from 1000 requests/minute from 1000 requests/hour.
- **S3** source: Fixed bug in spec to properly display the `format` field in the UI.

New CDK features:

- Now allows for setting request data in non-JSON formats.

## 7/30/2021

New sources:

- [**PrestaShop**](https://docs.airbyte.io/integrations/sources/prestashop)
- [**Snapchat Marketing**](https://docs.airbyte.io/integrations/sources/snapchat-marketing)
- [**Drupal**](https://docs.airbyte.io/integrations/sources/drupal)
- [**Magento**](https://docs.airbyte.io/integrations/sources/magento)
- [**Microsoft Dynamics AX**](https://docs.airbyte.io/integrations/sources/microsoft-dynamics-ax)
- [**Microsoft Dynamics Customer Engagement**](https://docs.airbyte.io/integrations/sources/microsoft-dynamics-customer-engagement)
- [**Microsoft Dynamics GP**](https://docs.airbyte.io/integrations/sources/microsoft-dynamics-gp)
- [**Microsoft Dynamics NAV**](https://docs.airbyte.io/integrations/sources/microsoft-dynamics-nav)
- [**Oracle PeopleSoft**](https://docs.airbyte.io/integrations/sources/oracle-peoplesoft)
- [**Oracle Siebel CRM**](https://docs.airbyte.io/integrations/sources/oracle-siebel-crm)
- [**SAP Business One**](https://docs.airbyte.io/integrations/sources/sap-business-one)
- [**Spree Commerce**](https://docs.airbyte.io/integrations/sources/spree-commerce)
- [**Sugar CRM**](https://docs.airbyte.io/integrations/sources/sugar-crm)
- [**WooCommerce**](https://docs.airbyte.io/integrations/sources/woocommerce)
- [**Wordpress**](https://docs.airbyte.io/integrations/sources/wordpress)
- [**Zencart**](https://docs.airbyte.io/integrations/sources/zencart)

Bug fixes:

- **Shopify** source: Fixed the `products` schema to be in accordance with the API.
- **BigQuery** source: No longer fails with `Array of Records` data types.
- **BigQuery** destination: Improved logging, Job IDs are now filled with location and Project IDs.

## 7/23/2021

New sources:

- [**Pipedrive**](https://docs.airbyte.io/integrations/sources/pipedrive)
- [**US Census**](https://docs.airbyte.io/integrations/sources/us-census)
- [**BigQuery**](https://docs.airbyte.io/integrations/sources/bigquery)

New destinations:

- [**Google Cloud Storage**](https://docs.airbyte.io/integrations/destinations/gcs)
- [**Kafka**](https://docs.airbyte.io/integrations/destinations/kafka)

New Features:

- **Java Connectors**: Now have config validators for check, discover, read, and write calls
- **Stripe** source: All subscription types are returnable \(including expired and canceled ones\).
- **Mixpanel** source: Migrated to the CDK.
- **Intercom** source: Migrated to the CDK.
- **Google Ads** source: Now supports the `Campaigns`, `Ads`, `AdGroups`, and `Accounts` streams.

Bug Fixes:

- **Facebook** source: Improved rate limit management
- **Instagram** source: Now supports old format for state and automatically updates it to the new format.
- **Sendgrid** source: Now gracefully handles malformed responses from API.
- **Jira** source: Fixed dbt failing to normalize schema for the labels stream.
- **MySQL** destination: Does not fail anymore with columns that contain JSON data.
- **Slack** source: Now does not fail stream slicing on reading threads.

## 7/16/2021

3 new sources:

- [**Zendesk Sunshine**](https://docs.airbyte.io/integrations/sources/zendesk-sunshine)
- [**Dixa**](https://docs.airbyte.io/integrations/sources/dixa)
- [**Typeform**](https://docs.airbyte.io/integrations/sources/typeform)

New Features:

- **MySQL** destination: Now supports normalization!
- **MSSQL** source: Now supports CDC \(Change Data Capture\).
- **Snowflake** destination: Data coming from Airbyte is now identifiable.
- **GitHub** source: Now handles rate limiting.

Bug Fixes:

- **GitHub** source: Now uses the correct cursor field for the `IssueEvents` stream.
- **Square** source: `send_request` method is no longer broken.

## 7/08/2021

7 new sources:

- [**PayPal Transaction**](https://docs.airbyte.io/integrations/sources/paypal-transaction)
- [**Square**](https://docs.airbyte.io/integrations/sources/square)
- [**SurveyMonkey**](https://docs.airbyte.io/integrations/sources/surveymonkey)
- [**CockroachDB**](https://docs.airbyte.io/integrations/sources/cockroachdb)
- [**Airbyte-native GitLab**](https://docs.airbyte.io/integrations/sources/gitlab)
- [**Airbyte-native GitHub**](https://docs.airbyte.io/integrations/sources/github)
- [**Airbyte-native Twilio**](https://docs.airbyte.io/integrations/sources/twilio)

New Features:

- **S3** destination: Now supports `anyOf`, `oneOf` and `allOf` schema fields.
- **Instagram** source: Migrated to the CDK and has improved error handling.
- **Snowflake** source: Now has comprehensive data type tests.
- **Shopify** source: Change the default stream cursor field to `update_at` where possible.
- **Shopify** source: Add support for draft orders.
- **MySQL** destination: Now supports normalization.

Connector Development:

- **Python CDK**: Now allows setting of network adapter args on outgoing HTTP requests.
- Abstract classes for non-JDBC relational database sources.

Bugfixes:

- **GitHub** source: Fixed issue with `locked` breaking normalization of the pull_request stream.
- **PostgreSQL** source: Fixed decimal handling with CDC.
- **Okta** source: Fix endless loop when syncing data from logs stream.

## 7/01/2021

Bugfixes:

- **Looker** source: Now supports the Run Look stream.
- **Google Adwords**: CI is fixed and new version is published.
- **Slack** source: Now Airbyte native and supports channels, channel members, messages, users, and threads streams.
- **Freshdesk** source: Does not fail after 300 pages anymore.
- **MSSQL** source: Now has comprehensive data type tests.

## 6/24/2021

1 new source:

- [**Db2**](https://docs.airbyte.io/integrations/sources/db2)

New features:

- **S3** destination: supports Avro and Jsonl output!
- **BigQuery** destination: now supports loading JSON data as structured data.
- **Looker** source: Now supports self-hosted instances.
- **Facebook** source: is now migrated to the CDK.

## 6/18/2021

1 new source:

- [**Snowflake**](https://docs.airbyte.io/integrations/sources/snowflake)

New features:

- **Postgres** source: now has comprehensive data type tests.
- **Google Ads** source: now uses the [Google Ads Query Language](https://developers.google.com/google-ads/api/docs/query/overview)!
- **S3** destination: supports Parquet output!
- **S3** destination: supports Minio S3!
- **BigQuery** destination: credentials are now optional.

## 6/10/2021

1 new destination:

- [**S3**](https://docs.airbyte.io/integrations/destinations/s3)

3 new sources:

- [**Harvest**](https://docs.airbyte.io/integrations/sources/harvest)
- [**Amplitude**](https://docs.airbyte.io/integrations/sources/amplitude)
- [**Posthog**](https://docs.airbyte.io/integrations/sources/posthog)

New features:

- **Jira** source: now supports all available entities in Jira Cloud.
- **ExchangeRatesAPI** source: clearer messages around unsupported currencies.
- **MySQL** source: Comprehensive core extension to be more compatible with other JDBC sources.
- **BigQuery** destination: Add dataset location.
- **Shopify** source: Add order risks + new attributes to orders schema for native connector

Bugfixes:

- **MSSQL** destination: fixed handling of unicode symbols.

Connector development updates:

- Containerized connector code generator.
- Added JDBC source connector bootstrap template.
- Added Java destination generator.

## 06/3/2021

2 new sources:

- [**Okta**](https://docs.airbyte.io/integrations/sources/okta)
- [**Amazon Seller Partner**](https://docs.airbyte.io/integrations/sources/amazon-seller-partner)

New features:

- **MySQL CDC** now only polls for 5 minutes if we haven't received any records \([\#3789](https://github.com/airbytehq/airbyte/pull/3789)\)
- **Python CDK** now supports Python 3.7.X \([\#3692](https://github.com/airbytehq/airbyte/pull/3692)\)
- **File** source: now supports Azure Blob Storage \([\#3660](https://github.com/airbytehq/airbyte/pull/3660)\)

Bugfixes:

- **Recurly** source: now uses type `number` instead of `integer` \([\#3769](https://github.com/airbytehq/airbyte/pull/3769)\)
- **Stripe** source: fix types in schema \([\#3744](https://github.com/airbytehq/airbyte/pull/3744)\)
- **Stripe** source: output `number` instead of `int` \([\#3728](https://github.com/airbytehq/airbyte/pull/3728)\)
- **MSSQL** destination: fix issue with unicode symbols handling \([\#3671](https://github.com/airbytehq/airbyte/pull/3671)\)

## 05/25/2021

4 new sources:

- [**Asana**](https://docs.airbyte.io/integrations/sources/asana)
- [**Klaviyo**](https://docs.airbyte.io/integrations/sources/klaviyo)
- [**Recharge**](https://docs.airbyte.io/integrations/sources/recharge)
- [**Tempo**](https://docs.airbyte.io/integrations/sources/tempo)

Progress on connectors:

- **CDC for MySQL** is now available!
- **Sendgrid** source: support incremental sync, as rewritten using HTTP CDK \([\#3445](https://github.com/airbytehq/airbyte/pull/3445)\)
- **Github** source bugfix: exception when parsing null date values, use `created_at` as cursor value for issue_milestones \([\#3314](https://github.com/airbytehq/airbyte/pull/3314)\)
- **Slack** source bugfix: don't overwrite thread_ts in threads stream \([\#3483](https://github.com/airbytehq/airbyte/pull/3483)\)
- **Facebook Marketing** source: allow configuring insights lookback window \([\#3396](https://github.com/airbytehq/airbyte/pull/3396)\)
- **Freshdesk** source: fix discovery \([\#3591](https://github.com/airbytehq/airbyte/pull/3591)\)

## 05/18/2021

1 new destination: [**MSSQL**](https://docs.airbyte.io/integrations/destinations/mssql)

1 new source: [**ClickHouse**](https://docs.airbyte.io/integrations/sources/clickhouse)

Progress on connectors:

- **Shopify**: make this source more resilient to timeouts \([\#3409](https://github.com/airbytehq/airbyte/pull/3409)\)
- **Freshdesk** bugfix: output correct schema for various streams \([\#3376](https://github.com/airbytehq/airbyte/pull/3376)\)
- **Iterable**: update to use latest version of CDK \([\#3378](https://github.com/airbytehq/airbyte/pull/3378)\)

## 05/11/2021

1 new destination: [**MySQL**](https://docs.airbyte.io/integrations/destinations/mysql)

2 new sources:

- [**Google Search Console**](https://docs.airbyte.io/integrations/sources/google-search-console)
- [**PokeAPI**](https://docs.airbyte.io/integrations/sources/pokeapi) \(talking about long tail and having fun ;\)\)

Progress on connectors:

- **Zoom**: bugfix on declaring correct types to match data coming from API \([\#3159](https://github.com/airbytehq/airbyte/pull/3159)\), thanks to [vovavovavovavova](https://github.com/vovavovavovavova)
- **Smartsheets**: bugfix on gracefully handling empty cell values \([\#3337](https://github.com/airbytehq/airbyte/pull/3337)\), thanks to [Nathan Nowack](https://github.com/zzstoatzz)
- **Stripe**: fix date property name, only add connected account header when set, and set primary key \(\#3210\), thanks to [Nathan Yergler](https://github.com/nyergler)

## 05/04/2021

2 new sources:

- [**Smartsheets**](https://docs.airbyte.io/integrations/sources/smartsheets), thanks to [Nathan Nowack](https://github.com/zzstoatzz)
- [**Zendesk Chat**](https://docs.airbyte.io/integrations/sources/zendesk-chat)

Progress on connectors:

- **Appstore**: bugfix private key handling in the UI \([\#3201](https://github.com/airbytehq/airbyte/pull/3201)\)
- **Facebook marketing**: Wait longer \(5 min\) for async jobs to start \([\#3116](https://github.com/airbytehq/airbyte/pull/3116)\), thanks to [Max Krog](https://github.com/MaxKrog)
- **Stripe**: support reading data from connected accounts \(\#3121\), and 2 new streams with Refunds & Bank Accounts \([\#3030](https://github.com/airbytehq/airbyte/pull/3030)\) \([\#3086](https://github.com/airbytehq/airbyte/pull/3086)\)
- **Redshift destination**: Ignore records that are too big \(instead of failing\) \([\#2988](https://github.com/airbytehq/airbyte/pull/2988)\)
- **MongoDB**: add supporting TLS and Replica Sets \([\#3111](https://github.com/airbytehq/airbyte/pull/3111)\)
- **HTTP sources**: bugfix on handling array responses gracefully \([\#3008](https://github.com/airbytehq/airbyte/pull/3008)\)

## 04/27/2021

- **Zendesk Talk**: fix normalization failure \([\#3022](https://github.com/airbytehq/airbyte/pull/3022)\), thanks to [yevhenii-ldv](https://github.com/yevhenii-ldv)
- **Github**: pull_requests stream only incremental syncs \([\#2886](https://github.com/airbytehq/airbyte/pull/2886)\) \([\#3009](https://github.com/airbytehq/airbyte/pull/3009)\), thanks to [Zirochkaa](https://github.com/Zirochkaa)
- Create streaming writes to a file and manage the issuance of copy commands for the destination \([\#2921](https://github.com/airbytehq/airbyte/pull/2921)\)
- **Redshift**: make Redshift part size configurable. \([\#3053](https://github.com/airbytehq/airbyte/pull/23053)\)
- **HubSpot**: fix argument error in log call \(\#3087\) \([\#3087](https://github.com/airbytehq/airbyte/pull/3087)\) , thanks to [Nathan Yergler](https://github.com/nyergler)

## 04/20/2021

3 new source connectors!

- [**Zendesk Talk**](https://docs.airbyte.io/integrations/sources/zendesk-talk)
- [**Iterable**](https://docs.airbyte.io/integrations/sources/iterable)
- [**QuickBooks**](https://docs.airbyte.io/integrations/sources/quickbooks-singer)

Other progress on connectors:

- **Postgres source/destination**: add SSL option, thanks to [Marcos Marx](https://github.com/marcosmarxm) \([\#2757](https://github.com/airbytehq/airbyte/pull/2757)\)
- **Google sheets bugfix**: handle duplicate sheet headers, thanks to [Aneesh Makala](https://github.com/makalaaneesh) \([\#2905](https://github.com/airbytehq/airbyte/pull/2905)\)
- **Source Google Adwords**: support specifying the lookback window for conversions, thanks to [Harshith Mullapudi](https://github.com/harshithmullapudi) \([\#2918](https://github.com/airbytehq/airbyte/pull/2918)\)
- **MongoDB improvement**: speed up mongodb schema discovery, thanks to [Yury Koleda](https://github.com/FUT) \([\#2851](https://github.com/airbytehq/airbyte/pull/2851)\)
- **MySQL bugfix**: parsing Mysql jdbc params, thanks to [Vasily Safronov](https://github.com/gingeard) \([\#2891](https://github.com/airbytehq/airbyte/pull/2891)\)
- **CSV bugfix**: discovery takes too much memory \([\#2089](https://github.com/airbytehq/airbyte/pull/2851)\)
- A lot of work was done on improving the standard tests for the connectors, for better standardization and maintenance!

## 04/13/2021

- New connector: [**Oracle DB**](https://docs.airbyte.io/integrations/sources/oracle), thanks to [Marcos Marx](https://github.com/marcosmarxm)

## 04/07/2021

- New connector: [**Google Workspace Admin Reports**](https://docs.airbyte.io/integrations/sources/google-workspace-admin-reports) \(audit logs\)
- Bugfix in the base python connector library that caused errors to be silently skipped rather than failing the sync
- **Exchangeratesapi.io** bugfix: to point to the updated API URL
- **Redshift destination** bugfix: quote keywords “DATETIME” and “TIME” when used as identifiers
- **GitHub** bugfix: syncs failing when a personal repository doesn’t contain collaborators or team streams available
- **Mixpanel** connector: sync at most the last 90 days of data in the annotations stream to adhere to API limits

## 03/29/2021

- We started measuring throughput of connectors. This will help us improve that point for all connectors.
- **Redshift**: implemented Copy strategy to improve its throughput.
- **Instagram**: bugfix an issue which caused media and media_insights streams to stop syncing prematurely.
- Support NCHAR and NVCHAR types in SQL-based database sources.
- Add the ability to specify a custom JDBC parameters for the MySQL source connector.

## 03/22/2021

- 2 new source connectors: [**Gitlab**](https://docs.airbyte.io/integrations/sources/gitlab) and [**Airbyte-native HubSpot**](https://docs.airbyte.io/integrations/sources/hubspot)
- Developing connectors now requires almost no interaction with Gradle, Airbyte’s monorepo build tool. If you’re building a Python connector, you never have to worry about developing outside your typical flow. See [the updated documentation](https://docs.airbyte.io/connector-development).

## 03/15/2021

- 2 new source connectors: [**Instagram**](https://docs.airbyte.io/integrations/sources/instagram) and [**Google Directory**](https://docs.airbyte.io/integrations/sources/google-directory)
- **Facebook Marketing**: support of API v10
- **Google Analytics**: support incremental sync
- **Jira**: bug fix to consistently pull all tickets
- **HTTP Source**: bug fix to correctly parse JSON responses consistently

## 03/08/2021

- 1 new source connector: **MongoDB**
- **Google Analytics**: Support chunked syncs to avoid sampling
- **AppStore**: fix bug where the catalog was displayed incorrectly

## 03/01/2021

- **New native HubSpot connector** with schema folder populated
- Facebook Marketing connector: add option to include deleted records

## 02/22/2021

- Bug fixes:
  - **Google Analytics:** add the ability to sync custom reports
  - **Apple Appstore:** bug fix to correctly run incremental syncs
  - **Exchange rates:** UI now correctly validates input date pattern
  - **File Source:** Support JSONL \(newline-delimited JSON\) format
  - **Freshdesk:** Enable controlling how many requests per minute the connector makes to avoid overclocking rate limits

## 02/15/2021

- 1 new destination connector: [MeiliSearch](https://docs.airbyte.io/integrations/destinations/meilisearch)
- 2 new sources that support incremental append: [Freshdesk](https://docs.airbyte.io/integrations/sources/freshdesk) and [Sendgrid](https://docs.airbyte.io/integrations/sources/sendgrid)
- Other fixes:
  - Thanks to [@ns-admetrics](https://github.com/ns-admetrics) for contributing an upgrade to the **Shopify** source connector which now provides the landing_site field containing UTM parameters in the Orders table.
  - **Sendgrid** source connector supports most available endpoints available in the API
  - **Facebook** Source connector now supports syncing Ad Insights data
  - **Freshdesk** source connector now supports syncing satisfaction ratings and conversations
  - **Microsoft Teams** source connector now gracefully handles rate limiting
  - Bug fix in **Slack** source where the last few records in a sync were sporadically dropped
  - Bug fix in **Google Analytics** source where the last few records in sync were sporadically dropped
  - In **Redshift source**, support non alpha-numeric table names
  - Bug fix in **Github Source** to fix instances where syncs didn’t always fail if there was an error while reading data from the API

## 02/02/2021

- Sources that we improved reliability for \(and that became “certified”\):
  - [Certified sources](https://docs.airbyte.io/integrations): Files and Shopify
  - Enhanced continuous testing for Tempo and Looker sources
- Other fixes / features:
  - Correctly handle boolean types in the File Source
  - Add docs for [App Store](https://docs.airbyte.io/integrations/sources/appstore) source
  - Fix a bug in Snowflake destination where the connector didn’t check for all needed write permissions, causing some syncs to fail

## 01/26/2021

- Improved reliability with our best practices on : Google Sheets, Google Ads, Marketo, Tempo
- Support incremental for Facebook and Google Ads
- The Facebook connector now supports the FB marketing API v9

## 01/19/2021

- **Our new** [**Connector Health Grade**](../../integrations/) **page**
- **1 new source:** App Store \(thanks to [@Muriloo](https://github.com/Muriloo)\)
- Fixes on connectors:
  - Bug fix writing boolean columns to Redshift
  - Bug fix where getting a connector’s input configuration hung indefinitely
  - Stripe connector now gracefully handles rate limiting from the Stripe API

## 01/12/2021

- **1 new source:** Tempo \(thanks to [@thomasvl](https://github.com/thomasvl)\)
- **Incremental support for 3 new source connectors:** [Salesforce](../../integrations/sources/salesforce.md), [Slack](../../integrations/sources/slack.md) and [Braintree](../../integrations/sources/braintree.md)
- Fixes on connectors:
  - Fix a bug in MSSQL and Redshift source connectors where custom SQL types weren't being handled correctly.
  - Improvement of the Snowflake connector from [@hudsondba](https://github.com/hudsondba) \(batch size and timeout sync\)

## 01/05/2021

- **Incremental support for 2 new source connectors:** [Mixpanel](../../integrations/sources/mixpanel.md) and [HubSpot](../../integrations/sources/hubspot.md)
- Fixes on connectors:
  - Fixed a bug in the github connector where the connector didn’t verify the provided API token was granted the correct permissions
  - Fixed a bug in the Google sheets connector where rate limits were not always respected
  - Alpha version of Facebook marketing API v9. This connector is a native Airbyte connector \(current is Singer based\).

## 12/30/2020

**New sources:** [Plaid](../../integrations/sources/plaid.md) \(contributed by [tgiardina](https://github.com/tgiardina)\), [Looker](../../integrations/sources/looker.md)

## 12/18/2020

**New sources:** [Drift](../../integrations/sources/drift.md), [Microsoft Teams](../../integrations/sources/microsoft-teams.md)

## 12/10/2020

**New sources:** [Intercom](../../integrations/sources/intercom.md), [Mixpanel](../../integrations/sources/mixpanel.md), [Jira Cloud](../../integrations/sources/jira.md), [Zoom](../../integrations/sources/zoom.md)

## 12/07/2020

**New sources:** [Slack](../../integrations/sources/slack.md), [Braintree](../../integrations/sources/braintree.md), [Zendesk Support](../../integrations/sources/zendesk-support.md)

## 12/04/2020

**New sources:** [Redshift](../../integrations/sources/redshift.md), [Greenhouse](../../integrations/sources/greenhouse.md) **New destination:** [Redshift](../../integrations/destinations/redshift.md)

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

**New sources:** [Facebook Ads](connectors.md), [Google Ads](../../integrations/sources/google-ads.md), [Marketo](../../integrations/sources/marketo.md) **New destination:** [Snowflake](../../integrations/destinations/snowflake.md)

## 10/30/2020

**New sources:** [Salesforce](../../integrations/sources/salesforce.md), Google Analytics, [HubSpot](../../integrations/sources/hubspot.md), [GitHub](../../integrations/sources/github.md), [Google Sheets](../../integrations/sources/google-sheets.md), [Rest APIs](connectors.md), and [MySQL](../../integrations/sources/mysql.md)

## 10/21/2020

**New destinations:** we built our own connectors for [BigQuery](../../integrations/destinations/bigquery.md) and [Postgres](../../integrations/destinations/postgres.md), to ensure they are of the highest quality.

## 09/23/2020

**New sources:** [Stripe](../../integrations/sources/stripe.md), [Postgres](../../integrations/sources/postgres.md) **New destinations:** [BigQuery](../../integrations/destinations/bigquery.md), [Postgres](../../integrations/destinations/postgres.md), [local CSV](../../integrations/destinations/local-csv.md)
