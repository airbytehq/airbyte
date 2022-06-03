const fs = require("fs");
const path = require("path")

const connectorsDocsRoot = "../docs/integrations";
const sourcesDocs = `${connectorsDocsRoot}/sources`;
const destinationDocs = `${connectorsDocsRoot}/destinations`;

function getFilenamesInDir(prefix, dir, excludes) {
    return fs.readdirSync(dir)
        .map(fileName => fileName.replace(".md", ""))
        .filter(fileName => excludes.indexOf(fileName.toLowerCase()) === -1)
        .map(filename => {
            return {type: 'doc', id: path.join(prefix, filename)}
        });
}

function getSourceConnectors() {
    return getFilenamesInDir("integrations/sources/", sourcesDocs, ["readme"]);
}

function getDestinationConnectors() {
    return getFilenamesInDir("integrations/destinations/", destinationDocs, ["readme"]);
}
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
      label: 'Documentation Help',
      items: [
        {
          type: 'doc',
          id: "docusaurus/contributing_to_docs",
        },
        {
          type: 'doc',
          id: "docusaurus/making_a_redirect",
        },
        {
          type: 'doc',
          id: "docusaurus/deploying_and_reverting_docs",
        },
        {
          type: 'doc',
          id: "docusaurus/locally_testing_docusaurus",
        },
        {
          type: 'doc',
          id: "docusaurus/readme",
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
            items: getSourceConnectors()
          },
          {
            type: 'category',
            label: 'Destinations',
            items: getDestinationConnectors()
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
          id: "contributing-to-airbyte/gradle-dependency-update",
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
