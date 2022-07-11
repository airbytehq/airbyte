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
| [3PL Central](01-sources/tplcentral.md)                                                        | Alpha                | No                  |
| [Airtable](01-sources/airtable.md)                                                             | Alpha                | Yes                 |
| [Amazon Ads](01-sources/amazon-ads.md)                                                         | Beta                 | Yes                 |
| [Amazon Seller Partner](01-sources/amazon-seller-partner.md)                                   | Alpha                | Yes                 |
| [Amazon SQS](01-sources/amazon-sqs.md)                                                         | Alpha                | Yes                 |
| [Amplitude](01-sources/amplitude.md)                                                           | Generally Available  | Yes                 |
| [Apify Dataset](01-sources/apify-dataset.md)                                                   | Alpha                | Yes                 |
| [Appstore](01-sources/appstore.md)                                                             | Alpha                | No                  |
| [Asana](01-sources/asana.md)                                                                   | Alpha                | No                  |
| [AWS CloudTrail](01-sources/aws-cloudtrail.md)                                                 | Alpha                | Yes                 |
| [Azure Table Storage](01-sources/azure-table.md)                                               | Alpha                | Yes                 |
| [BambooHR](01-sources/bamboo-hr.md)                                                            | Alpha                | No                  |
| [Baton](01-sources/hellobaton.md)                                                              | Alpha                | No                  |
| [BigCommerce](01-sources/bigcommerce.md)                                                       | Alpha                | Yes                 |
| [BigQuery](01-sources/bigquery.md)                                                             | Alpha                | Yes                 |
| [Bing Ads](01-sources/bing-ads.md)                                                             | Generally Available  | Yes                 |
| [Braintree](01-sources/braintree.md)                                                           | Alpha                | Yes                 |
| [Cart.com](01-sources/cart.md)                                                                 | Alpha                | No                  |
| [Chargebee](01-sources/chargebee.md)                                                           | Alpha                | Yes                 |
| [Chargify](01-sources/chargify.md)                                                             | Alpha                | No                  |
| [Chartmogul](01-sources/chartmogul.md)                                                         | Alpha                | Yes                 |
| [ClickHouse](01-sources/clickhouse.md)                                                         | Alpha                | Yes                 |
| [Close.com](01-sources/close-com.md)                                                           | Alpha                | Yes                 |
| [CockroachDB](01-sources/cockroachdb.md)                                                       | Alpha                | No                  |
| [Commercetools](01-sources/commercetools.md)                                                   | Alpha                | No                  |
| [Confluence](01-sources/confluence.md)                                                         | Alpha                | No                  |
| [Customer.io](01-sources/customer-io.md)                                                       | Alpha                | No                  |
| [Db2](01-sources/db2.md)                                                                       | Alpha                | No                  |
| [Delighted](01-sources/delighted.md)                                                           | Alpha                | Yes                 |
| [Dixa](01-sources/dixa.md)                                                                     | Alpha                | Yes                 |
| [Dockerhub](01-sources/dockerhub.md)                                                           | Alpha                | Yes                 |
| [Drift](01-sources/drift.md)                                                                   | Alpha                | No                  |
| [Drupal](01-sources/drupal.md)                                                                 | Alpha                | No                  |
| [End-to-End Testing](01-sources/e2e-test.md)                                                   | Alpha                | Yes                 |
| [Exchange Rates API](01-sources/exchangeratesapi.md)                                           | Alpha                | Yes                 |
| [Facebook Marketing](01-sources/facebook-marketing.md)                                         | Generally Available  | Yes                 |
| [Facebook Pages](01-sources/facebook-pages.md)                                                 | Alpha                | No                  |
| [Faker](01-sources/faker.md)                                                                   | Alpha                | Yes                 |
| [File](01-sources/file.md)                                                                     | Alpha                | Yes                 |
| [Firebolt](01-sources/firebolt.md)                                                             | Alpha                | Yes                 |
| [Flexport](01-sources/flexport.md)                                                             | Alpha                | No                  |
| [Freshdesk](01-sources/freshdesk.md)                                                           | Alpha                | Yes                 |
| [Freshsales](01-sources/freshsales.md)                                                         | Alpha                | No                  |
| [Freshservice](01-sources/freshservice.md)                                                     | Alpha                | No                  |
| [GitHub](01-sources/github.md)                                                                 | Generally Available  | Yes                 |
| [GitLab](01-sources/gitlab.md)                                                                 | Alpha                | Yes                 |
| [Google Ads](01-sources/google-ads.md)                                                         | Generally Available  | Yes                 |
| [Google Analytics (v4)](01-sources/google-analytics-v4.md)                                     | Alpha                | No                  |
| [Google Analytics (Universal Analytics)](01-sources/google-analytics-universal-analytics.md)   | Generally Available  | Yes                 |
| [Google Directory](01-sources/google-directory.md)                                             | Alpha                | Yes                 |
| [Google Search Console](01-sources/google-search-console.md)                                   | Beta                 | Yes                 |
| [Google Sheets](01-sources/google-sheets.md)                                                   | Generally Available  | Yes                 |
| [Google Workspace Admin Reports](01-sources/google-workspace-admin-reports.md)                 | Alpha                | Yes                 |
| [Greenhouse](01-sources/greenhouse.md)                                                         | Alpha                | Yes                 |
| [Harness](01-sources/harness.md)                                                               | Alpha                | No                  |
| [Harvest](01-sources/harvest.md)                                                               | Alpha                | No                  |
| [http-request](01-sources/http-request.md)                                                     | Alpha                | No                  |
| [HubSpot](01-sources/hubspot.md)                                                               | Generally Available  | Yes                 |
| [Instagram](01-sources/instagram.md)                                                           | Generally Available  | Yes                 |
| [Intercom](01-sources/intercom.md)                                                             | Generally Available  | Yes                 |
| [Iterable](01-sources/iterable.md)                                                             | Alpha                | Yes                 |
| [Jenkins](01-sources/jenkins.md)                                                               | Alpha                | No                  |
| [Jira](01-sources/jira.md)                                                                     | Alpha                | No                  |
| [Kafka](01-sources/kafka.md)                                                                   | Alpha                | No                  |
| [Klaviyo](01-sources/klaviyo.md)                                                               | Alpha                | Yes                 |
| [Kustomer](01-sources/kustomer.md)                                                             | Alpha                | Yes                 |
| [Lemlist](01-sources/lemlist.md)                                                               | Alpha                | Yes                 |
| [Lever](01-sources/lever-hiring.md)                                                            | Alpha                | No                  |
| [LinkedIn Ads](01-sources/linkedin-ads.md)                                                     | Generally Available  | Yes                 |
| [Linnworks](01-sources/linnworks.md)                                                           | Alpha                | Yes                 |
| [Looker](01-sources/looker.md)                                                                 | Alpha                | Yes                 |
| [Magento](01-sources/magento.md)                                                               | Alpha                | No                  |
| [Mailchimp](01-sources/mailchimp.md)                                                           | Generally Available  | Yes                 |
| [Marketo](01-sources/marketo.md)                                                               | Alpha                | Yes                 |
| [Metabase](01-sources/metabase.md)                                                             | Alpha                | Yes                 |
| [Microsoft Dynamics AX](01-sources/microsoft-dynamics-ax.md)                                   | Alpha                | No                  |
| [Microsoft Dynamics Customer Engagement](01-sources/microsoft-dynamics-customer-engagement.md) | Alpha                | No                  |
| [Microsoft Dynamics GP](01-sources/microsoft-dynamics-gp.md)                                   | Alpha                | No                  |
| [Microsoft Dynamics NAV](01-sources/microsoft-dynamics-nav.md)                                 | Alpha                | No                  |
| [Microsoft SQL Server (MSSQL)](01-sources/mssql.md)                                            | Alpha                | Yes                 |
| [Microsoft Teams](01-sources/microsoft-teams.md)                                               | Alpha                | Yes                 |
| [Mixpanel](01-sources/mixpanel.md)                                                             | Beta                 | Yes                 |
| [Monday](01-sources/monday.md)                                                                 | Alpha                | Yes                 |
| [Mongo DB](01-sources/mongodb-v2.md)                                                           | Alpha                | Yes                 |
| [My Hours](01-sources/my-hours.md)                                                             | Alpha                | Yes                 |
| [MySQL](01-sources/mysql.md)                                                                   | Alpha                | Yes                 |
| [Notion](01-sources/notion.md)                                                                 | Alpha                | No                  |
| [Okta](01-sources/okta.md)                                                                     | Alpha                | Yes                 |
| [OneSignal](01-sources/onesignal.md)                                                           | Alpha                | No                  |
| [OpenWeather](01-sources/openweather.md)                                                       | Alpha                | No                  |
| [Oracle DB](01-sources/oracle.md)                                                              | Alpha                | Yes                 |
| [Oracle PeopleSoft](01-sources/oracle-peoplesoft.md)                                           | Alpha                | No                  |
| [Oracle Siebel CRM](01-sources/oracle-siebel-crm.md)                                           | Alpha                | No                  |
| [Orb](01-sources/orb.md)                                                                       | Alpha                | Yes                 |
| [Outreach](./01-sources/outreach.md)                                                           | Alpha                | No                  |
| [PagerDuty](01-sources/pagerduty.md)                                                           | Alpha                | No                  |
| [PayPal Transaction](01-sources/paypal-transaction.md)                                         | Alpha                | No                  |
| [Paystack](01-sources/paystack.md)                                                             | Alpha                | No                  |
| [PersistIq](01-sources/persistiq.md)                                                           | Alpha                | Yes                 |
| [Pinterest](01-sources/pinterest.md)                                                           | Alpha                | No                  |
| [Pipedrive](01-sources/pipedrive.md)                                                           | Alpha                | No                  |
| [Pivotal Tracker](01-sources/pivotal-tracker.md)                                               | Alpha                | No                  |
| [Plaid](01-sources/plaid.md)                                                                   | Alpha                | No                  |
| [PokéAPI](01-sources/pokeapi.md)                                                               | Alpha                | Yes                 |
| [Postgres](01-sources/postgres.md)                                                             | Beta                 | Yes                 |
| [PostHog](01-sources/posthog.md)                                                               | Alpha                | Yes                 |
| [PrestaShop](01-sources/presta-shop.md)                                                        | Alpha                | Yes                 |
| [Qualaroo](01-sources/qualaroo.md)                                                             | Alpha                | Yes                 |
| [QuickBooks](01-sources/quickbooks.md)                                                         | Alpha                | No                  |
| [Recharge](01-sources/recharge.md)                                                             | Alpha                | Yes                 |
| [Recurly](01-sources/recurly.md)                                                               | Alpha                | Yes                 |
| [Redshift](01-sources/redshift.md)                                                             | Alpha                | Yes                 |
| [Retently](01-sources/retently.md)                                                             | Alpha                | Yes                 |
| [S3](01-sources/s3.md)                                                                         | Beta                 | Yes                 |
| [Salesforce](01-sources/salesforce.md)                                                         | Generally Available  | Yes                 |
| [Salesloft](01-sources/salesloft.md)                                                           | Alpha                | No                  |
| [SAP Business One](01-sources/sap-business-one.md)                                             | Alpha                | No                  |
| [SearchMetrics](./01-sources/search-metrics.md)                                                | Alpha                | No                  |
| [Sendgrid](01-sources/sendgrid.md)                                                             | Alpha                | Yes                 |
| [Sentry](01-sources/sentry.md)                                                                 | Alpha                | Yes                 |
| [SFTP](01-sources/sftp.md)                                                                     | Alpha                | Yes                 |
| [Shopify](01-sources/shopify.md)                                                               | Alpha                | No                  |
| [Short.io](01-sources/shortio.md)                                                              | Alpha                | Yes                 |
| [Slack](01-sources/slack.md)                                                                   | Alpha                | No                  |
| [Smartsheets](01-sources/smartsheets.md)                                                       | Beta                 | Yes                 |
| [Snapchat Marketing](01-sources/snapchat-marketing.md)                                         | Alpha                | Yes                 |
| [Snowflake](01-sources/snowflake.md)                                                           | Alpha                | Yes                 |
| [Spree Commerce](01-sources/spree-commerce.md)                                                 | Alpha                | No                  |
| [Square](01-sources/square.md)                                                                 | Alpha                | Yes                 |
| [Strava](01-sources/strava.md)                                                                 | Alpha                | No                  |
| [Stripe](01-sources/stripe.md)                                                                 | Generally Available  | Yes                 |
| [Sugar CRM](01-sources/sugar-crm.md)                                                           | Alpha                | No                  |
| [SurveyMonkey](01-sources/surveymonkey.md)                                                     | Alpha                | No                  |
| [Tempo](01-sources/tempo.md)                                                                   | Alpha                | Yes                 |
| [TiDB](01-sources/tidb.md)                                                                     | Alpha                | No                  |
| [TikTok Marketing](./01-sources/tiktok-marketing.md)                                           | Generally Available  | Yes                 |
| [Trello](01-sources/trello.md)                                                                 | Alpha                | No                  |
| [Twilio](01-sources/twilio.md)                                                                 | Alpha                | Yes                 |
| [Typeform](01-sources/typeform.md)                                                             | Alpha                | Yes                 |
| [US Census](01-sources/us-census.md)                                                           | Alpha                | Yes                 |
| [VictorOps](01-sources/victorops.md)                                                           | Alpha                | No                  |
| [Webflow](01-sources/webflow.md        )                                                       | Alpha                | Yes                 |
| [WooCommerce](01-sources/woocommerce.md)                                                       | Alpha                | No                  |
| [Wordpress](01-sources/wordpress.md)                                                           | Alpha                | No                  |
| [YouTube Analytics](01-sources/youtube-analytics.md)                                           | Alpha                | No                  |
| [Zencart](01-sources/zencart.md)                                                               | Alpha                | No                  |
| [Zendesk Chat](01-sources/zendesk-chat.md)                                                     | Alpha                | Yes                 |
| [Zendesk Sunshine](01-sources/zendesk-sunshine.md)                                             | Alpha                | Yes                 |
| [Zendesk Support](01-sources/zendesk-support.md)                                               | Generally Available  | Yes                 |
| [Zendesk Talk](01-sources/zendesk-talk.md)                                                     | Alpha                | No                  |
| [Zenloop](01-sources/zenloop.md)                                                               | Alpha                | Yes                 |
| [Zoho CRM](01-sources/zoho-crm.md)                                                             | Alpha                | No                  |
| [Zoom](01-sources/zoom.md)                                                                     | Alpha                | No                  |
| [Zuora](01-sources/zuora.md)                                                                   | Alpha                | Yes                 |

## Destinations

| Connector                                                  | Product Release Stage| Available in Cloud? |
|:-----------------------------------------------------------| :------------------- | :------------------ |
| [Amazon SQS](02-destinations/amazon-sqs.md)                   | Alpha                | Yes                 |
| [Amazon Datalake](02-destinations/aws-datalake.md)            | Alpha                | No                  |
| [AzureBlobStorage](02-destinations/azureblobstorage.md)       | Alpha                | Yes                 |
| [BigQuery](02-destinations/bigquery.md)                       | Generally Available  | Yes                 |
| [Cassandra](02-destinations/cassandra.md)                     | Alpha                | Yes                 |
| [Chargify (Keen)](02-destinations/chargify.md)                | Alpha                | Yes                 |
| [ClickHouse](02-destinations/clickhouse.md)                   | Alpha                | Yes                 |
| [Databricks](02-destinations/databricks.md)                   | Alpha                | Yes                 |
| [DynamoDB](02-destinations/dynamodb.md)                       | Alpha                | Yes                 |
| [Elasticsearch](02-destinations/elasticsearch.md)             | Alpha                | Yes                 |
| [End-to-End Testing](02-destinations/e2e-test.md)             | Alpha                | Yes                 |
| [Firebolt](02-destinations/firebolt.md)                       | Alpha                | Yes                 |
| [Google Cloud Storage (GCS)](02-destinations/gcs.md)          | Beta                 | Yes                 |
| [Google Pubsub](02-destinations/pubsub.md)                    | Alpha                | Yes                 |
| [Google Sheets](02-destinations/google-sheets.md)             | Alpha                | Yes                 |
| [Kafka](02-destinations/kafka.md)                             | Alpha                | No                  |
| [Keen](02-destinations/keen.md)                               | Alpha                | No                  |
| [Kinesis](02-destinations/kinesis.md)                         | Alpha                | No                  |
| [Local CSV](02-destinations/local-csv.md)                     | Alpha                | No                  |
| [Local JSON](02-destinations/local-json.md)                   | Alpha                | No                  |
| [MariaDB ColumnStore](02-destinations/mariadb-columnstore.md) | Alpha                | Yes                 |
| [MeiliSearch](02-destinations/meilisearch.md)                 | Alpha                | Yes                 |
| [MongoDB](02-destinations/mongodb.md)                         | Alpha                | Yes                 |
| [MQTT](02-destinations/mqtt.md)                               | Alpha                | Yes                 |
| [MS SQL Server](02-destinations/mssql.md)                     | Alpha                | Yes                 |
| [MySQL](02-destinations/mysql.md)                             | Alpha                | Yes                 |
| [Oracle](02-destinations/oracle.md)                           | Alpha                | Yes                 |
| [Postgres](02-destinations/postgres.md)                       | Alpha                | Yes                 |
| [Pulsar](02-destinations/pulsar.md)                           | Alpha                | Yes                 |
| [RabbitMQ](02-destinations/rabbitmq.md)                       | Alpha                | Yes                 |
| [Redis](02-destinations/redis.md)                             | Alpha                | Yes                 |
| [Redshift](02-destinations/redshift.md)                       | Beta                 | Yes                 |
| [Rockset](02-destinations/rockset.md)                         | Alpha                | Yes                 |
| [S3](02-destinations/s3.md)                                   | Generally Available  | Yes                 |
| [Scylla](02-destinations/scylla.md)                           | Alpha                | Yes                 |
| [SFTP JSON](02-destinations/sftp-json.md)                     | Alpha                | Yes                 |
| [Snowflake](02-destinations/snowflake.md)                     | Generally Available  | Yes                 |
| [Streamr](02-destinations/streamr.md)                         | Alpha                | No                  |
