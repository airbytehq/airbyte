# Connector Catalog

## Connector grades
Airbyte uses a grading system for connectors to help users understand what to expect from a connector. There are three grades, explained below:

**Certified**: This connector has been proven to be robust via usage by a large number of users and extensive testing.

**Beta**: While this connector is well tested and is expected to work a majority of the time, it was released recently. There may be some unhandled edge cases but Airbyte will provide very quick turnaround for support on any issues (we'll publish our target KPIs for support turnaround very soon). All beta connectors will make their way to certified status after enough field testing.

**Alpha**: This connector is either not sufficiently tested, has extremely limited functionality (e.g: created as an example connector), or for any other reason may not be very mature.

### Sources
| Connector | Grade |
|----|----|
|[Amazon Seller Partner](./sources/amazon-seller-partner.md)| Alpha |
|[Amplitude](./sources/amplitude.md)| Beta |
|[Apify Dataset](./sources/apify-dataset.md)| Alpha |
|[Appstore](./sources/appstore.md)| Alpha |
|[Asana](./sources/asana.md) | Beta |
|[AWS CloudTrail](./sources/aws-cloudtrail.md)| Beta |
|[BambooHR](./sources/bamboo-hr.md)| Alpha |
|[Braintree](./sources/braintree.md)| Alpha |
|[BigCommerce](./sources/bigcommerce.md)| Alpha |
|[BigQuery](./sources/bigquery.md)| Beta |
|[Bing Ads](./sources/bing-ads.md)| Beta |
|[Cart](./sources/cart.md)| Beta |
|[Chargebee](./sources/chargebee.md)| Alpha |
|[ClickHouse](./sources/clickhouse.md)| Beta |
|[Close.com](./sources/close-com.md)| Beta |
|[CockroachDB](./sources/cockroachdb.md)| Beta |
|[Db2](./sources/db2.md)| Beta |
|[Dixa](./sources/dixa.md) | Alpha |
|[Drift](./sources/drift.md)| Beta |
|[Drupal](./sources/drupal.md)| Beta |
|[Exchange Rates API](./sources/exchangeratesapi.md)| Certified |
|[Facebook Marketing](./sources/facebook-marketing.md)| Beta |
|[Facebook Pages](./sources/facebook-pages.md)| Alpha |
|[Files](./sources/file.md)| Certified |
|[Freshdesk](./sources/freshdesk.md)| Certified |
|[GitHub](./sources/github.md)| Beta |
|[GitLab](./sources/gitlab.md)| Beta |
|[Google Ads](./sources/google-ads.md)| Beta |
|[Google Adwords](./sources/google-adwords.md)| Beta |
|[Google Analytics](./sources/googleanalytics.md)| Beta |
|[Google Analytics v4](./sources/google-analytics-v4.md)| Beta |
|[Google Directory](./sources/google-directory.md)| Certified |
|[Google Search Console](./sources/google-search-console.md)| Beta |
|[Google Sheets](./sources/google-sheets.md)| Certified |
|[Google Workspace Admin Reports](./sources/google-workspace-admin-reports.md)| Certified |
|[Greenhouse](./sources/greenhouse.md)| Beta |
|[Hubspot](./sources/hubspot.md)| Certified |
|[Instagram](./sources/instagram.md)| Certified |
|[Intercom](./sources/intercom.md)| Beta |
|[Iterable](./sources/iterable.md)| Beta |
|[Jira](./sources/jira.md)| Certified |
|[Klaviyo](./sources/klaviyo.md)| Beta |
|[Klaviyo](./sources/kustomer.md)| Alpha |
|[Looker](./sources/looker.md)| Beta |
|[Magento](./sources/magento.md)| Beta |
|[Mailchimp](./sources/mailchimp.md)| Certified |
|[Marketo](./sources/marketo.md)| Certified |
|[Microsoft SQL Server \(MSSQL\)](./sources/mssql.md)| Certified |
|[Microsoft Dynamics AX](./sources/microsoft-dynamics-ax.md)| Beta |
|[Microsoft Dynamics Customer Engagement](./sources/microsoft-dynamics-customer-engagement.md)| Beta |
|[Microsoft Dynamics GP](./sources/microsoft-dynamics-gp.md)| Beta |
|[Microsoft Dynamics NAV](./sources/microsoft-dynamics-nav.md)| Beta |
|[Microsoft Teams](./sources/microsoft-teams.md)| Certified |
|[Mixpanel](./sources/mixpanel.md)| Beta |
|[Mongo DB](./sources/mongodb-v2.md)| Beta |
|[MySQL](./sources/mysql.md)| Certified |
|[Okta](./sources/okta.md)| Beta |
|[Oracle DB](./sources/oracle.md)| Certified |
|[Oracle PeopleSoft](./sources/oracle-peoplesoft.md)| Beta |
|[Oracle Siebel CRM](./sources/oracle-siebel-crm.md)| Beta |
|[PayPal Transaction](./sources/paypal-transaction.md)| Beta |
|[Pipedrive](./sources/pipedrive.md)| Alpha |
|[Plaid](./sources/plaid.md)| Alpha |
|[PokéAPI](./sources/pokeapi.md)| Beta |
|[Postgres](./sources/postgres.md)| Certified |
|[PostHog](./sources/posthog.md)| Beta |
|[PrestaShop](./sources/presta-shop.md)| Beta |
|[Quickbooks](./sources/quickbooks.md)| Beta |
|[Recharge](./sources/recharge.md)| Beta |
|[Recurly](./sources/recurly.md)| Beta |
|[Redshift](./sources/redshift.md)| Certified |
|[S3](./sources/s3.md)| Alpha |
|[Salesforce](./sources/salesforce.md)| Certified |
|[SAP Business One](./sources/sap-business-one.md)| Beta |
|[Sendgrid](./sources/sendgrid.md)| Certified |
|[Shopify](./sources/shopify.md)| Certified |
|[Short.io](./sources/shortio.md)| Beta |
|[Slack](./sources/slack.md)| Beta |
|[Spree Commerce](./sources/spree-commerce.md)| Beta |
|[Smartsheets](./sources/smartsheets.md)| Beta |
|[Snowflake](./sources/snowflake.md)| Beta |
|[Square](./sources/square.md)| Beta |
|[Stripe](./sources/stripe.md)| Certified |
|[Sugar CRM](./sources/sugar-crm.md)| Beta |
|[SurveyMonkey](./sources/surveymonkey.md)| Beta |
|[Tempo](./sources/tempo.md)| Beta |
|[Trello](./sources/trello.md)| Beta |
|[Twilio](./sources/twilio.md)| Beta |
|[US Census](./sources/us-census.md)| Alpha |
|[WooCommerce](./sources/woo-commerce.md)| Beta |
|[Wordpress](./sources/wordpress.md)| Beta |
|[Zencart](./sources/zencart.md)| Beta |
|[Zendesk Chat](./sources/zendesk-chat.md)| Certified |
|[Zendesk Sunshine](./sources/zendesk-sunshine.md)| Beta |
|[Zendesk Support](./sources/zendesk-support.md)| Certified |
|[Zendesk Talk](./sources/zendesk-talk.md)| Certified |
|[Zoom](./sources/zoom.md)| Beta |
|[Zuora](./sources/zuora.md)| Beta |

### Destinations
| Connector | Grade |
|----|----|
|[AzureBlobStorage](./destinations/azureblobstorage.md)| Alpha |
|[BigQuery](./destinations/bigquery.md)| Certified |
|[Chargify (Keen)](./destinations/keen.md)| Alpha |
|[Databricks](./destinations/databricks.md) | Beta |
|[Google Cloud Storage (GCS)](./destinations/gcs.md)| Alpha |
|[Google Pubsub](./destinations/pubsub.md)| Alpha |
|[Kafka](./destinations/kafka.md)| Alpha |
|[Keen](./destinations/keen.md)| Alpha |
|[Local CSV](./destinations/local-csv.md)| Certified |
|[Local JSON](./destinations/local-json.md)| Certified |
|[MeiliSearch](./destinations/meilisearch.md)| Beta |
|[MongoDB](./destinations/mongodb.md)| Alpha |
|[MySQL](./destinations/mysql.md)| Beta |
|[Oracle](./destinations/oracle.md)| Alpha |
|[Postgres](./destinations/postgres.md)| Certified |
|[Redshift](./destinations/redshift.md)| Certified |
|[S3](./destinations/s3.md)| Certified |
|[SQL Server (MSSQL)](./destinations/mssql.md)| Alpha |
|[Snowflake](./destinations/snowflake.md)| Certified |
