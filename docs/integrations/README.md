# Connector Catalog

## Connector Release Stages

Airbyte uses a grading system for connectors to help you understand what to expect from a connector:

**Generally Available**: A generally available connector has been deemed ready for use in a production environment and is officially supported by Airbyte. Its documentation is considered sufficient to support widespread adoption.

**Beta**: A beta connector is considered stable and reliable with no backwards incompatible changes but has not been validated by a broader group of users. We expect to find and fix a few issues and bugs in the release before it’s ready for GA.

**Alpha**: An alpha connector signifies a connector under development and helps Airbyte gather early feedback and issues reported by early adopters. We strongly discourage using alpha releases for production use cases and do not offer Cloud Support SLAs around these products, features, or connectors.

For more information about the grading system, see [Product Release Stages](https://docs.airbyte.com/project-overview/product-release-stages)

## Sources

| Connector                                                                                   | Product Release Stage| Available in Cloud? |
|:--------------------------------------------------------------------------------------------| :------------------- | :------------------ |
| [3PL Central](sources/tplcentral.md)                                                        | Alpha                | No                  |
| [Airtable](sources/airtable.md)                                                             | Alpha                | Yes                 |
| [Amazon Ads](sources/amazon-ads.md)                                                         | Beta                 | Yes                 |
| [Amazon Seller Partner](sources/amazon-seller-partner.md)                                   | Alpha                | Yes                 |
| [Amazon SQS](sources/amazon-sqs.md)                                                         | Alpha                | Yes                 |
| [Amplitude](sources/amplitude.md)                                                           | Generally Available  | Yes                 |
| [Apify Dataset](sources/apify-dataset.md)                                                   | Alpha                | Yes                 |
| [Appstore](sources/appstore.md)                                                             | Alpha                | No                  |
| [Asana](sources/asana.md)                                                                   | Alpha                | No                  |
| [AWS CloudTrail](sources/aws-cloudtrail.md)                                                 | Alpha                | Yes                 |
| [Azure Table Storage](sources/azure-table.md)                                               | Alpha                | Yes                 |
| [BambooHR](sources/bamboo-hr.md)                                                            | Alpha                | No                  |
| [Baton](sources/hellobaton.md)                                                              | Alpha                | No                  |
| [BigCommerce](sources/bigcommerce.md)                                                       | Alpha                | Yes                 |
| [BigQuery](sources/bigquery.md)                                                             | Alpha                | Yes                 |
| [Bing Ads](sources/bing-ads.md)                                                             | Generally Available  | Yes                 |
| [Braintree](sources/braintree.md)                                                           | Alpha                | Yes                 |
| [Cart.com](sources/cart.md)                                                                 | Alpha                | No                  |
| [Chargebee](sources/chargebee.md)                                                           | Alpha                | Yes                 |
| [Chargify](sources/chargify.md)                                                             | Alpha                | No                  |
| [Chartmogul](sources/chartmogul.md)                                                         | Alpha                | Yes                 |
| [ClickHouse](sources/clickhouse.md)                                                         | Alpha                | Yes                 |
| [Close.com](sources/close-com.md)                                                           | Alpha                | Yes                 |
| [CockroachDB](sources/cockroachdb.md)                                                       | Alpha                | No                  |
| [Commercetools](sources/commercetools.md)                                                   | Alpha                | No                  |
| [Confluence](sources/confluence.md)                                                         | Alpha                | No                  |
| [Customer.io](sources/customer-io.md)                                                       | Alpha                | No                  |
| [Db2](sources/db2.md)                                                                       | Alpha                | No                  |
| [Delighted](sources/delighted.md)                                                           | Alpha                | Yes                 |
| [Dixa](sources/dixa.md)                                                                     | Alpha                | Yes                 |
| [Dockerhub](sources/dockerhub.md)                                                           | Alpha                | Yes                 |
| [Drift](sources/drift.md)                                                                   | Alpha                | No                  |
| [Drupal](sources/drupal.md)                                                                 | Alpha                | No                  |
| [Elasticsearch](sources/elasticsearch.md)                                                   | Alpha                | No                  |
| [End-to-End Testing](sources/e2e-test.md)                                                   | Alpha                | Yes                 |
| [Exchange Rates API](sources/exchangeratesapi.md)                                           | Alpha                | Yes                 |
| [Facebook Marketing](sources/facebook-marketing.md)                                         | Generally Available  | Yes                 |
| [Facebook Pages](sources/facebook-pages.md)                                                 | Alpha                | No                  |
| [Faker](sources/faker.md)                                                                   | Alpha                | Yes                 |
| [File](sources/file.md)                                                                     | Alpha                | Yes                 |
| [Firebolt](sources/firebolt.md)                                                             | Alpha                | Yes                 |
| [Flexport](sources/flexport.md)                                                             | Alpha                | No                  |
| [Freshdesk](sources/freshdesk.md)                                                           | Alpha                | Yes                 |
| [Freshsales](sources/freshsales.md)                                                         | Alpha                | No                  |
| [Freshservice](sources/freshservice.md)                                                     | Alpha                | No                  |
| [GitHub](sources/github.md)                                                                 | Generally Available  | Yes                 |
| [GitLab](sources/gitlab.md)                                                                 | Alpha                | Yes                 |
| [Glassfrog](sources/glassfrog.md)                                                           | Alpha                | No                  |
| [Google Ads](sources/google-ads.md)                                                         | Generally Available  | Yes                 |
| [Google Analytics (v4)](sources/google-analytics-v4.md)                                     | Alpha                | No                  |
| [Google Analytics (Universal Analytics)](sources/google-analytics-universal-analytics.md)   | Generally Available  | Yes                 |
| [Google Directory](sources/google-directory.md)                                             | Alpha                | Yes                 |
| [Google Search Console](sources/google-search-console.md)                                   | Beta                 | Yes                 |
| [Google Sheets](sources/google-sheets.md)                                                   | Generally Available  | Yes                 |
| [Google Workspace Admin Reports](sources/google-workspace-admin-reports.md)                 | Alpha                | Yes                 |
| [Greenhouse](sources/greenhouse.md)                                                         | Alpha                | Yes                 |
| [Harness](sources/harness.md)                                                               | Alpha                | No                  |
| [Harvest](sources/harvest.md)                                                               | Alpha                | No                  |
| [http-request](sources/http-request.md)                                                     | Alpha                | No                  |
| [HubSpot](sources/hubspot.md)                                                               | Generally Available  | Yes                 |
| [Instagram](sources/instagram.md)                                                           | Generally Available  | Yes                 |
| [Intercom](sources/intercom.md)                                                             | Generally Available  | Yes                 |
| [Iterable](sources/iterable.md)                                                             | Alpha                | Yes                 |
| [Jenkins](sources/jenkins.md)                                                               | Alpha                | No                  |
| [Jira](sources/jira.md)                                                                     | Alpha                | No                  |
| [Kafka](sources/kafka.md)                                                                   | Alpha                | No                  |
| [Klaviyo](sources/klaviyo.md)                                                               | Beta                 | Yes                 |
| [Kustomer](sources/kustomer.md)                                                             | Alpha                | Yes                 |
| [Kyriba](sources/kyriba.md)                                                                 | Alpha                | No                  |
| [Lemlist](sources/lemlist.md)                                                               | Alpha                | Yes                 |
| [Lever](sources/lever-hiring.md)                                                            | Alpha                | No                  |
| [LinkedIn Ads](sources/linkedin-ads.md)                                                     | Generally Available  | Yes                 |
| [LinkedIn Pages](sources/linkedin-pages.md)                                                 | Alpha                | Yes                 |
| [Linnworks](sources/linnworks.md)                                                           | Alpha                | Yes                 |
| [Looker](sources/looker.md)                                                                 | Alpha                | Yes                 |
| [Magento](sources/magento.md)                                                               | Alpha                | No                  |
| [Mailchimp](sources/mailchimp.md)                                                           | Generally Available  | Yes                 |
| [Marketo](sources/marketo.md)                                                               | Alpha                | Yes                 |
| [Metabase](sources/metabase.md)                                                             | Alpha                | Yes                 |
| [Microsoft Dynamics AX](sources/microsoft-dynamics-ax.md)                                   | Alpha                | No                  |
| [Microsoft Dynamics Customer Engagement](sources/microsoft-dynamics-customer-engagement.md) | Alpha                | No                  |
| [Microsoft Dynamics GP](sources/microsoft-dynamics-gp.md)                                   | Alpha                | No                  |
| [Microsoft Dynamics NAV](sources/microsoft-dynamics-nav.md)                                 | Alpha                | No                  |
| [Microsoft SQL Server (MSSQL)](sources/mssql.md)                                            | Alpha                | Yes                 |
| [Microsoft Teams](sources/microsoft-teams.md)                                               | Alpha                | Yes                 |
| [Mixpanel](sources/mixpanel.md)                                                             | Beta                 | Yes                 |
| [Monday](sources/monday.md)                                                                 | Alpha                | Yes                 |
| [Mongo DB](sources/mongodb-v2.md)                                                           | Alpha                | Yes                 |
| [My Hours](sources/my-hours.md)                                                             | Alpha                | Yes                 |
| [MySQL](sources/mysql.md)                                                                   | Alpha                | Yes                 |
| [Notion](sources/notion.md)                                                                 | Beta                 | No                  |
| [Okta](sources/okta.md)                                                                     | Alpha                | Yes                 |
| [OneSignal](sources/onesignal.md)                                                           | Alpha                | No                  |
| [OpenWeather](sources/openweather.md)                                                       | Alpha                | No                  |
| [Oracle DB](sources/oracle.md)                                                              | Alpha                | Yes                 |
| [Oracle PeopleSoft](sources/oracle-peoplesoft.md)                                           | Alpha                | No                  |
| [Oracle Siebel CRM](sources/oracle-siebel-crm.md)                                           | Alpha                | No                  |
| [Orb](sources/orb.md)                                                                       | Alpha                | Yes                 |
| [Orbit](sources/orbit.md)                                                                   | Alpha                | No                  |
| [Outreach](./sources/outreach.md)                                                           | Alpha                | No                  |
| [PagerDuty](sources/pagerduty.md)                                                           | Alpha                | No                  |
| [PayPal Transaction](sources/paypal-transaction.md)                                         | Alpha                | Yes                 |
| [Paystack](sources/paystack.md)                                                             | Alpha                | No                  |
| [PersistIq](sources/persistiq.md)                                                           | Alpha                | Yes                 |
| [Pinterest](sources/pinterest.md)                                                           | Alpha                | No                  |
| [Pipedrive](sources/pipedrive.md)                                                           | Alpha                | No                  |
| [Pivotal Tracker](sources/pivotal-tracker.md)                                               | Alpha                | No                  |
| [Plaid](sources/plaid.md)                                                                   | Alpha                | No                  |
| [PokéAPI](sources/pokeapi.md)                                                               | Alpha                | Yes                 |
| [Postgres](sources/postgres.md)                                                             | Beta                 | Yes                 |
| [PostHog](sources/posthog.md)                                                               | Alpha                | Yes                 |
| [PrestaShop](sources/presta-shop.md)                                                        | Alpha                | Yes                 |
| [Qualaroo](sources/qualaroo.md)                                                             | Alpha                | Yes                 |
| [QuickBooks](sources/quickbooks.md)                                                         | Alpha                | No                  |
| [Recharge](sources/recharge.md)                                                             | Beta                 | Yes                 |
| [Recurly](sources/recurly.md)                                                               | Alpha                | Yes                 |
| [Redshift](sources/redshift.md)                                                             | Alpha                | Yes                 |
| [Retently](sources/retently.md)                                                             | Alpha                | Yes                 |
| [S3](sources/s3.md)                                                                         | Generally Available  | Yes                 |
| [Salesforce](sources/salesforce.md)                                                         | Generally Available  | Yes                 |
| [Salesloft](sources/salesloft.md)                                                           | Alpha                | No                  |
| [SAP Business One](sources/sap-business-one.md)                                             | Alpha                | No                  |
| [SearchMetrics](./sources/search-metrics.md)                                                | Alpha                | No                  |
| [Sendgrid](sources/sendgrid.md)                                                             | Alpha                | Yes                 |
| [Sentry](sources/sentry.md)                                                                 | Alpha                | Yes                 |
| [SFTP](sources/sftp.md)                                                                     | Alpha                | Yes                 |
| [Shopify](sources/shopify.md)                                                               | Alpha                | No                  |
| [Short.io](sources/shortio.md)                                                              | Alpha                | Yes                 |
| [Slack](sources/slack.md)                                                                   | Alpha                | No                  |
| [Smartsheets](sources/smartsheets.md)                                                       | Beta                 | Yes                 |
| [Snapchat Marketing](sources/snapchat-marketing.md)                                         | Beta                 | Yes                 |
| [Snowflake](sources/snowflake.md)                                                           | Alpha                | Yes                 |
| [Spree Commerce](sources/spree-commerce.md)                                                 | Alpha                | No                  |
| [Square](sources/square.md)                                                                 | Alpha                | Yes                 |
| [Strava](sources/strava.md)                                                                 | Alpha                | No                  |
| [Stripe](sources/stripe.md)                                                                 | Generally Available  | Yes                 |
| [Sugar CRM](sources/sugar-crm.md)                                                           | Alpha                | No                  |
| [SurveyMonkey](sources/surveymonkey.md)                                                     | Beta                 | Yes                 |
| [Tempo](sources/tempo.md)                                                                   | Alpha                | Yes                 |
| [TiDB](sources/tidb.md)                                                                     | Alpha                | No                  |
| [TikTok Marketing](./sources/tiktok-marketing.md)                                           | Generally Available  | Yes                 |
| [Trello](sources/trello.md)                                                                 | Alpha                | No                  |
| [Twilio](sources/twilio.md)                                                                 | Alpha                | Yes                 |
| [Typeform](sources/typeform.md)                                                             | Alpha                | Yes                 |
| [US Census](sources/us-census.md)                                                           | Alpha                | Yes                 |
| [VictorOps](sources/victorops.md)                                                           | Alpha                | No                  |
| [Webflow](sources/webflow.md        )                                                       | Alpha                | Yes                 |
| [WooCommerce](sources/woocommerce.md)                                                       | Alpha                | No                  |
| [Wordpress](sources/wordpress.md)                                                           | Alpha                | No                  |
| [YouTube Analytics](sources/youtube-analytics.md)                                           | Alpha                | No                  |
| [Zencart](sources/zencart.md)                                                               | Alpha                | No                  |
| [Zendesk Chat](sources/zendesk-chat.md)                                                     | Alpha                | Yes                 |
| [Zendesk Sunshine](sources/zendesk-sunshine.md)                                             | Alpha                | Yes                 |
| [Zendesk Support](sources/zendesk-support.md)                                               | Generally Available  | Yes                 |
| [Zendesk Talk](sources/zendesk-talk.md)                                                     | Alpha                | No                  |
| [Zenloop](sources/zenloop.md)                                                               | Alpha                | Yes                 |
| [Zoho CRM](sources/zoho-crm.md)                                                             | Alpha                | No                  |
| [Zoom](sources/zoom.md)                                                                     | Alpha                | No                  |
| [Zuora](sources/zuora.md)                                                                   | Alpha                | Yes                 |

## Destinations

| Connector                                                  | Product Release Stage| Available in Cloud? |
|:-----------------------------------------------------------| :------------------- | :------------------ |
| [Amazon SQS](destinations/amazon-sqs.md)                   | Alpha                | Yes                 |
| [Amazon Datalake](destinations/aws-datalake.md)            | Alpha                | No                  |
| [AzureBlobStorage](destinations/azureblobstorage.md)       | Alpha                | Yes                 |
| [BigQuery](destinations/bigquery.md)                       | Generally Available  | Yes                 |
| [Cassandra](destinations/cassandra.md)                     | Alpha                | Yes                 |
| [Chargify (Keen)](destinations/chargify.md)                | Alpha                | Yes                 |
| [ClickHouse](destinations/clickhouse.md)                   | Alpha                | Yes                 |
| [Databricks](destinations/databricks.md)                   | Alpha                | Yes                 |
| [DynamoDB](destinations/dynamodb.md)                       | Alpha                | Yes                 |
| [Elasticsearch](destinations/elasticsearch.md)             | Alpha                | Yes                 |
| [End-to-End Testing](destinations/e2e-test.md)             | Alpha                | Yes                 |
| [Firebolt](destinations/firebolt.md)                       | Alpha                | Yes                 |
| [Google Cloud Storage (GCS)](destinations/gcs.md)          | Beta                 | Yes                 |
| [Google Pubsub](destinations/pubsub.md)                    | Alpha                | Yes                 |
| [Google Sheets](destinations/google-sheets.md)             | Alpha                | Yes                 |
| [Kafka](destinations/kafka.md)                             | Alpha                | No                  |
| [Keen](destinations/keen.md)                               | Alpha                | No                  |
| [Kinesis](destinations/kinesis.md)                         | Alpha                | No                  |
| [Local CSV](destinations/local-csv.md)                     | Alpha                | No                  |
| [Local JSON](destinations/local-json.md)                   | Alpha                | No                  |
| [MariaDB ColumnStore](destinations/mariadb-columnstore.md) | Alpha                | Yes                 |
| [MeiliSearch](destinations/meilisearch.md)                 | Alpha                | Yes                 |
| [MongoDB](destinations/mongodb.md)                         | Alpha                | Yes                 |
| [MQTT](destinations/mqtt.md)                               | Alpha                | Yes                 |
| [MS SQL Server](destinations/mssql.md)                     | Alpha                | Yes                 |
| [MySQL](destinations/mysql.md)                             | Alpha                | Yes                 |
| [Oracle](destinations/oracle.md)                           | Alpha                | Yes                 |
| [Postgres](destinations/postgres.md)                       | Alpha                | Yes                 |
| [Pulsar](destinations/pulsar.md)                           | Alpha                | Yes                 |
| [RabbitMQ](destinations/rabbitmq.md)                       | Alpha                | Yes                 |
| [Redis](destinations/redis.md)                             | Alpha                | Yes                 |
| [Redshift](destinations/redshift.md)                       | Beta                 | Yes                 |
| [Rockset](destinations/rockset.md)                         | Alpha                | Yes                 |
| [S3](destinations/s3.md)                                   | Generally Available  | Yes                 |
| [Scylla](destinations/scylla.md)                           | Alpha                | Yes                 |
| [SFTP JSON](destinations/sftp-json.md)                     | Alpha                | Yes                 |
| [Snowflake](destinations/snowflake.md)                     | Generally Available  | Yes                 |
| [SQLite](destinations/sqlite.md)                           | Alpha                | No                  |
| [Streamr](destinations/streamr.md)                         | Alpha                | No                  |
