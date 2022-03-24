# Connector Catalog

## Connector Release Stages

Airbyte uses a grading system for connectors to help users understand what to expect from a connector. There are three grades, explained below:

**Generally Available**: This connector has been proven to be robust via usage by a large number of users and extensive testing. Generally available connectors are ready for production use.

**Beta**: A beta connector is considered to be stable and reliable but has not been validated by a larger group of users and therefor users should be cautious using these connectors in production. Any issues with beta connectors will be prioritized and worked on when the connector is ready for the next release stage.

**Alpha**: This connector is either not sufficiently tested, has extremely limited functionality \(e.g: created as an example connector\), or for any other reason may not be very mature. We strongly discourage using alpha connectors for production use cases as we do not offer Cloud Support SLAs and issues will looked into when the connector is to be priortized for the next release stage.

**Note:** Some connectors on this list are currently not available on the Airbyte Cloud platform.

### Sources

| Connector | Stage |
| :--- | :--- |
| [3PL Central](sources/tplcentral.md) | Alpha |
| [Airtable](sources/airtable.md) | Alpha |
| [Amazon SQS](sources/amazon-sqs.md) | Alpha |
| [Amazon Seller Partner](sources/amazon-seller-partner.md) | Alpha |
| [Amplitude](sources/amplitude.md) | Alpha |
| [Apify Dataset](sources/apify-dataset.md) | Alpha |
| [Appstore](sources/appstore.md) | Alpha |
| [Asana](sources/asana.md) | Alpha |
| [AWS CloudTrail](sources/aws-cloudtrail.md) | Alpha |
| [Azure Table Storage](sources/azure-table.md) | Alpha |
| [BambooHR](sources/bamboo-hr.md) | Alpha |
| [Braintree](sources/braintree.md) | Alpha |
| [BigCommerce](sources/bigcommerce.md) | Alpha |
| [BigQuery](sources/bigquery.md) | Alpha |
| [Bing Ads](sources/bing-ads.md) | Alpha |
| [Cart.com](sources/cart.md) | Alpha |
| [Chargebee](sources/chargebee.md) | Alpha |
| [Chartmogul](sources/chartmogul.md) | Alpha |
| [ClickHouse](sources/clickhouse.md) | Alpha |
| [Close.com](sources/close-com.md) | Alpha |
| [CockroachDB](sources/cockroachdb.md) | Alpha |
| [Customer.io](sources/customer-io.md) | Alpha |
| [Db2](sources/db2.md) | Alpha |
| [Delighted](sources/delighted.md) | Alpha |
| [Dixa](sources/dixa.md) | Alpha |
| [Drift](sources/drift.md) | Alpha |
| [Drupal](sources/drupal.md) | Alpha |
| [End-to-End Testing](sources/e2e-test.md) | Alpha |
| [Exchange Rates API](sources/exchangeratesapi.md) | Alpha |
| [Facebook Marketing](sources/facebook-marketing.md) | Beta |
| [Facebook Pages](sources/facebook-pages.md) | Alpha |
| [Files](sources/file.md) | Alpha |
| [Flexport](sources/flexport.md) | Alpha |
| [Freshdesk](sources/freshdesk.md) | Alpha |
| [GitHub](sources/github.md) | Beta |
| [GitLab](sources/gitlab.md) | Alpha |
| [Google Ads](sources/google-ads.md) | Beta |
| [Google Adwords](sources/google-adwords.md) | Alpha |
| [Google Analytics v4](sources/google-analytics-v4.md) | Beta |
| [Google Directory](sources/google-directory.md) | Alpha |
| [Google Search Console](sources/google-search-console.md) | Alpha |
| [Google Sheets](sources/google-sheets.md) | Beta |
| [Google Workspace Admin Reports](sources/google-workspace-admin-reports.md) | Alpha |
| [Greenhouse](sources/greenhouse.md) | Alpha |
| [Harness](sources/harness.md) | Alpha |
| [HubSpot](sources/hubspot.md) | Beta |
| [Instagram](sources/instagram.md) | Alpha |
| [Intercom](sources/intercom.md) | Beta |
| [Iterable](sources/iterable.md) | Alpha |
| [Jenkins](sources/jenkins.md) | Alpha |
| [Jira](sources/jira.md) | Alpha |
| [Klaviyo](sources/klaviyo.md) | Alpha |
| [Kustomer](sources/kustomer.md) | Alpha |
| [Lemlist](sources/lemlist.md) | Alpha |
| [LinkedIn Ads](sources/linkedin-ads.md) | Alpha |
| [Linnworks](sources/linnworks.md) | Alpha |
| [Kustomer](sources/kustomer.md) | Alpha |
| [Lever Hiring](sources/lever-hiring.md) | Alpha |
| [Looker](sources/looker.md) | Alpha |
| [Magento](sources/magento.md) | Alpha |
| [Mailchimp](sources/mailchimp.md) | Alpha |
| [Marketo](sources/marketo.md) | Alpha |
| [Microsoft SQL Server \(MSSQL\)](sources/mssql.md) | Alpha |
| [Microsoft Dynamics AX](sources/microsoft-dynamics-ax.md) | Alpha |
| [Microsoft Dynamics Customer Engagement](sources/microsoft-dynamics-customer-engagement.md) | Alpha |
| [Microsoft Dynamics GP](sources/microsoft-dynamics-gp.md) | Alpha |
| [Microsoft Dynamics NAV](sources/microsoft-dynamics-nav.md) | Alpha |
| [Microsoft Teams](sources/microsoft-teams.md) | Alpha |
| [Mixpanel](sources/mixpanel.md) | Alpha |
| [Monday](sources/monday.md) | Alpha |
| [Mongo DB](sources/mongodb-v2.md) | Alpha |
| [My Hours](sources/my-hours.md) | Alpha |
| [MySQL](sources/mysql.md) | Alpha |
| [Notion](sources/notion.md) | Alpha |
| [Okta](sources/okta.md) | Alpha |
| [OneSignal](sources/onesignal.md) | Alpha |
| [OpenWeather](sources/openweather.md) | Alpha |
| [Oracle DB](sources/oracle.md) | Alpha |
| [Oracle PeopleSoft](sources/oracle-peoplesoft.md) | Alpha |
| [Oracle Siebel CRM](sources/oracle-siebel-crm.md) | Alpha |
| [Outreach](./sources/outreach.md)| Alpha |
| [PagerDuty](sources/pagerduty.md) | Alpha |
| [PayPal Transaction](sources/paypal-transaction.md) | Alpha |
| [Paystack](sources/paystack.md) | Alpha |
| [PersistIq](sources/persistiq.md) | Alpha |
| [Pinterest](sources/pinterest.md) | Alpha |
| [Pipedrive](sources/pipedrive.md) | Alpha |
| [Plaid](sources/plaid.md) | Alpha |
| [PokéAPI](sources/pokeapi.md) | Alpha |
| [Postgres](sources/postgres.md) | Alpha |
| [PostHog](sources/posthog.md) | Alpha |
| [PrestaShop](sources/presta-shop.md) | Alpha |
| [Qualaroo](sources/qualaroo.md) | Alpha |
| [QuickBooks](sources/quickbooks.md) | Alpha |
| [Recharge](sources/recharge.md) | Alpha |
| [Recurly](sources/recurly.md) | Alpha |
| [Redshift](sources/redshift.md) | Alpha |
| [Retently](sources/retently.md) | Alpha |
| [S3](sources/s3.md) | Beta |
| [Salesforce](sources/salesforce.md) | Certified |
| [Salesloft](./sources/salesloft.md)| Alpha |
| [SAP Business One](sources/sap-business-one.md) | Alpha |
| [SearchMetrics](./sources/search-metrics.md)| Alpha |
| [Sendgrid](sources/sendgrid.md) | Alpha |
| [Sentry](sources/sentry.md) | Alpha |
| [Shopify](sources/shopify.md) | Alpha |
| [Short.io](sources/shortio.md) | Alpha |
| [Slack](sources/slack.md) | Alpha |
| [Spree Commerce](sources/spree-commerce.md) | Alpha |
| [Smartsheets](sources/smartsheets.md) | Alpha |
| [Snowflake](sources/snowflake.md) | Alpha |
| [Square](sources/square.md) | Alpha |
| [Strava](sources/strava.md) | Alpha |
| [Stripe](sources/stripe.md) | Beta |
| [Sugar CRM](sources/sugar-crm.md) | Alpha |
| [SurveyMonkey](sources/surveymonkey.md) | Alpha |
| [Tempo](sources/tempo.md) | Alpha |
| [TikTok Marketing](./sources/tiktok-marketing.md)| Alpha |
| [Trello](sources/trello.md) | Alpha |
| [Twilio](sources/twilio.md) | Alpha |
| [Typeform](sources/typeform.md) | Alpha |
| [US Census](sources/us-census.md) | Alpha |
| [VictorOps](sources/victorops.md) | Alpha |
| [WooCommerce](sources/woocommerce.md) | Alpha |
| [Wordpress](sources/wordpress.md) | Alpha |
| [YouTube Analytics](sources/youtube-analytics.md) | Alpha |
| [Zencart](sources/zencart.md) | Alpha |
| [Zendesk Chat](sources/zendesk-chat.md) | Alpha |
| [Zendesk Sunshine](sources/zendesk-sunshine.md) | Alpha |
| [Zendesk Support](sources/zendesk-support.md) | Alpha |
| [Zendesk Talk](sources/zendesk-talk.md) | Alpha |
| [Zenloop](sources/zenloop.md)| Alpha |
| [Zoom](sources/zoom.md) | Alpha |
| [Zuora](sources/zuora.md) | Alpha |

### Destinations

| Connector | Stage |
| :--- | :--- |
| [Amazon SQS](destinations/amazon-sqs.md) | Alpha |
| [AzureBlobStorage](destinations/azureblobstorage.md) | Alpha |
| [BigQuery](destinations/bigquery.md) | Beta |
| [Cassandra](sources/cassandra.md) | Alpha |
| [Chargify \(Keen\)](destinations/chargify.md) | Alpha |
| [ClickHouse](destinations/clickhouse.md) | Alpha |
| [Databricks](destinations/databricks.md) | Alpha |
| [DynamoDB](sources/dynamodb.md) | Alpha |
| [Elasticsearch](destinations/elasticsearch.md) | Alpha |
| [End-to-End Testing](destinations/e2e-test.md) | Alpha |
| [Google Cloud Storage \(GCS\)](destinations/gcs.md) | Beta |
| [Google Firestore](destinations/firestore.md) | Alpha |
| [Google Pubsub](destinations/pubsub.md) | Alpha |
| [Kafka](destinations/kafka.md) | Alpha |
| [Keen](destinations/keen.md) | Alpha |
| [Local CSV](destinations/local-csv.md) | Alpha |
| [Local JSON](destinations/local-json.md) | Alpha |
| [MariaDB ColumnStore](destinations/mariadb-columnstore.md) | Alpha |
| [MeiliSearch](destinations/meilisearch.md) | Alpha |
| [MongoDB](destinations/mongodb.md) | Alpha |
| [MQTT](destinations/mqtt.md) | Alpha |
| [MS SQL Server](sources/mssql.md) | Alpha |
| [MySQL](destinations/mysql.md) | Alpha |
| [Oracle](destinations/oracle.md) | Alpha |
| [Postgres](destinations/postgres.md) | Alpha |
| [Pulsar](destinations/pulsar.md) | Alpha |
| [RabbitMQ](destinations/rabbitmq.md) | Alpha |
| [Redis](sources/redis.md) | Alpha |
| [Redshift](destinations/redshift.md) | Beta |
| [Rockset](destinations/rockset.md) | Alpha |
| [S3](destinations/s3.md) | Beta |
| [Scylla](sources/scylla.md) | Alpha |
| [SFTP JSON](./destinations/sftp-json.md)| Alpha |
| [SQL Server \(MSSQL\)](destinations/mssql.md) | Alpha |
| [Snowflake](destinations/snowflake.md) | Generally Available |
| [Cassandra](destinations/cassandra.md) | Alpha |
| [Scylla](destinations/scylla.md) | Alpha |
| [Redis](destinations/redis.md) | Alpha |
| [Kinesis](destinations/kinesis.md) | Alpha |
| [Streamr](destinations/streamr.md) | Alpha |
