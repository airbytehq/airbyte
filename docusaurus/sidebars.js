module.exports = {
  mySidebar: [
    {
      type: 'doc',
      id: "readme",
    },
    {
      type: 'category',
      label: 'Airbyte Cloud QuickStart',
      items: [
          {
            type: 'doc',
            id: "cloud/getting-started-with-airbyte-cloud",
          },
          {
            type: 'doc',
            id: "cloud/core-concepts",
          },
          {
            type: 'doc',
            id: "cloud/managing-airbyte-cloud",
          },
      ]
    },
    {
      type: 'category',
      label: 'Airbyte Open Source QuickStart',
      items: [
        {
          type: 'doc',
          id: "quickstart/deploy-airbyte",
        },
        {
          type: 'doc',
          id: "quickstart/add-a-source",
        },
        {
          type: 'doc',
          id: "quickstart/add-a-destination",
        },
        {
          type: 'doc',
          id: "quickstart/set-up-a-connection",
        },
      ]
    },
    {
      type: 'category',
      label: 'Deploying Airbyte Open Source',
      items: [
        {
          type: 'doc',
          id: "deploying-airbyte/local-deployment",
        },
        {
          type: 'doc',
          id: "deploying-airbyte/on-aws-ec2",
        },
        {
          type: 'doc',
          id: "deploying-airbyte/on-aws-ecs",
        },
        {
          type: 'doc',
          id: "deploying-airbyte/on-azure-vm-cloud-shell",
        },
        {
          type: 'doc',
          id: "deploying-airbyte/on-gcp-compute-engine",
        },
        {
          type: 'doc',
          id: "deploying-airbyte/on-kubernetes",
        },
        {
          type: 'doc',
          id: "deploying-airbyte/on-plural",
        },
        {
          type: 'doc',
          id: "deploying-airbyte/on-oci-vm",
        },
        {
          type: 'doc',
          id: "deploying-airbyte/on-digitalocean-droplet",
        },
      ]
    },
    {
      type: 'category',
      label: 'Operator Guides',
      items: [
        {
          type: 'doc',
          id: "operator-guides/upgrading-airbyte",
        },
        {
          type: 'doc',
          id: "operator-guides/reset",
        },
        {
          type: 'doc',
          id: "operator-guides/configuring-airbyte-db",
        },
        {
          type: 'doc',
          id: "operator-guides/browsing-output-logs",
        },
        {
          type: 'doc',
          id: "operator-guides/using-the-airflow-airbyte-operator",
        },
        {
          type: 'doc',
          id: "operator-guides/using-prefect-task",
        },
        {
          type: 'doc',
          id: "operator-guides/using-dagster-integration",
        },
        {
          type: 'doc',
          id: "operator-guides/locating-files-local-destination",
        },
        {
          type: 'category',
          label: 'Transformations and Normalization',
          items: [
            {
              type: 'doc',
              id: "operator-guides/transformation-and-normalization/transformations-with-sql",
            },
            {
              type: 'doc',
              id: "operator-guides/transformation-and-normalization/transformations-with-dbt",
            },
            {
              type: 'doc',
              id: "operator-guides/transformation-and-normalization/transformations-with-airbyte",
            },
            ]
          },
        {
          type: 'category',
          label: 'Configuring Airbyte',
          items: [
            {
               type: 'doc',
              id: "operator-guides/configuring-airbyte",
            },
            {
              type: 'doc',
              id: "operator-guides/sentry-integration",
            },
            ]
        },
        {
          type: 'doc',
          id: "operator-guides/using-custom-connectors",
        },
        {
          type: 'doc',
          id: "operator-guides/scaling-airbyte",
        },
        {
          type: 'doc',
          id: "operator-guides/securing-airbyte",
        },
      ]
    },
    {
      type: 'category',
      label: 'Connector Catalog',
      items: [
        {
            type: 'doc',
            id: "integrations/README",
          },
          {
            type: 'category',
            label: 'Sources',
            items: [
              {
                type: 'doc',
                id: "integrations/sources/tplcentral",
              },
              {
                type: 'doc',
                id: "integrations/sources/airtable",
              },
              {
                type: 'doc',
                id: "integrations/sources/amazon-sqs",
              },
              {
                type: 'doc',
                id: "integrations/sources/amazon-seller-partner",
              },
              {
                type: 'doc',
                id: "integrations/sources/amazon-ads",
              },
              {
                type: 'doc',
                id: "integrations/sources/amplitude",
              },
              {
                type: 'doc',
                id: "integrations/sources/apify-dataset",
              },
              {
                type: 'doc',
                id: "integrations/sources/appstore",
              },
              {
                type: 'doc',
                id: "integrations/sources/asana",
              },
              {
                type: 'doc',
                id: "integrations/sources/aws-cloudtrail",
              },
              {
                type: 'doc',
                id: "integrations/sources/azure-table",
              },
              {
                type: 'doc',
                id: "integrations/sources/bamboo-hr",
              },
              {
                type: 'doc',
                id: "integrations/sources/bing-ads",
              },
              {
                type: 'doc',
                id: "integrations/sources/bigcommerce",
              },
              {
                type: 'doc',
                id: "integrations/sources/bigquery",
              },
              {
                type: 'doc',
                id: "integrations/sources/braintree",
              },
              {
                type: 'doc',
                id: "integrations/sources/cart",
              },
              {
                type: 'doc',
                id: "integrations/sources/chargebee",
              },
              {
                type: 'doc',
                id: "integrations/sources/chartmogul",
              },
              {
                type: 'doc',
                id: "integrations/sources/clickhouse",
              },
              {
                type: 'doc',
                id: "integrations/sources/close-com",
              },
              {
                type: 'doc',
                id: "integrations/sources/cockroachdb",
              },
              {
                type: 'doc',
                id: "integrations/sources/confluence",
              },
              {
                type: 'doc',
                id: "integrations/sources/customer-io",
              },
              {
                type: 'doc',
                id: "integrations/sources/delighted",
              },
              {
                type: 'doc',
                id: "integrations/sources/db2",
              },
              {
                type: 'doc',
                id: "integrations/sources/dixa",
              },
              {
                type: 'doc',
                id: "integrations/sources/drift",
              },
              {
                type: 'doc',
                id: "integrations/sources/drupal",
              },
              {
                type: 'doc',
                id: "integrations/sources/e2e-test",
              },
              {
                type: 'doc',
                id: "integrations/sources/exchangeratesapi",
              },
              {
                type: 'doc',
                id: "integrations/sources/facebook-marketing",
              },
              {
                type: 'doc',
                id: "integrations/sources/facebook-pages",
              },
              {
                type: 'doc',
                id: "integrations/sources/file",
              },
              {
                type: 'doc',
                id: "integrations/sources/flexport",
              },
              {
                type: 'doc',
                id: "integrations/sources/freshdesk",
              },
              {
                type: 'doc',
                id: "integrations/sources/freshsales",
              },
              {
                type: 'doc',
                id: "integrations/sources/freshservice",
              },
              {
                type: 'doc',
                id: "integrations/sources/github",
              },
              {
                type: 'doc',
                id: "integrations/sources/gitlab",
              },
              {
                type: 'doc',
                id: "integrations/sources/google-ads",
              },
              {
                type: 'doc',
                id: "integrations/sources/google-analytics-v4",
              },
              {
                type: 'doc',
                id: "integrations/sources/google-directory",
              },
              {
                type: 'doc',
                id: "integrations/sources/google-search-console",
              },
              {
                type: 'doc',
                id: "integrations/sources/google-sheets",
              },
              {
                type: 'doc',
                id: "integrations/sources/google-workspace-admin-reports",
              },
              {
                type: 'doc',
                id: "integrations/sources/greenhouse",
              },
              {
                type: 'doc',
                id: "integrations/sources/harvest",
              },
              {
                type: 'doc',
                id: "integrations/sources/harness",
              },
              {
                type: 'doc',
                id: "integrations/sources/http-request",
              },
              {
                type: 'doc',
                id: "integrations/sources/hubspot",
              },
              {
                type: 'doc',
                id: "integrations/sources/instagram",
              },
              {
                type: 'doc',
                id: "integrations/sources/intercom",
              },
              {
                type: 'doc',
                id: "integrations/sources/iterable",
              },
              {
                type: 'doc',
                id: "integrations/sources/jenkins",
              },
              {
                type: 'doc',
                id: "integrations/sources/jira",
              },
              {
                type: 'doc',
                id: "integrations/sources/kafka",
              },
              {
                type: 'doc',
                id: "integrations/sources/klaviyo",
              },
              {
                type: 'doc',
                id: "integrations/sources/kustomer",
              },
              {
                type: 'doc',
                id: "integrations/sources/lemlist",
              },
              {
                type: 'doc',
                id: "integrations/sources/linkedin-ads",
              },
              {
                type: 'doc',
                id: "integrations/sources/linnworks",
              },
              {
                type: 'doc',
                id: "integrations/sources/lever-hiring",
              },
              {
                type: 'doc',
                id: "integrations/sources/looker",
              },
              {
                type: 'doc',
                id: "integrations/sources/magento",
              },
              {
                type: 'doc',
                id: "integrations/sources/mailchimp",
              },
              {
                type: 'doc',
                id: "integrations/sources/marketo",
              },
              {
                type: 'doc',
                id: "integrations/sources/microsoft-dynamics-ax",
              },
              {
                type: 'doc',
                id: "integrations/sources/microsoft-dynamics-customer-engagement",
              },
              {
                type: 'doc',
                id: "integrations/sources/microsoft-dynamics-gp",
              },
              {
                type: 'doc',
                id: "integrations/sources/microsoft-dynamics-nav",
              },
              {
                type: 'doc',
                id: "integrations/sources/mssql",
              },
              {
                type: 'doc',
                id: "integrations/sources/microsoft-teams",
              },
              {
                type: 'doc',
                id: "integrations/sources/mixpanel",
              },
              {
                type: 'doc',
                id: "integrations/sources/monday",
              },
              {
                type: 'doc',
                id: "integrations/sources/mongodb-v2",
              },
              {
                type: 'doc',
                id: "integrations/sources/my-hours",
              },
              {
                type: 'doc',
                id: "integrations/sources/mysql",
              },
              {
                type: 'doc',
                id: "integrations/sources/notion",
              },
              {
                type: 'doc',
                id: "integrations/sources/okta",
              },
              {
                type: 'doc',
                id: "integrations/sources/onesignal",
              },
              {
                type: 'doc',
                id: "integrations/sources/openweather",
              },
              {
                type: 'doc',
                id: "integrations/sources/oracle",
              },
              {
                type: 'doc',
                id: "integrations/sources/oracle-peoplesoft",
              },
              {
                type: 'doc',
                id: "integrations/sources/oracle-siebel-crm",
              },
              {
                type: 'doc',
                id: "integrations/sources/orb",
              },
              {
                type: 'doc',
                id: "integrations/sources/outreach",
              },
              {
                type: 'doc',
                id: "integrations/sources/pagerduty",
              },
              {
                type: 'doc',
                id: "integrations/sources/paypal-transaction",
              },
              {
                type: 'doc',
                id: "integrations/sources/paystack",
              },
              {
                type: 'doc',
                id: "integrations/sources/persistiq",
              },
              {
                type: 'doc',
                id: "integrations/sources/plaid",
              },
              {
                type: 'doc',
                id: "integrations/sources/pinterest",
              },
              {
                type: 'doc',
                id: "integrations/sources/pipedrive",
              },
              {
                type: 'doc',
                id: "integrations/sources/pokeapi",
              },
              {
                type: 'doc',
                id: "integrations/sources/postgres",
              },
              {
                type: 'doc',
                id: "integrations/sources/posthog",
              },
              {
                type: 'doc',
                id: "integrations/sources/presta-shop",
              },
              {
                type: 'doc',
                id: "integrations/sources/qualaroo",
              },
              {
                type: 'doc',
                id: "integrations/sources/quickbooks",
              },
              {
                type: 'doc',
                id: "integrations/sources/recharge",
              },
              {
                type: 'doc',
                id: "integrations/sources/recurly",
              },
              {
                type: 'doc',
                id: "integrations/sources/redshift",
              },
              {
                type: 'doc',
                id: "integrations/sources/s3",
              },
              {
                type: 'doc',
                id: "integrations/sources/sap-business-one",
              },
              {
                type: 'doc',
                id: "integrations/sources/search-metrics",
              },
              {
                type: 'doc',
                id: "integrations/sources/salesforce",
              },
              {
                type: 'doc',
                id: "integrations/sources/salesloft",
              },
              {
                type: 'doc',
                id: "integrations/sources/sendgrid",
              },
              {
                type: 'doc',
                id: "integrations/sources/sentry",
              },
              {
                type: 'doc',
                id: "integrations/sources/shopify",
              },
              {
                type: 'doc',
                id: "integrations/sources/shortio",
              },
              {
                type: 'doc',
                id: "integrations/sources/slack",
              },
              {
                type: 'doc',
                id: "integrations/sources/smartsheets",
              },
              {
                type: 'doc',
                id: "integrations/sources/snapchat-marketing",
              },
              {
                type: 'doc',
                id: "integrations/sources/snowflake",
              },
              {
                type: 'doc',
                id: "integrations/sources/spree-commerce",
              },
              {
                type: 'doc',
                id: "integrations/sources/square",
              },
              {
                type: 'doc',
                id: "integrations/sources/strava",
              },
              {
                type: 'doc',
                id: "integrations/sources/stripe",
              },
              {
                type: 'doc',
                id: "integrations/sources/sugar-crm",
              },
              {
                type: 'doc',
                id: "integrations/sources/surveymonkey",
              },
              {
                type: 'doc',
                id: "integrations/sources/tempo",
              },
              {
                type: 'doc',
                id: "integrations/sources/tiktok-marketing",
              },
              {
                type: 'doc',
                id: "integrations/sources/trello",
              },
              {
                type: 'doc',
                id: "integrations/sources/twilio",
              },
              {
                type: 'doc',
                id: "integrations/sources/typeform",
              },
              {
                type: 'doc',
                id: "integrations/sources/us-census",
              },
              {
                type: 'doc',
                id: "integrations/sources/victorops",
              },
              {
                type: 'doc',
                id: "integrations/sources/woocommerce",
              },
              {
                type: 'doc',
                id: "integrations/sources/wordpress",
              },
              {
                type: 'doc',
                id: "integrations/sources/youtube-analytics",
              },
              {
                type: 'doc',
                id: "integrations/sources/zencart",
              },
              {
                type: 'doc',
                id: "integrations/sources/zendesk-chat",
              },
              {
                type: 'doc',
                id: "integrations/sources/zendesk-sunshine",
              },
              {
                type: 'doc',
                id: "integrations/sources/zendesk-support",
              },
              {
                type: 'doc',
                id: "integrations/sources/zendesk-talk",
              },
              {
                type: 'doc',
                id: "integrations/sources/zenloop",
              },
              {
                type: 'doc',
                id: "integrations/sources/zoho-crm",
              },
              {
                type: 'doc',
                id: "integrations/sources/zoom",
              },
              {
                type: 'doc',
                id: "integrations/sources/zuora",
              },
            ]
          },
          {
            type: 'category',
            label: 'Destinations',
            items: [
              {
                type: 'doc',
                id: "integrations/destinations/amazon-sqs",
              },
              {
                type: 'doc',
                id: "integrations/destinations/azureblobstorage",
              },
              {
                type: 'doc',
                id: "integrations/destinations/bigquery",
              },
              {
                type: 'doc',
                id: "integrations/destinations/clickhouse",
              },
              {
                type: 'doc',
                id: "integrations/destinations/databricks",
              },
              {
                type: 'doc',
                id: "integrations/destinations/dynamodb",
              },
              {
                type: 'doc',
                id: "integrations/destinations/elasticsearch",
              },
              {
                type: 'doc',
                id: "integrations/destinations/e2e-test",
              },
              {
                type: 'doc',
                id: "integrations/destinations/chargify",
              },
              {
                type: 'doc',
                id: "integrations/destinations/gcs",
              },
              {
                type: 'doc',
                id: "integrations/destinations/pubsub",
              },
              {
                type: 'doc',
                id: "integrations/destinations/kafka",
              },
              {
                type: 'doc',
                id: "integrations/destinations/keen",
              },
              {
                type: 'doc',
                id: "integrations/destinations/local-csv",
              },
              {
                type: 'doc',
                id: "integrations/destinations/local-json",
              },
              {
                type: 'doc',
                id: "integrations/destinations/mariadb-columnstore",
              },
              {
                type: 'doc',
                id: "integrations/destinations/meilisearch",
              },
              {
                type: 'doc',
                id: "integrations/destinations/mongodb",
              },
              {
                type: 'doc',
                id: "integrations/destinations/mqtt",
              },
              {
                type: 'doc',
                id: "integrations/destinations/mssql",
              },
              {
                type: 'doc',
                id: "integrations/destinations/mysql",
              },
              {
                type: 'doc',
                id: "integrations/destinations/oracle",
              },
              {
                type: 'doc',
                id: "integrations/destinations/postgres",
              },
              {
                type: 'doc',
                id: "integrations/destinations/pulsar",
              },
              {
                type: 'doc',
                id: "integrations/destinations/rabbitmq",
              },
              {
                type: 'doc',
                id: "integrations/destinations/redshift",
              },
              {
                type: 'doc',
                id: "integrations/destinations/rockset",
              },
              {
                type: 'doc',
                id: "integrations/destinations/s3",
              },
              {
                type: 'doc',
                id: "integrations/destinations/sftp-json",
              },
              {
                type: 'doc',
                id: "integrations/destinations/snowflake",
              },
              {
                type: 'doc',
                id: "integrations/destinations/cassandra",
              },
              {
                type: 'doc',
                id: "integrations/destinations/scylla",
              },
              {
                type: 'doc',
                id: "integrations/destinations/redis",
              },
              {
                type: 'doc',
                id: "integrations/destinations/kinesis",
              },
              {
                type: 'doc',
                id: "integrations/destinations/streamr",
              },
            ]
          },
          {
            type: 'doc',
            id: "integrations/custom-connectors",
          },
        ]

      },
    {
      type: 'category',
      label: 'Connector Development',
      items: [
        {
          type: 'doc',
          id: "connector-development/README",
        },
        {
          type: 'doc',
          id: "connector-development/tutorials/cdk-speedrun",
        },
        {
          type: 'category',
          label: 'Python CDK: Creating a HTTP API Source',
          items: [
            {
              type: 'doc',
              id: "connector-development/tutorials/cdk-tutorial-python-http/getting-started",
            },
            {
              type: 'doc',
              id: "connector-development/tutorials/cdk-tutorial-python-http/creating-the-source",
            },
            {
              type: 'doc',
              id: "connector-development/tutorials/cdk-tutorial-python-http/install-dependencies",
            },
            {
              type: 'doc',
              id: "connector-development/tutorials/cdk-tutorial-python-http/define-inputs",
            },
            {
              type: 'doc',
              id: "connector-development/tutorials/cdk-tutorial-python-http/connection-checking",
            },
            {
              type: 'doc',
              id: "connector-development/tutorials/cdk-tutorial-python-http/declare-schema",
            },
            {
              type: 'doc',
              id: "connector-development/tutorials/cdk-tutorial-python-http/read-data",
            },
            {
              type: 'doc',
              id: "connector-development/tutorials/cdk-tutorial-python-http/use-connector-in-airbyte",
            },
            {
              type: 'doc',
              id: "connector-development/tutorials/cdk-tutorial-python-http/test-your-connector",
            },
          ]
        },
        {
          type: 'doc',
          id: "connector-development/tutorials/building-a-python-source",
        },
        {
          type: 'doc',
          id: "connector-development/tutorials/building-a-python-destination",
        },
        {
          type: 'doc',
          id: "connector-development/tutorials/building-a-java-destination",
        },
        {
          type: 'doc',
          id: "connector-development/tutorials/profile-java-connector-memory",
        },
        {
          type: 'category',
          label: 'Connector Development Kit (Python)',
          items: [
            {
              type: 'doc',
              id: "connector-development/cdk-python/README",
            },
            {
              type: 'doc',
              id: "connector-development/cdk-python/basic-concepts",
            },
            {
              type: 'doc',
              id: "connector-development/cdk-python/schemas",
            },
            {
              type: 'doc',
              id: "connector-development/cdk-python/full-refresh-stream",
            },
            {
              type: 'doc',
              id: "connector-development/cdk-python/incremental-stream",
            },
            {
              type: 'doc',
              id: "connector-development/cdk-python/http-streams",
            },
            {
              type: 'doc',
              id: "connector-development/cdk-python/python-concepts",
            },
            {
              type: 'doc',
              id: "connector-development/cdk-python/stream-slices",
            },
          ]
        },
        {
          type: 'doc',
          id: "connector-development/cdk-faros-js",
        },
        {
          type: 'doc',
          id: "connector-development/airbyte101",
        },
        {
          type: 'doc',
          id: "connector-development/testing-connectors/README",
        },
        {
          type: 'doc',
          id: "connector-development/testing-connectors/source-acceptance-tests-reference",
        },
        {
          type: 'doc',
          id: "connector-development/connector-specification-reference",
        },
        {
          type: 'doc',
          id: "connector-development/best-practices",
        },
        {
          type: 'doc',
          id: "connector-development/ux-handbook",
        },
      ]
    },
    {
      type: 'category',
      label: 'Contributing to Airbyte',
      items: [
        {
          type: 'doc',
          id: "contributing-to-airbyte/README",
        },
        {
          type: 'doc',
          id: "contributing-to-airbyte/code-of-conduct",
        },
        {
          type: 'doc',
          id: "contributing-to-airbyte/developing-locally",
        },
        {
          type: 'doc',
          id: "contributing-to-airbyte/developing-on-docker",
        },
        {
          type: 'doc',
          id: "contributing-to-airbyte/developing-on-kubernetes",
        },
        {
          type: 'doc',
          id: "contributing-to-airbyte/monorepo-python-development",
        },
        {
          type: 'doc',
          id: "contributing-to-airbyte/code-style",
        },
        {
          type: 'doc',
          id: "contributing-to-airbyte/gradle-cheatsheet",
        },
        {
          type: 'doc',
          id: "contributing-to-airbyte/updating-documentation",
        },
        {
          type: 'doc',
          id: "contributing-to-airbyte/templates/README",
        },
        {
          type: 'doc',
          id: "contributing-to-airbyte/templates/integration-documentation-template",
        },
      ]
    },
    {
      type: 'category',
      label: 'Understanding Airbyte',
      items: [
        {
          type: 'doc',
          id: "understanding-airbyte/beginners-guide-to-catalog",
        },
        {
          type: 'doc',
          id: "understanding-airbyte/catalog",
        },
        {
          type: 'doc',
          id: "understanding-airbyte/airbyte-specification",
        },
        {
          type: 'doc',
          id: "understanding-airbyte/basic-normalization",
        },
        {
          type: 'category',
          label: 'Connections and Sync Modes',
          items: [
            {
              type: 'doc',
              id: "understanding-airbyte/connections/README",
            },
            {
              type: 'doc',
              id: "understanding-airbyte/connections/full-refresh-overwrite",
            },
            {
              type: 'doc',
              id: "understanding-airbyte/connections/full-refresh-append",
            },
            {
              type: 'doc',
              id: "understanding-airbyte/connections/incremental-append",
            },
            {
              type: 'doc',
              id: "understanding-airbyte/connections/incremental-deduped-history",
            },
          ]
        },
        {
          type: 'doc',
          id: "understanding-airbyte/operations",
        },
        {
          type: 'doc',
          id: "understanding-airbyte/high-level-view",
        },
        {
          type: 'doc',
          id: "understanding-airbyte/jobs",
        },
        {
          type: 'doc',
          id: "understanding-airbyte/tech-stack",
        },
        {
          type: 'doc',
          id: "understanding-airbyte/cdc",
        },
        {
          type: 'doc',
          id: "understanding-airbyte/namespaces",
        },
        {
          type: 'doc',
          id: "understanding-airbyte/supported-data-types",
        },
        {
          type: 'doc',
          id: "understanding-airbyte/json-avro-conversion",
        },
        {
          type: 'doc',
          id: "understanding-airbyte/glossary",
        },
      ]
    },
    {
      type: 'doc',
      id: "api-documentation",
    },
    {
      type: 'link',
      label: 'CLI documentation',
      href: 'https://github.com/airbytehq/airbyte/blob/master/octavia-cli/README.md',
    },
    {
      type: 'category',
      label: 'Project Overview',
      items: [
        {
          type: 'link',
          label: 'Roadmap',
          href: 'https://app.harvestr.io/roadmap/view/pQU6gdCyc/airbyte-roadmap',
        },
        {
          type: 'category',
          label: 'Changelog',
          items: [
            {
              type: 'doc',
              id: "project-overview/changelog/README",
            },
            {
              type: 'doc',
              id: "project-overview/changelog/platform",
            },
            {
              type: 'doc',
              id: "project-overview/changelog/connectors",
            },
          ]
        },
        {
          type: 'doc',
          id: "project-overview/slack-code-of-conduct",
        },
        {
          type: 'doc',
          id: "project-overview/security",
        },
        {
          type: 'category',
          label: 'Licenses',
          items: [
            {
              type: 'doc',
              id: "project-overview/licenses/README",
            },
            {
              type: 'doc',
              id: "project-overview/licenses/license-faq",
            },
            {
              type: 'doc',
              id: "project-overview/licenses/elv2-license",
            },
            {
              type: 'doc',
              id: "project-overview/licenses/mit-license",
            },
            {
              type: 'doc',
              id: "project-overview/licenses/examples",
            },
          ]
        },
        {
          type: 'doc',
          id: "project-overview/product-release-stages",
        },
      ]
    },
    {
      type: 'category',
      label: 'Troubleshooting & FAQ',
      items: [
       {
          type: 'doc',
          id: "troubleshooting/README",
        },
        {
          type: 'doc',
          id: "troubleshooting/on-deploying",
        },
        {
          type: 'doc',
          id: "troubleshooting/new-connection",
        },
        {
          type: 'doc',
          id: "troubleshooting/running-sync",
        },
        {
          type: 'doc',
          id: "troubleshooting/on-upgrading",
        },
      ]
    },
    {
      type: 'link',
      label: 'Airbyte Repository',
      href: 'https://github.com/airbytehq/airbyte',
    },
  ],
}
