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
      label: 'Start here',
      id: "readme",
    },
    {
      type: 'category',
      label: 'Connector Catalog',
      link: {
        type: 'doc',
        id: 'integrations/README',
      },
      items: [
          {
            type: 'category',
            label: 'Sources',
            link: {
              type: 'generated-index',
            },
            items: getSourceConnectors()
          },
          {
            type: 'category',
            label: 'Destinations',
            link: {
              type: 'generated-index',
            },
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
      label: 'Airbyte Cloud',
      link: {
        type: 'doc',
        id: 'cloud/getting-started-with-airbyte-cloud',
      },
      items: [
        'cloud/core-concepts',
        'cloud/managing-airbyte-cloud',

      ],
    },
    {
      type: 'category',
      label: 'Airbyte Open Source QuickStart',
      link: {
        type: 'generated-index',
      },
      items: [
        'quickstart/deploy-airbyte',
        'quickstart/add-a-source',
        'quickstart/add-a-destination',
        'quickstart/set-up-a-connection',
      ],
    },
    {
      type: 'category',
      label: 'Deploy Airbyte Open Source',
      link: {
        type: 'generated-index',
      },
      items: [
        'deploying-airbyte/local-deployment',
        'deploying-airbyte/on-aws-ec2',
        'deploying-airbyte/on-azure-vm-cloud-shell',
        'deploying-airbyte/on-gcp-compute-engine',
        'deploying-airbyte/on-kubernetes',
        'deploying-airbyte/on-plural',
        'deploying-airbyte/on-oci-vm',
        'deploying-airbyte/on-digitalocean-droplet',
      ],
    },
    {
      type: 'category',
      label: 'Manage Airbyte Open Source',
      link: {
        type: 'generated-index',
      },
      items: [
        'operator-guides/upgrading-airbyte',
        'operator-guides/reset',
        'operator-guides/configuring-airbyte-db',
        'operator-guides/browsing-output-logs',
        'operator-guides/using-the-airflow-airbyte-operator',
        'operator-guides/using-prefect-task',
        'operator-guides/using-dagster-integration',
        'operator-guides/locating-files-local-destination',
        {
          type: 'category',
          label: 'Transformations and Normalization',
          items: [
            'operator-guides/transformation-and-normalization/transformations-with-sql',
            'operator-guides/transformation-and-normalization/transformations-with-dbt',
            'operator-guides/transformation-and-normalization/transformations-with-airbyte',
            ]
          },
          {
            type: 'category',
            label: 'Configuring Airbyte',
            link: {
              type: 'doc',
              id: 'operator-guides/configuring-airbyte',
            },
            items: [
                'operator-guides/sentry-integration',
              ]
          },
        'operator-guides/using-custom-connectors',
        'operator-guides/scaling-airbyte',
        'operator-guides/securing-airbyte',
      ],
    },
    {
      type: 'category',
      label: 'Troubleshoot Airbyte',
      link: {
        type: 'doc',
        id: 'troubleshooting/README',
      },
      items: [
        'troubleshooting/on-deploying',
        'troubleshooting/new-connection',
        'troubleshooting/running-sync',     
      ],
    },
    {
      type: 'category',
      label: 'Build a connector',
      link: {
        type: 'doc',
        id: 'connector-development/README',
      },      
      items: [
        'connector-development/tutorials/cdk-speedrun',
        {
          type: 'category',
          label: 'Python CDK: Creating a HTTP API Source',
          items: [
            'connector-development/tutorials/cdk-tutorial-python-http/getting-started',
            'connector-development/tutorials/cdk-tutorial-python-http/creating-the-source',
            'connector-development/tutorials/cdk-tutorial-python-http/install-dependencies',
            'connector-development/tutorials/cdk-tutorial-python-http/define-inputs',
            'connector-development/tutorials/cdk-tutorial-python-http/connection-checking',
            'connector-development/tutorials/cdk-tutorial-python-http/declare-schema',
            'connector-development/tutorials/cdk-tutorial-python-http/read-data',
            'connector-development/tutorials/cdk-tutorial-python-http/use-connector-in-airbyte',
            'connector-development/tutorials/cdk-tutorial-python-http/test-your-connector',
          ]
        },
        'connector-development/tutorials/building-a-python-source',
        'connector-development/tutorials/building-a-python-destination',
        'connector-development/tutorials/building-a-java-destination',
        'connector-development/tutorials/profile-java-connector-memory',
        {
          type: 'category',
          label: 'Connector Development Kit (Python)',
          link: {
            type: 'doc',
            id: 'connector-development/cdk-python/README',
          },
          items: [
            'connector-development/cdk-python/basic-concepts',
            'connector-development/cdk-python/schemas',
            'connector-development/cdk-python/full-refresh-stream',
            'connector-development/cdk-python/incremental-stream',
            'connector-development/cdk-python/http-streams',
            'connector-development/cdk-python/python-concepts',
            'connector-development/cdk-python/stream-slices',
          ]
        },
        'connector-development/cdk-faros-js',
        'connector-development/airbyte101',
        'connector-development/testing-connectors/README',
        'connector-development/testing-connectors/source-acceptance-tests-reference',
        'connector-development/connector-specification-reference',
        'connector-development/best-practices',
        'connector-development/ux-handbook',
      ]
    },
    {
      type: 'category',
      label: 'Contribute to Airbyte',
      link: {
        type: 'doc',
        id: 'contributing-to-airbyte/README',
      },
      items: [
        'contributing-to-airbyte/code-of-conduct',
        'contributing-to-airbyte/maintainer-code-of-conduct',
        'contributing-to-airbyte/developing-locally',
        'contributing-to-airbyte/developing-on-docker',
        'contributing-to-airbyte/developing-on-kubernetes',
        'contributing-to-airbyte/monorepo-python-development',
        'contributing-to-airbyte/code-style',
        'contributing-to-airbyte/issues-and-pull-requests',
        'contributing-to-airbyte/gradle-cheatsheet',
        'contributing-to-airbyte/gradle-dependency-update',
        {
          type: 'category',
          label: 'Updating documentation',
          link: {
            type: 'doc',
            id: 'contributing-to-airbyte/updating-documentation',
          },
          items: [
            {
              type: 'link',
              label: 'Connector doc template',
              href: 'https://hackmd.io/Bz75cgATSbm7DjrAqgl4rw',
            },
          ]
        },
      ]
    },
    {
      type: 'category',
      label: 'Understand Airbyte',
      items: [
        'understanding-airbyte/beginners-guide-to-catalog',
        'understanding-airbyte/airbyte-protocol',
        'understanding-airbyte/airbyte-protocol-docker',
        'understanding-airbyte/basic-normalization',
        {
          type: 'category',
          label: 'Connections and Sync Modes',
          link: {
            type: 'doc',
            id: 'understanding-airbyte/connections/README',
          },
          items: [
            'understanding-airbyte/connections/full-refresh-overwrite',
            'understanding-airbyte/connections/full-refresh-append',
            'understanding-airbyte/connections/incremental-append',
            'understanding-airbyte/connections/incremental-deduped-history',
          ]
        },
        'understanding-airbyte/operations',
        'understanding-airbyte/high-level-view',
        'understanding-airbyte/jobs',
        'understanding-airbyte/tech-stack',
        'understanding-airbyte/cdc',
        'understanding-airbyte/namespaces',
        'understanding-airbyte/supported-data-types',
        'understanding-airbyte/json-avro-conversion',
        'understanding-airbyte/glossary',
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
        'project-overview/product-release-stages',
        'project-overview/slack-code-of-conduct',
        'project-overview/security',
        {
          type: 'link',
          label: 'Airbyte Repository',
          href: 'https://github.com/airbytehq/airbyte',
        },
        {
          type: 'category',
          label: 'Licenses',
          link: {
            type: 'doc',
            id: 'project-overview/licenses/README',
          },
          items: [
            'project-overview/licenses/license-faq',
            'project-overview/licenses/elv2-license',
            'project-overview/licenses/mit-license',
            'project-overview/licenses/examples',
          ]
        },
      ],
    },
  ],
}
